from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from dashboard.models import MetricRecord, SourceFile, KnowledgeEntry


# =========================================================
# SOURCE FILE SYNC
# =========================================================
@transaction.atomic
def sync_source_files():
    """
    Advanced optimized workspace scanner.
    Bulk updates/creates for performance.
    Safe for SQLite/Postgres.
    """

    base_paths = [
        Path(__file__).resolve().parents[1],
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "ConsolidatedProjects",
        Path.home() / "ollama-code-pilot-manoj548",
    ]

    extensions = {
        '.py': 'py',
        '.html': 'html',
        '.htm': 'html',
        '.index': 'index',
        '.json': 'json',
        '.md': 'doc',
        '.bat': 'script',
        '.ps1': 'script',
        '.cs': 'cs',
        '.js': 'js',
        '.jsx': 'js',
        '.ts': 'ts',
        '.tsx': 'ts',
        '.java': 'java',
        '.go': 'go',
        '.rb': 'ruby',
        '.sh': 'script',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sql': 'sql',
        '.xml': 'xml',
        '.ini': 'config',
        '.cfg': 'config',
        '.txt': 'doc',
        '.ipynb': 'notebook',
        '.unity': 'doc',
    }

    count_exts = {
        '.py', '.html', '.htm', '.index', '.md',
        '.bat', '.ps1', '.cs', '.js', '.jsx',
        '.ts', '.tsx', '.java', '.go', '.rb',
        '.sh', '.yaml', '.yml', '.json', '.sql', '.txt'
    }

    skip_dirs = {
        'venv',
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'node_modules',
        '.pytest_cache',
        'dist',
        'build',
    }

    MAX_JPG = 300

    jpg_count = 0
    scanned = 0

    existing_files = {
        sf.path: sf
        for sf in SourceFile.objects.all()
    }

    to_create = []
    to_update = []

    seen_paths = set()

    for base in base_paths:
        if not base.exists():
            continue

        print(f"Scanning: {base}")

        for p in base.rglob('*'):
            if not p.is_file():
                continue

            if any(skip in p.parts for skip in skip_dirs):
                continue

            suffix = p.suffix.lower()

            if suffix == '.jpg':
                jpg_count += 1
                if jpg_count > MAX_JPG:
                    continue

            try:
                rel_path = str(p.relative_to(base))
                db_path = f"{base.name}/{rel_path}"
            except Exception:
                db_path = str(p)

            if db_path in seen_paths:
                continue
            seen_paths.add(db_path)

            scanned += 1

            file_type = extensions.get(suffix, 'other')

            if 'script_' in db_path:
                file_type = 'script'
            elif 'doc_' in db_path:
                file_type = 'doc'

            try:
                stat = p.stat()
                size_bytes = stat.st_size
                mtime = timezone.make_aware(
                    datetime.fromtimestamp(stat.st_mtime)
                )
            except Exception:
                size_bytes = 0
                mtime = None

            line_count = 0
            if suffix in count_exts:
                try:
                    with p.open('r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    pass

            defaults = {
                'file_type': file_type,
                'line_count': line_count,
                'last_updated': mtime,
                'size_bytes': size_bytes,
                'is_dashboard_relevant': file_type in {
                    'py', 'html', 'index', 'script', 'doc',
                    'js', 'ts', 'java', 'json', 'yaml',
                    'sql', 'xml', 'cs', 'ruby', 'go'
                },
                'is_knowledge_relevant': file_type in {
                    'doc', 'script', 'py', 'js', 'ts',
                    'java', 'json', 'yaml', 'sql', 'md'
                }
            }

            if db_path in existing_files:
                sf = existing_files[db_path]

                changed = False
                for field, value in defaults.items():
                    if getattr(sf, field) != value:
                        setattr(sf, field, value)
                        changed = True

                if changed:
                    to_update.append(sf)

            else:
                to_create.append(
                    SourceFile(path=db_path, **defaults)
                )

    if to_create:
        SourceFile.objects.bulk_create(
            to_create,
            batch_size=500
        )

    if to_update:
        SourceFile.objects.bulk_update(
            to_update,
            fields=[
                'file_type',
                'line_count',
                'last_updated',
                'size_bytes',
                'is_dashboard_relevant',
                'is_knowledge_relevant'
            ],
            batch_size=500
        )

    print(
        f"Sync Complete | "
        f"Scanned={scanned} | "
        f"Created={len(to_create)} | "
        f"Updated={len(to_update)} | "
        f"Skipped JPG={jpg_count}"
    )

    return {
        "scanned": scanned,
        "created": len(to_create),
        "updated": len(to_update),
        "jpg_skipped": jpg_count,
        "bases": [str(b) for b in base_paths],
    }


# =========================================================
# KNOWLEDGE CONSOLIDATION
# =========================================================
@transaction.atomic
def consolidate_knowledge_task():
    """
    Optimized knowledge extraction sync.
    """

    from consolidate_knowledge import consolidate_knowledge

    kb = consolidate_knowledge()

    if 'error' in kb:
        print(f"Consolidation Error: {kb['error']}")
        return kb

    source_map = {
        sf.path: sf
        for sf in SourceFile.objects.all()
    }

    created = 0
    updated = 0

    for extract in kb['extracts']:
        sf = source_map.get(extract['path'])

        if not sf:
            continue

        ke, is_new = KnowledgeEntry.objects.update_or_create(
            source_file=sf,
            defaults={
                'knowledge_type': (
                    'script'
                    if 'script_' in extract['path']
                    else 'doc'
                ),
                'title': extract['title'],
                'content_preview': extract['content_preview'],
                'extracted_data': extract,
            }
        )

        if is_new:
            created += 1
        else:
            updated += 1

    print(
        f"Knowledge Sync Complete | "
        f"Created={created} | Updated={updated}"
    )

    return {
        "created": created,
        "updated": updated,
        "total_extracted": len(kb['extracts']),
    }


# =========================================================
# CELERY TASKS
# =========================================================
@shared_task
def celery_sync_source_files():
    return sync_source_files()


@shared_task
def celery_consolidate_knowledge_task():
    return consolidate_knowledge_task()