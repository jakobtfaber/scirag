#!/usr/bin/env python3
"""
Comprehensive Final Linting Fix Script

This script addresses all remaining 180 linting errors systematically.
"""

import os
import re
from pathlib import Path

def fix_file_comprehensively(file_path: Path):
    """Fix all linting issues in a single file comprehensively."""
    print(f"Comprehensively fixing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove all trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix 2: Remove blank lines with only whitespace
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # Fix 3: Fix line length issues by breaking long lines intelligently
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 79:
            fixed_line = fix_long_line(line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix 4: Remove unused imports
    content = remove_unused_imports(content)
    
    # Fix 5: Fix type annotations
    content = fix_type_annotations(content)
    
    # Fix 6: Fix indentation issues
    content = fix_indentation_issues(content)
    
    # Fix 7: Ensure proper file ending
    content = content.rstrip() + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_long_line(line: str) -> str:
    """Fix a single long line by breaking it intelligently."""
    if len(line) <= 79:
        return line
    
    # Don't break strings or comments
    if line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''"):
        return line
    
    # Break long import statements
    if 'import' in line and len(line) > 79:
        return break_import_line(line)
    
    # Break long function definitions
    if 'def ' in line and '(' in line and ')' in line and len(line) > 79:
        return break_function_definition(line)
    
    # Break long assignments
    if ' = ' in line and len(line) > 79:
        return break_assignment(line)
    
    # Break long method calls
    if '.' in line and '(' in line and len(line) > 79:
        return break_method_call(line)
    
    # Break long string concatenations
    if ' + ' in line and len(line) > 79:
        return break_string_concatenation(line)
    
    # For other long lines, try to break at logical points
    return break_at_logical_points(line)

def break_import_line(line: str) -> str:
    """Break long import lines."""
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

def break_assignment(line: str) -> str:
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

def remove_unused_imports(content: str) -> str:
    """Remove unused imports."""
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
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_type_annotations(content: str) -> str:
    """Fix type annotation issues."""
    # Fix default parameter type issues
    content = re.sub(
        r'metadata: dict\[str, Any\] = None',
        'metadata: Optional[Dict[str, Any]] = None',
        content
    )
    
    content = re.sub(
        r'source_ids: list\[str\] = None',
        'source_ids: Optional[List[str]] = None',
        content
    )
    
    # Add missing imports if needed
    if 'Optional[' in content and 'from typing import' in content:
        if 'Optional' not in content.split('from typing import')[1].split('\n')[0]:
            content = re.sub(
                r'from typing import ([^)]+)',
                r'from typing import \1, Optional',
                content
            )
    
    return content

def fix_indentation_issues(content: str) -> str:
    """Fix indentation issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix continuation line indentation
        if line.strip().startswith(('(', '[', '{')) and len(line) > 79:
            # This is a continuation line, ensure proper indentation
            indent = len(line) - len(line.lstrip())
            if indent < 4:
                line = '    ' + line.lstrip()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    """Fix all linting errors in enhanced processing modules."""
    enhanced_processing_dir = Path(__file__).parent / "scirag" / "enhanced_processing"
    
    if not enhanced_processing_dir.exists():
        print(f"Directory not found: {enhanced_processing_dir}")
        return
    
    # Get all Python files
    python_files = list(enhanced_processing_dir.glob("*.py"))
    
    print(f"Found {len(python_files)} Python files to fix comprehensively")
    
    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue  # Skip __init__.py for now
        
        try:
            fix_file_comprehensively(file_path)
            print(f"✅ Comprehensively fixed {file_path.name}")
        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")

if __name__ == "__main__":
    main()
