#!/usr/bin/env python3
"""
Standalone FULL consolidation script - no Django deps.
Scans all directories, extracts knowledge for IndusVision.
"""

from pathlib import Path
from datetime import datetime
import json
import re
from collections import defaultdict

BASE_PATHS = [
    Path.home() / "Desktop",
    Path.home() / "Downloads",
    Path.home() / "ConsolidatedProjects",
    Path.home() / "ollama-code-pilot-manoj548",
    Path.cwd()
]

EXTENSIONS = {
    '.py': 'python',
    '.md': 'doc',
    '.cs': 'csharp_unity',
    '.unity': 'unity',
    '.js': 'javascript',
    '.html': 'html',
    '.bat': 'batch',
    '.ps1': 'powershell'
}

def scan_and_extract():
    files = []
    for base in BASE_PATHS:
        print(f"Scanning {base}")
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in EXTENSIONS:
                try:
                    content = p.read_text(errors='ignore')
                    preview = content[:200]
                    
                    files.append({
                        'path': str(p),
                        'name': p.name,
                        'type': EXTENSIONS[p.suffix.lower()],
                        'size': p.stat().st_size,
                        'line_count': len(content.splitlines()),
                        'preview': preview,
                        'mtime': datetime.fromtimestamp(p.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    print(f"Skip {p}: {e}")
    return files

if __name__ == '__main__':
    knowledge = {
        'timestamp': datetime.now().isoformat(),
        'scanned_paths': [str(p) for p in BASE_PATHS],
        'total_files': 0,
        'files': []
    }
    
    knowledge['files'] = scan_and_extract()
    knowledge['total_files'] = len(knowledge['files'])
    
    output = Path.cwd() / 'full_knowledge_base.json'
    with open(output, 'w') as f:
        json.dump(knowledge, f, indent=2, default=str)
    
    print(f"✅ Consolidated {knowledge['total_files']} files from all directories!")
    print(f"Saved to {output}")
    print("Import to dashboard: python manage.py shell < full_knowledge_base.json")

