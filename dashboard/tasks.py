from datetime import datetime
import random
from .models import MetricRecord, SourceFile, KnowledgeEntry
from django.utils import timezone
from pathlib import Path
import json

def sync_source_files():
    """Non-Celery version for shell."""
    repo_root = Path(__file__).resolve().parents[1]
    updated = 0
    jpg_count = 0
    extensions = {'.py': 'py', '.html': 'html', '.htm': 'html', '.index': 'index', '.json': 'other', '.md': 'doc', '.bat': 'script', '.ps1': 'script'}
    count_exts = ['.py', '.html', '.htm', '.index', '.md', '.bat', '.ps1']
    
    for p in repo_root.rglob('*'):
        if not p.is_file(): continue
        if p.match('**/venv/**') or p.match('**/__pycache__/**') or p.match('**/.git/**'): continue
        
        rel_path = str(p.relative_to(repo_root))
        
        if p.suffix.lower() == '.jpg':
            jpg_count += 1
            if jpg_count > 200: continue
        
        file_type = 'other'
        if 'script_' in rel_path:
            file_type = 'script'
        elif 'doc_' in rel_path:
            file_type = 'doc'
        elif p.suffix.lower() in extensions:
            file_type = extensions[p.suffix.lower()]
        
        mtime = None
        try:
            mtime = timezone.make_aware(datetime.fromtimestamp(p.stat().st_mtime))
        except: pass
        
        line_count = 0
        if p.suffix.lower() in count_exts:
            try:
                with p.open('r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
            except: pass
        
        sf, _ = SourceFile.objects.update_or_create(
            path=rel_path,
            defaults={
                'file_type': file_type,
                'line_count': line_count,
                'last_updated': mtime,
                'size_bytes': p.stat().st_size,
                'is_dashboard_relevant': file_type in ['py', 'html', 'index', 'script', 'doc'],
                'is_knowledge_relevant': file_type in ['doc', 'script'],
            }
        )
        updated += 1
    
    print(f'Updated {updated} files, skipped {jpg_count} images')
    return {'updated': updated, 'jpg_count': jpg_count}

def consolidate_knowledge_task():
    """Non-Celery version for shell - uses consolidate_knowledge.py."""
    from consolidate_knowledge import consolidate_knowledge
    kb = consolidate_knowledge()
    if 'error' in kb:
        print(f"Error: {kb['error']}")
        return kb
    created = 0
    for extract in kb['extracts']:
        try:
            sf = SourceFile.objects.get(path=extract['path'])
            ke, new = KnowledgeEntry.objects.update_or_create(
                source_file=sf,
                defaults={
                    'knowledge_type': 'script' if 'script_' in extract['path'] else 'doc',
                    'title': extract['title'],
                    'content_preview': extract['content_preview'],
                    'extracted_data': extract
                }
            )
            if new:
                created += 1
        except SourceFile.DoesNotExist:
            continue
    print(f'Created {created} KnowledgeEntry items')
    return {'created': created, 'total_extracted': len(kb['extracts'])}

# Celery tasks (require Redis)
from celery import shared_task

@shared_task
def celery_sync_source_files():
    return sync_source_files()

@shared_task
def celery_consolidate_knowledge_task():
    return consolidate_knowledge_task()


