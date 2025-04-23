#!/usr/bin/env python3
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


"""
Script to apply license headers to all Python files in the project.
"""

import os
import re
from datetime import datetime

# License header template
LICENSE_HEADER = '''"""
Copyright (c) {year} nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""

'''

# File patterns to apply the license to
INCLUDE_PATTERNS = ['.py']

# Directories to exclude
EXCLUDE_DIRS = ['venv', '.venv', '__pycache__', '.git', 'build', 'dist', 'node_modules']

# Files to exclude
EXCLUDE_FILES = ['__init__.py']

def should_process_file(file_path):
    """Determine if a file should have a license header applied."""
    # Check if file has an extension we want to process
    should_process = False
    for pattern in INCLUDE_PATTERNS:
        if file_path.endswith(pattern):
            should_process = True
            break
    
    if not should_process:
        return False
    
    # Check if file is in the exclusion list
    filename = os.path.basename(file_path)
    if filename in EXCLUDE_FILES:
        return False
    
    return True

def has_license_header(content):
    """Check if the file already has a license header."""
    # Check if the first X lines of the file contain the word "Copyright"
    first_lines = content.split('\n')[:10]
    for line in first_lines:
        if 'Copyright' in line:
            return True
    return False

def add_license_to_file(file_path):
    """Add license header to a file if it doesn't already have one."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_license_header(content):
        print(f"Skipping (already has header): {file_path}")
        return False
    
    # For Python files, we need to handle shebang and encoding declarations
    if file_path.endswith('.py'):
        lines = content.split('\n')
        new_content = []
        
        # Check if first line is a shebang or encoding declaration
        first_line_index = 0
        if lines and (lines[0].startswith('#!') or lines[0].startswith('# -*- coding')):
            new_content.append(lines[0])
            first_line_index = 1
        
        # Add license header
        current_year = datetime.now().year
        license_text = LICENSE_HEADER.format(year=current_year)
        new_content.append(license_text)
        
        # Add the rest of the content
        new_content.extend(lines[first_line_index:])
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_content))
    
    print(f"Added license header to: {file_path}")
    return True

def process_directory(directory):
    """Process all files in a directory recursively."""
    files_processed = 0
    files_updated = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            if should_process_file(file_path):
                files_processed += 1
                if add_license_to_file(file_path):
                    files_updated += 1
    
    return files_processed, files_updated

if __name__ == "__main__":
    print("Applying license headers to source files...")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    files_processed, files_updated = process_directory(project_root)
    
    print(f"Completed! Processed {files_processed} files, updated {files_updated} files.")