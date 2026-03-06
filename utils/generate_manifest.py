#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: utils/generate_manifest.py
Version: 1.1.2
Objective: Generate a comprehensive FILE_MANIFEST.md from the utils/ directory.
"""

import os
import re

# Resolve the project root by going up one level from utils/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRECTORIES = ['core/preflight', 'core/flight', 'core/postflight', 'logic', 'tests', 'utils']
MANIFEST_FILE = os.path.join(BASE_DIR, 'FILE_MANIFEST.md')

def get_file_info(filepath):
    """Extracts Version and Objective from the file's docstring."""
    version, objective = "N/A", "No objective defined."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Match strict manifest header format
            v_match = re.search(r"Version:\s*([\d\.]+)", content)
            o_match = re.search(r"Objective:\s*(.*)", content)
            if v_match:
                version = v_match.group(1)
            if o_match:
                objective = o_match.group(1).strip()
    except Exception:
        pass
    return version, objective

def generate_manifest():
    """Builds the Markdown table for the manifest file."""
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as md:
        md.write("# Seestar Organizer File Manifest\n\n")
        md.write("| Path | Version | Objective |\n")
        md.write("| :--- | :--- | :--- |\n")
        
        for directory in TARGET_DIRECTORIES:
            dir_path = os.path.join(BASE_DIR, directory)
            if not os.path.exists(dir_path):
                continue
                
            # Filter for scripts and data assets
            for filename in sorted(os.listdir(dir_path)):
                if filename.endswith('.py') or filename.endswith('.psv'):
                    full_path = os.path.join(dir_path, filename)
                    # Create a relative path for the display table
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    ver, obj = get_file_info(full_path)
                    md.write(f"| {rel_path} | {ver} | {obj} |\n")

if __name__ == "__main__":
    generate_manifest()
    print(f"✅ {MANIFEST_FILE} updated successfully.")
