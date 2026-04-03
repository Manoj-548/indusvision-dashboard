#!/usr/bin/env python
"""
Consolidate knowledge from all documentation files in the workspace.
This script extracts key information from .md files and creates a unified knowledge base model.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class KnowledgeConsolidator:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.knowledge_base = {
            'timestamp': datetime.now().isoformat(),
            'modules': {},
            'tools': {},
            'apis': {},
            'workflows': {},
            'references': [],
            'best_practices': [],
        }
    
    def extract_from_markdown(self, filepath):
        """Extract structured information from markdown files."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'file': str(filepath.relative_to(self.root_path)),
                'size': len(content),
                'sections': self._extract_sections(content),
                'headers': self._extract_headers(content),
                'code_blocks': self._count_code_blocks(content),
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_sections(self, content):
        """Extract main sections from markdown."""
        sections = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                section = line[2:].strip()
                sections.append({
                    'title': section,
                    'line': i,
                    'content_preview': '\n'.join(lines[i:min(i+10, len(lines))])[:200]
                })
        return sections
    
    def _extract_headers(self, content):
        """Extract all headers from markdown."""
        headers = defaultdict(list)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('# ').strip()
                headers[level].append(title)
        return dict(headers)
    
    def _count_code_blocks(self, content):
        """Count code blocks by language."""
        code_blocks = defaultdict(int)
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].startswith('```'):
                lang = lines[i][3:].strip() or 'unknown'
                code_blocks[lang] += 1
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    i += 1
            i += 1
        return dict(code_blocks)
    
    def consolidate(self):
        """Consolidate knowledge from all markdown files."""
        doc_files = list(self.root_path.rglob('doc_*.md'))
        doc_files += list(self.root_path.rglob('*KNOWLEDGE*.md'))
        doc_files += list(self.root_path.rglob('*GUIDE*.md'))
        doc_files += list(self.root_path.rglob('README.md'))
        
        for doc_file in set(doc_files):  # Use set to avoid duplicates
            if doc_file.is_file():
                info = self.extract_from_markdown(doc_file)
                if 'error' not in info:
                    self.knowledge_base['references'].append(info)
        
        return self.knowledge_base
    
    def add_module_info(self, module_name, description, components):
        """Add module information."""
        self.knowledge_base['modules'][module_name] = {
            'description': description,
            'components': components,
            'added_at': datetime.now().isoformat(),
        }
    
    def save_to_json(self, output_path):
        """Save consolidated knowledge to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, default=str)
        print(f"Knowledge base saved to {output_path}")


def run_consolidation():
    """Run the knowledge consolidation process."""
    root = Path(__file__).parent.parent.parent  # Navigate to manoj folder
    consolidator = KnowledgeConsolidator(root)
    
    # Add module information
    modules = {
        'annotation': 'Data annotation and labeling system for training datasets',
        'automation': 'Automated workflow execution and task scheduling',
        'sandbox': 'Safe environment for testing new features',
        'spider': 'Web crawling and data extraction system',
        'wrangling': 'Data cleaning and transformation tools',
        'sensor': 'IoT and sensor data collection',
        'camera': 'Live camera feed processing and recording',
    }
    
    for module_name, description in modules.items():
        consolidator.add_module_info(
            module_name, 
            description,
            ['task processor', 'data model', 'API endpoint', 'dashboard widget']
        )
    
    # Consolidate knowledge
    kb = consolidator.consolidate()
    
    # Save results
    output_path = Path(__file__).parent / 'knowledge_base.json'
    consolidator.save_to_json(output_path)
    
    print(f"\nConsolidation complete!")
    print(f"Total references found: {len(kb['references'])}")
    print(f"Modules documented: {len(kb['modules'])}")
    
    return kb


if __name__ == '__main__':
    run_consolidation()
