"""
Result formatter utilities for displaying DAG execution results in a readable format.

This module provides functions to format and display various data structures,
with special support for markdown content.
"""


def format_and_display_results(xcom_results):
    """Format and display the DAG execution results in a readable way"""
    if not xcom_results:
        print("❌ No results returned from DAG execution")
        return
    
    print("\n" + "="*80)
    print("🎉 DAG EXECUTION COMPLETED SUCCESSFULLY!")
    print("="*80)
    
    for task_id, result in xcom_results.items():
        print(f"\n📋 Task: {task_id}")
        print("-" * 50)
        print_readable_content(result)
    
    print("\n" + "="*80)


def print_readable_content(data, indent_level=0):
    """Recursively print any data structure in a readable markdown-friendly format"""
    indent = "  " * indent_level
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_display = key.replace('_', ' ').title()
            
            if isinstance(value, str) and len(value) > 100:
                # Long text content - likely markdown
                print(f"\n{indent}📄 {key_display}:")
                print(f"{indent}" + "=" * 60)
                print_markdown_content(value, indent)
            elif isinstance(value, (dict, list)):
                # Nested structure
                print(f"\n{indent}📂 {key_display}:")
                print_readable_content(value, indent_level + 1)
            else:
                # Simple value
                print(f"{indent}📊 {key_display}: {value}")
                
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"\n{indent}📌 Item {i+1}:")
            print_readable_content(item, indent_level + 1)
            
    elif isinstance(data, str):
        if len(data) > 100:
            print_markdown_content(data, indent)
        else:
            print(f"{indent}{data}")
    else:
        print(f"{indent}{data}")


def print_markdown_content(content, base_indent=""):
    """Print markdown content with better formatting"""
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            print()
            continue
            
        # Headers
        if line.startswith('#'):
            header_level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('# ').strip()
            if header_level == 1:
                print(f"\n{base_indent}🔥 {header_text}")
                print(f"{base_indent}" + "=" * (len(header_text) + 3))
            elif header_level == 2:
                print(f"\n{base_indent}🚀 {header_text}")
                print(f"{base_indent}" + "-" * (len(header_text) + 3))
            else:
                print(f"\n{base_indent}{'  ' * (header_level-3)}💡 {header_text}")
        
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            print(f"{base_indent}  • {bullet_text}")
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            num_text = line[3:].strip()
            num = line[:2]
            print(f"{base_indent}  {num} {num_text}")
        
        # Bold text (simple detection)
        elif '**' in line:
            # Simple bold formatting
            formatted_line = line.replace('**', '🔸 ').replace('🔸 🔸 ', ' ')
            print(f"{base_indent}{formatted_line}")
        
        # Regular text
        else:
            print(f"{base_indent}{line}")
    
    print()  # Add spacing after content


def format_result_to_string(data, indent_level=0):
    """
    Convert result data to a formatted string instead of printing directly.
    Useful for saving to files or further processing.
    """
    output_lines = []
    indent = "  " * indent_level
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_display = key.replace('_', ' ').title()
            
            if isinstance(value, str) and len(value) > 100:
                output_lines.append(f"\n{indent}{key_display}:")
                output_lines.append(f"{indent}" + "=" * 60)
                output_lines.extend(_markdown_to_string_lines(value, indent))
            elif isinstance(value, (dict, list)):
                output_lines.append(f"\n{indent}{key_display}:")
                output_lines.extend(format_result_to_string(value, indent_level + 1))
            else:
                output_lines.append(f"{indent}{key_display}: {value}")
                
    elif isinstance(data, list):
        for i, item in enumerate(data):
            output_lines.append(f"\n{indent}Item {i+1}:")
            output_lines.extend(format_result_to_string(item, indent_level + 1))
            
    elif isinstance(data, str):
        if len(data) > 100:
            output_lines.extend(_markdown_to_string_lines(data, indent))
        else:
            output_lines.append(f"{indent}{data}")
    else:
        output_lines.append(f"{indent}{data}")
    
    return output_lines


def _markdown_to_string_lines(content, base_indent=""):
    """Helper function to convert markdown content to formatted string lines"""
    lines = content.split('\n')
    output_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            output_lines.append("")
            continue
            
        # Headers
        if line.startswith('#'):
            header_level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('# ').strip()
            if header_level == 1:
                output_lines.append(f"\n{base_indent}{header_text}")
                output_lines.append(f"{base_indent}" + "=" * len(header_text))
            elif header_level == 2:
                output_lines.append(f"\n{base_indent}{header_text}")
                output_lines.append(f"{base_indent}" + "-" * len(header_text))
            else:
                output_lines.append(f"\n{base_indent}{'  ' * (header_level-3)}{header_text}")
        
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            output_lines.append(f"{base_indent}  • {bullet_text}")
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            num_text = line[3:].strip()
            num = line[:2]
            output_lines.append(f"{base_indent}  {num} {num_text}")
        
        # Bold text (simple detection)
        elif '**' in line:
            formatted_line = line.replace('**', '').replace('  ', ' ')
            output_lines.append(f"{base_indent}{formatted_line}")
        
        # Regular text
        else:
            output_lines.append(f"{base_indent}{line}")
    
    output_lines.append("")  # Add spacing after content
    return output_lines
