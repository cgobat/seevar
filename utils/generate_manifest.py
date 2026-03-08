#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: /home/ed/seestar_organizer/utils/generate_manifest.py
Version: 1.2.5
Objective: Generate a comprehensive FILE_MANIFEST.md in logic/ while excluding reference catalogs.
"""

import os
import re

# Resolve the project root (one level up from utils/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRECTORIES = ['core/preflight', 'core/flight', 'core/postflight', 'logic', 'tests', 'utils', 'bruno']
MANIFEST_FILE = os.path.join(BASE_DIR, 'logic/FILE_MANIFEST.md')

def get_file_info(filepath):
    """Extracts Version and Objective from the file's docstring or header."""
    version, objective = "N/A", "No objective defined."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read first 2KB to capture headers without loading entire large files
            content = f.read(2048)
            # Match strict manifest header format for .py, .sh, .md, and .psv
            v_match = re.search(r"(?:Version:|# Version:)\s*([\d\.]+)", content)
            o_match = re.search(r"(?:Objective:|# Objective:)\s*(.*)", content)
            if v_match:
                version = v_match.group(1).strip()
            if o_match:
                # Clean up trailing comment characters or Markdown formatting
                objective = o_match.group(1).strip().rstrip(' */#')
    except Exception:
        pass
    return version, objective

def generate_manifest():
    """Builds the Markdown table for the manifest file."""
    # Ensure the logic directory exists
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as md:
        md.write("# 🔭 S30-PRO Federation: File Manifest\n\n")
        md.write("> **System State**: Diamond Revision (Sovereign)\n\n")
        md.write("| Path | Version | Objective |\n")
        md.write("| :--- | :--- | :--- |\n")
        
        for directory in TARGET_DIRECTORIES:
            dir_path = os.path.join(BASE_DIR, directory)
            if not os.path.exists(dir_path):
                continue
                
            # Iterate through files in the target directory
            for filename in sorted(os.listdir(dir_path)):
                # Ignore hidden files and the manifest itself to prevent recursion
                if filename.startswith('.') or filename == 'FILE_MANIFEST.md':
                    continue
                
                # Only include logic, script, and protocol assets
                if filename.endswith(('.py', '.psv', '.sh', '.md', '.bru')):
                    full_path = os.path.join(dir_path, filename)
                    
                    # Double-check we aren't in the excluded catalogs directory
                    if 'catalogs/reference_stars' in full_path:
                        continue
                        
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    ver, obj = get_file_info(full_path)
                    md.write(f"| {rel_path} | {ver} | {obj} |\n")

if __name__ == "__main__":
    generate_manifest()
    print(f"✅ {MANIFEST_FILE} updated successfully.")
