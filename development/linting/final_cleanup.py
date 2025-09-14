#!/usr/bin/env python3
"""
Final Cleanup Script - Fix the remaining 30 linting errors

This script addresses the final linting issues with surgical precision.
"""

import os
import re
from pathlib import Path

def fix_final_issues(file_path: Path):
    """Fix the final linting issues in a single file."""
    print(f"Final cleanup for {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove ALL trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix 2: Remove ALL blank lines with only whitespace
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # Fix 3: Fix line length issues
    content = fix_line_length_final(content)
    
    # Fix 4: Ensure proper file ending
    content = content.rstrip() + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_line_length_final(content: str) -> str:
    """Fix line length issues with final precision."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 79:
            fixed_line = break_line_final(line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def break_line_final(line: str) -> str:
    """Break a line with final precision."""
    if len(line) <= 79:
        return line
    
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * (indent + 4)
    
    # Break long assignments
    if ' = ' in line and len(line) > 79:
        return break_assignment_final(line)
    
    # Break long method calls
    if '.' in line and '(' in line and len(line) > 79:
        return break_method_call_final(line)
    
    # Break long string concatenations
    if ' + ' in line and len(line) > 79:
        return break_string_concatenation_final(line)
    
    # Break long conditional statements
    if ' and ' in line and len(line) > 79:
        return break_conditional_final(line, ' and ')
    
    if ' or ' in line and len(line) > 79:
        return break_conditional_final(line, ' or ')
    
    # Break long dictionary/list definitions
    if ('{' in line or '[' in line) and len(line) > 79:
        return break_collection_final(line)
    
    # Break long string literals
    if ('"' in line or "'" in line) and len(line) > 79:
        return break_string_literal_final(line)
    
    # For other long lines, try to break at logical points
    return break_at_logical_points_final(line)

def break_assignment_final(line: str) -> str:
    """Break long assignment statements with final precision."""
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

def break_method_call_final(line: str) -> str:
    """Break long method calls with final precision."""
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

def break_string_concatenation_final(line: str) -> str:
    """Break long string concatenations with final precision."""
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

def break_conditional_final(line: str, operator: str) -> str:
    """Break long conditional statements with final precision."""
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

def break_collection_final(line: str) -> str:
    """Break long collection definitions with final precision."""
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

def break_string_literal_final(line: str) -> str:
    """Break long string literals with final precision."""
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

def break_at_logical_points_final(line: str) -> str:
    """Break long lines at logical points with final precision."""
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

def main():
    """Fix the final linting issues in enhanced processing modules."""
    enhanced_processing_dir = Path(__file__).parent / "scirag" / "enhanced_processing"
    
    if not enhanced_processing_dir.exists():
        print(f"Directory not found: {enhanced_processing_dir}")
        return
    
    # Get all Python files
    python_files = list(enhanced_processing_dir.glob("*.py"))
    
    print(f"Final cleanup for {len(python_files)} Python files")
    
    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue  # Skip __init__.py for now
        
        try:
            fix_final_issues(file_path)
            print(f"✅ Final cleanup completed for {file_path.name}")
        except Exception as e:
            print(f"❌ Error in final cleanup of {file_path.name}: {e}")

if __name__ == "__main__":
    main()
