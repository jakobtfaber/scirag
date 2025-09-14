#!/usr/bin/env python3
import os
import re
import sys
import csv
import requests
import subprocess
import xml.etree.ElementTree as ET

# CONFIG
# Resolve paths relative to the location of this script so the script can be
# executed from any working directory.
BASE_DIR      = '/Users/jakobfaber/Documents/research/caltech/my_papers/nihari/cited_works' #os.path.dirname(os.path.abspath(__file__))

# Local data files that live next to this script
BIBFILE       = os.path.join(BASE_DIR, 'refs.txt')
CSV_ALLOWED   = os.path.join(BASE_DIR, 'allowed_refs.csv')
# Folder where the PDFs will be saved. Keep the original absolute path so
# behaviour remains unchanged.
OUTPUT_FOLDER = os.path.expanduser('/Users/jakobfaber/Documents/research/caltech/my_papers/nihari/cited_works')
ARXIV_API     = 'http://export.arxiv.org/api/query'

def load_allowed_keys(csv_path):
    allowed = set()
    try:
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get('CitationKey') or row.get('citationkey')
                print(key)
                if key:
                    allowed.add(key.strip())
    except FileNotFoundError:
        sys.exit(f"ERROR: CSV file '{csv_path}' not found.")
    if not allowed:
        sys.exit(f"ERROR: No keys found in '{csv_path}'.")
    return allowed

def clean_text(s):
    s = re.sub(r'[{}"\'“”‘’]', '', s)
    s = re.sub(r'[/\-:;,&]', ' ', s)
    s = re.sub(r'[^A-Za-z0-9\s]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def slugify(title):
    return clean_text(title).replace(' ', '_').lower()

def extract_braced(entry, field):
    pat = re.compile(rf'{field}\s*=\s*{{', re.IGNORECASE)
    m = pat.search(entry)
    if not m:
        return None
    idx, depth = m.end(), 1
    start = idx
    while idx < len(entry) and depth > 0:
        if entry[idx] == '{':
            depth += 1
        elif entry[idx] == '}':
            depth -= 1
        idx += 1
    return entry[start:idx-1].strip()

def extract_quoted(entry, field):
    m = re.search(rf'{field}\s*=\s*"([^"]*)"', entry, re.IGNORECASE)
    return m.group(1).strip() if m else None

def extract_field(entry, field):
    return extract_braced(entry, field) or extract_quoted(entry, field)

def parse_bib_entries(text):
    entries, buf, depth, in_entry = [], [], 0, False
    for line in text.splitlines():
        if not in_entry and line.strip().startswith('@'):
            in_entry = True
            depth = line.count('{') - line.count('}')
            buf = [line]
        elif in_entry:
            depth += line.count('{') - line.count('}')
            buf.append(line)
            if depth <= 0:
                entries.append('\n'.join(buf))
                in_entry = False
    return entries

def query_arxiv(raw_title):
    title = clean_text(raw_title)
    if not title:
        return None, None
    params = {
        'search_query': f'ti:"{title}"',
        'start':        0,
        'max_results':  1
    }
    r = requests.get(ARXIV_API, params=params, timeout=10)
    if not r.ok:
        return None, None
    root = ET.fromstring(r.text)
    ns   = {'atom': 'http://www.w3.org/2005/Atom'}
    e    = root.find('atom:entry', ns)
    if e is None:
        return None, None
    aid = e.find('atom:id', ns).text.rsplit('/', 1)[-1]
    yr  = e.find('atom:published', ns).text[:4]
    return aid, yr

def main():
    allowed_keys = load_allowed_keys(CSV_ALLOWED)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    try:
        with open(BIBFILE) as f:
            bib_text = f.read()
    except FileNotFoundError:
        sys.exit(f"ERROR: BibTeX file '{BIBFILE}' not found.")

    entries = parse_bib_entries(bib_text)
    for entry in entries:
        m = re.match(r'@\w+\s*{\s*([^,]+),', entry)
        key = m.group(1).strip() if m else None
        if key not in allowed_keys:
            continue

        # Extract first non-collaboration author
        author_raw = extract_field(entry, 'author') or ''
        authors    = [a.strip('{} ').strip() for a in author_raw.split(' and ')]
        if authors and 'collaboration' in authors[0].lower() and len(authors) > 1:
            first_author = authors[1]
        else:
            first_author = authors[0] if authors else 'Unknown'
        first_author = first_author.strip('{} ').strip()
        last = first_author.split(',')[0] if ',' in first_author else first_author.split()[-1]

        year  = extract_field(entry, 'year') or '0000'
        title = extract_field(entry, 'title') or ''

        # Get arXiv ID
        arxiv = extract_field(entry, 'eprint')
        if not arxiv and title:
            arxiv, yr2 = query_arxiv(title)
            if arxiv and yr2:
                year = yr2

        if not arxiv:
            print(f"WARNING: {key} has no arXiv ID, skipping", file=sys.stderr)
            continue

        slug  = slugify(title)
        fname = f"{last}_{year}_{arxiv}_{slug}.pdf"
        outp  = os.path.join(OUTPUT_FOLDER, fname)
        url   = f"https://arxiv.org/pdf/{arxiv}.pdf"

        print(f"Downloading {key} ➔ {fname}")
        try:
            subprocess.run(['wget', '-L', '-O', outp, url], check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR downloading {key}: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
    
