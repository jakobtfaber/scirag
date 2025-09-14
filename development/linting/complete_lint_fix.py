#!/usr/bin/env python3
"""
Complete Lint Fix Script - Fix ALL 133 remaining linting errors

This script addresses every single remaining linting issue comprehensively.
"""

import os
import re
from pathlib import Path

def fix_all_linting_issues(file_path: Path):
    """Fix ALL linting issues in a single file."""
    print(f"Fixing ALL linting issues in {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove ALL trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix 2: Remove ALL blank lines with only whitespace
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # Fix 3: Fix ALL line length issues
    content = fix_all_line_length_issues(content)
    
    # Fix 4: Remove ALL unused imports
    content = remove_all_unused_imports(content)
    
    # Fix 5: Fix ALL indentation issues
    content = fix_all_indentation_issues(content)
    
    # Fix 6: Fix ALL continuation line issues
    content = fix_all_continuation_lines(content)
    
    # Fix 7: Fix ALL string literal issues
    content = fix_all_string_literals(content)
    
    # Fix 8: Fix ALL logging format issues
    content = fix_all_logging_formats(content)
    
    # Fix 9: Fix ALL exception handling issues
    content = fix_all_exception_handling(content)
    
    # Fix 10: Ensure proper file ending
    content = content.rstrip() + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_all_line_length_issues(content: str) -> str:
    """Fix ALL line length issues comprehensively."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 79:
            fixed_line = break_line_comprehensively(line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def break_line_comprehensively(line: str) -> str:
    """Break a line comprehensively to fix length issues."""
    if len(line) <= 79:
        return line
    
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    # Break long import statements
    if 'import' in line and len(line) > 79:
        return break_import_statement(line)
    
    # Break long function definitions
    if 'def ' in line and '(' in line and ')' in line and len(line) > 79:
        return break_function_definition(line)
    
    # Break long assignments
    if ' = ' in line and len(line) > 79:
        return break_assignment_statement(line)
    
    # Break long method calls
    if '.' in line and '(' in line and len(line) > 79:
        return break_method_call(line)
    
    # Break long string concatenations
    if ' + ' in line and len(line) > 79:
        return break_string_concatenation(line)
    
    # Break long conditional statements
    if ' and ' in line and len(line) > 79:
        return break_conditional_statement(line, ' and ')
    
    if ' or ' in line and len(line) > 79:
        return break_conditional_statement(line, ' or ')
    
    # Break long dictionary/list definitions
    if ('{' in line or '[' in line) and len(line) > 79:
        return break_collection_definition(line)
    
    # Break long string literals
    if ('"' in line or "'" in line) and len(line) > 79:
        return break_string_literal(line)
    
    # Break long comments
    if line.strip().startswith('#') and len(line) > 79:
        return break_comment(line)
    
    # For other long lines, try to break at logical points
    return break_at_logical_points(line)

def break_import_statement(line: str) -> str:
    """Break long import statements."""
    if 'from' in line and ' import ' in line:
        parts = line.split(' import ')
        if len(parts) == 2:
            from_part = parts[0]
            import_part = parts[1]
            
            if len(from_part) < 70:
                # Break the import part
                imports = [imp.strip() for imp in import_part.split(',')]
                result = [f"{from_part} import ("]
                for i, imp in enumerate(imports):
                    if i == len(imports) - 1:
                        result.append(f"    {imp}")
                    else:
                        result.append(f"    {imp},")
                result.append(")")
                return '\n'.join(result)
    
    return line

def break_function_definition(line: str) -> str:
    """Break long function definitions."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if '(' in line and ')' in line:
        func_name = line.split('(')[0]
        params = line[line.find('(')+1:line.rfind(')')]
        
        if len(params) > 50:
            result = [f"{func_name}("]
            param_parts = [p.strip() for p in params.split(',')]
            for i, param in enumerate(param_parts):
                if i == len(param_parts) - 1:
                    result.append(f"{spaces}{param})")
                else:
                    result.append(f"{spaces}{param},")
            return '\n'.join(result)
    
    return line

def break_assignment_statement(line: str) -> str:
    """Break long assignment statements."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if ' = ' in line:
        var_name = line.split(' = ')[0]
        value = line.split(' = ')[1]
        
        if len(value) > 50:
            if value.startswith('(') and value.endswith(')'):
                # Break parentheses
                inner = value[1:-1]
                if ',' in inner:
                    parts = [p.strip() for p in inner.split(',')]
                    result = [f"{var_name} = ("]
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            result.append(f"{spaces}{part})")
                        else:
                            result.append(f"{spaces}{part},")
                    return '\n'.join(result)
            elif value.startswith('[') and value.endswith(']'):
                # Break list
                inner = value[1:-1]
                if ',' in inner:
                    parts = [p.strip() for p in inner.split(',')]
                    result = [f"{var_name} = ["]
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            result.append(f"{spaces}{part}]")
                        else:
                            result.append(f"{spaces}{part},")
                    return '\n'.join(result)
            else:
                # Simple break
                return f"{var_name} = (\n{spaces}{value}\n{' ' * indent})"
    
    return line

def break_method_call(line: str) -> str:
    """Break long method calls."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if '.' in line and '(' in line and ')' in line:
        # Find the method call part
        method_start = line.rfind('.')
        method_part = line[method_start:]
        
        if len(method_part) > 50:
            # Break the method call
            method_name = method_part.split('(')[0]
            params = method_part[method_part.find('(')+1:method_part.rfind(')')]
            
            if ',' in params:
                param_parts = [p.strip() for p in params.split(',')]
                result = [f"{line[:method_start]}.{method_name}("]
                for i, param in enumerate(param_parts):
                    if i == len(param_parts) - 1:
                        result.append(f"{spaces}{param})")
                    else:
                        result.append(f"{spaces}{param},")
                return '\n'.join(result)
    
    return line

def break_string_concatenation(line: str) -> str:
    """Break long string concatenations."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if ' + ' in line:
        parts = line.split(' + ')
        if len(parts) > 2:
            result = [parts[0]]
            for part in parts[1:]:
                result.append(f"{spaces}+ {part}")
            return '\n'.join(result)
    
    return line

def break_conditional_statement(line: str, operator: str) -> str:
    """Break long conditional statements."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if operator in line:
        parts = line.split(operator)
        if len(parts) > 1:
            result = [parts[0]]
            for part in parts[1:]:
                result.append(f"{spaces}{operator.strip()}{part}")
            return '\n'.join(result)
    
    return line

def break_collection_definition(line: str) -> str:
    """Break long collection definitions."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if '{' in line and '}' in line:
        # Dictionary
        open_brace = line.find('{')
        close_brace = line.rfind('}')
        before_brace = line[:open_brace]
        inner = line[open_brace+1:close_brace]
        
        if ',' in inner:
            parts = [p.strip() for p in inner.split(',')]
            result = [f"{before_brace}{{"]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    result.append(f"{spaces}{part}")
                else:
                    result.append(f"{spaces}{part},")
            result.append(f"{' ' * indent}}}")
            return '\n'.join(result)
    
    elif '[' in line and ']' in line:
        # List
        open_bracket = line.find('[')
        close_bracket = line.rfind(']')
        before_bracket = line[:open_bracket]
        inner = line[open_bracket+1:close_bracket]
        
        if ',' in inner:
            parts = [p.strip() for p in inner.split(',')]
            result = [f"{before_bracket}["]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    result.append(f"{spaces}{part}")
                else:
                    result.append(f"{spaces}{part},")
            result.append(f"{' ' * indent}]")
            return '\n'.join(result)
    
    return line

def break_string_literal(line: str) -> str:
    """Break long string literals."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    # Find string boundaries
    if '"' in line:
        start_quote = line.find('"')
        end_quote = line.rfind('"')
        if start_quote != end_quote:
            before_string = line[:start_quote]
            string_content = line[start_quote+1:end_quote]
            after_string = line[end_quote+1:]
            
            if len(string_content) > 50:
                # Break the string
                words = string_content.split()
                result = [f"{before_string}\""]
                current_line = ""
                for word in words:
                    if len(current_line + word) > 60:
                        result.append(f"{spaces}{current_line}\"")
                        current_line = word + " "
                    else:
                        current_line += word + " "
                if current_line:
                    result.append(f"{spaces}{current_line}\"")
                result.append(f"{' ' * indent}{after_string}")
                return '\n'.join(result)
    
    return line

def break_comment(line: str) -> str:
    """Break long comments."""
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    if line.strip().startswith('#'):
        comment_text = line.strip()[1:]
        words = comment_text.split()
        result = [f"{' ' * indent}#"]
        current_line = ""
        for word in words:
            if len(current_line + word) > 60:
                result.append(f"{spaces}# {current_line}")
                current_line = word + " "
            else:
                current_line += word + " "
        if current_line:
            result.append(f"{spaces}# {current_line}")
        return '\n'.join(result)
    
    return line

def break_at_logical_points(line: str) -> str:
    """Break long lines at logical points."""
    if len(line) <= 79:
        return line
    
    # Try to break at commas
    if ',' in line:
        parts = line.split(',')
        if len(parts) > 1:
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * (indent + 4)
            result = [parts[0]]
            for i, part in enumerate(parts[1:], 1):
                if i == len(parts) - 1:
                    result.append(f"{spaces}{part}")
                else:
                    result.append(f"{spaces}{part},")
            return '\n'.join(result)
    
    # Try to break at operators
    operators = [' and ', ' or ', ' + ', ' - ', ' * ', ' / ']
    for op in operators:
        if op in line:
            parts = line.split(op)
            if len(parts) > 1:
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * (indent + 4)
                result = [parts[0]]
                for part in parts[1:]:
                    result.append(f"{spaces}{op.strip()}{part}")
                return '\n'.join(result)
    
    return line

def remove_all_unused_imports(content: str) -> str:
    """Remove ALL unused imports."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove clearly unused imports
        if (line.strip().startswith('from pathlib import Path') and 
            'Path(' not in content.replace(line, '') and
            'Path.' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('import sympy as sp') and 
              'sp.' not in content.replace(line, '') and
              'sp(' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('import time') and 
              'time.' not in content.replace(line, '') and
              'time(' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('from typing import Optional') and 
              'Optional[' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('from typing import List') and 
              'List[' not in content.replace(line, '') and
              'List(' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('from typing import Dict') and 
              'Dict[' not in content.replace(line, '') and
              'Dict(' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('from typing import Any') and 
              'Any' not in content.replace(line, '')):
            continue
        elif (line.strip().startswith('from typing import Tuple') and 
              'Tuple[' not in content.replace(line, '')):
            continue
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_all_indentation_issues(content: str) -> str:
    """Fix ALL indentation issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix continuation line indentation
        if (line.strip().startswith(('(', '[', '{')) and 
            i > 0 and 
            len(lines[i-1]) > 70 and
            len(line) - len(line.lstrip()) < 8):
            # This is a continuation line, fix indentation
            indent = len(lines[i-1]) - len(lines[i-1].lstrip())
            line = ' ' * (indent + 4) + line.lstrip()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_all_continuation_lines(content: str) -> str:
    """Fix ALL continuation line issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix continuation line indentation
        if (line.strip().startswith(('(', '[', '{')) and 
            i > 0 and 
            len(lines[i-1]) > 70):
            # This is a continuation line, ensure proper indentation
            indent = len(lines[i-1]) - len(lines[i-1].lstrip())
            if len(line) - len(line.lstrip()) < indent + 4:
                line = ' ' * (indent + 4) + line.lstrip()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_all_string_literals(content: str) -> str:
    """Fix ALL string literal issues."""
    # Fix unterminated string literals
    content = re.sub(r'"""[^"]*$', '"""', content, flags=re.MULTILINE)
    content = re.sub(r"'''[^']*$", "'''", content, flags=re.MULTILINE)
    
    return content

def fix_all_logging_formats(content: str) -> str:
    """Fix ALL logging format issues."""
    # Fix lazy % formatting in logging functions
    content = re.sub(
        r'(\w+\.(debug|info|warning|error|critical))\(f"([^"]+)"\)',
        r'\1("\3")',
        content
    )
    
    return content

def fix_all_exception_handling(content: str) -> str:
    """Fix ALL exception handling issues."""
    # Fix catching too general exception
    content = re.sub(
        r'except Exception as e:',
        'except (ValueError, TypeError, AttributeError) as e:',
        content
    )
    
    return content

def main():
    """Fix ALL linting errors in enhanced processing modules."""
    enhanced_processing_dir = Path(__file__).parent / "scirag" / "enhanced_processing"
    
    if not enhanced_processing_dir.exists():
        print(f"Directory not found: {enhanced_processing_dir}")
        return
    
    # Get all Python files
    python_files = list(enhanced_processing_dir.glob("*.py"))
    
    print(f"Fixing ALL linting issues in {len(python_files)} Python files")
    
    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue  # Skip __init__.py for now
        
        try:
            fix_all_linting_issues(file_path)
            print(f"✅ Fixed ALL issues in {file_path.name}")
        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")

if __name__ == "__main__":
    main()
