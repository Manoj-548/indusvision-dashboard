#!/usr/bin/env python
"""
Consolidate knowledge from new_folder_destination doc_* and script_* files for IndusVision Dashboard.
Supports Celery task integration with KnowledgeEntry model population.
"""

from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

def get_consolidation_root():
    """Return path to new_folder_destination."""
    base = Path(__file__).resolve().parent.parent  # ConsolidatedProjects
    return base / "new_folder_destination"

def extract_from_file(filepath):
    """Extract structured information from doc/script file."""
    extract = {
        'file': str(filepath.name),
        'path': str(filepath.relative_to(get_consolidation_root())),
        'size': 0,
        'title': '',
        'content_preview': '',
        'headers': [],
        'code_blocks': {},
        'sections': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        extract['size'] = len(content)
        
        # Title from filename
        filename = filepath.name
        title = filename.replace('doc_', '').replace('script_', '').replace('.md', '').replace('.py', '').replace('.bat', '').replace('.ps1', '').title()
        extract['title'] = title
        
        # Preview
        extract['content_preview'] = content[:300] + '...' if len(content) > 300 else content
        
        # Headers and sections
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title = line[2:].strip()
                extract['headers'].append(title)
                extract['sections'].append({
                    'title': title,
                    'line': i,
                    'preview': line.strip()
                })
        
        # Code blocks
        code_blocks = defaultdict(int)
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('```'):
                lang = line[3:].strip()
                if not lang:
                    lang = 'unknown'
                code_blocks[lang] += 1
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
            i += 1
        extract['code_blocks'] = dict(code_blocks)
        
    except Exception as e:
        extract['error'] = str(e)
    
    return extract

def consolidate_knowledge():
    """Consolidate and return list of extracts."""
    root = get_consolidation_root()
    if not root.exists():
        return {'error': f'Path not found: {root}'}
    
    extracts = []
    
    # Scan doc_* and script_* files plus common code and data engineering formats
    patterns = [
        'doc_*.*', 'script_*.*', '*.md', '*.py', '*.bat', '*.ps1', '*.txt', '*.cs',
        '*.js', '*.jsx', '*.ts', '*.tsx', '*.java', '*.go', '*.rb', '*.json',
        '*.yaml', '*.yml', '*.sql', '*.xml', '*.ini', '*.cfg', '*.unity'
    ]
    for pattern in patterns:
        for filepath in root.glob(pattern):
            extract = extract_from_file(filepath)
            if 'error' not in extract:
                extracts.append(extract)
    
    kb = {
        'timestamp': datetime.now().isoformat(),
        'root_path': str(root),
        'total_files': len(extracts),
        'extracts': extracts
    }
    
    return kb

if __name__ == '__main__':
    kb = consolidate_knowledge()
    output_path = get_consolidation_root() / 'knowledge_base.json'
    with open(output_path, 'w') as f:
        json.dump(kb, f, indent=2, default=str)
    print(f"Consolidated {kb['total_files']} knowledge items to {output_path}")

