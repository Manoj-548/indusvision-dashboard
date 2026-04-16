from datetime import datetime
from pathlib import Path
import os
import django

# =========================================================
# DJANGO SETUP
# =========================================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "indusvision.settings")
django.setup()

from django.db import transaction
from django.utils import timezone
from dashboard.models import SourceFile


# =========================================================
# CONFIG
# =========================================================
BASE_PATHS = [
    Path(__file__).resolve().parents[1],      # Current Project Root
    Path.home() / "Desktop",
    Path.home() / "Downloads",
    Path.home() / "ConsolidatedProjects",
    Path.home() / "ollama-code-pilot-manoj548",
]

EXTENSIONS = {
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
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.sql': 'sql',
    '.xml': 'xml',
    '.txt': 'doc',
    '.unity': 'doc',
}

COUNT_EXTS = {
    '.py', '.html', '.htm', '.index', '.md',
    '.bat', '.ps1', '.cs', '.js', '.jsx',
    '.ts', '.tsx', '.java', '.go', '.rb',
    '.sh', '.yaml', '.yml', '.json', '.sql', '.txt'
}

SKIP_DIRS = {
    'venv',
    '__pycache__',
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    'dist',
    'build',
}

MAX_JPG = 300


# =========================================================
# SYNC LOGIC
# =========================================================
@transaction.atomic
def sync_source_files():
    """
    Fast bulk sync for all workspaces.
    Safe for SQLite/Postgres.
    """

    existing_files = {
        sf.path: sf
        for sf in SourceFile.objects.all()
    }

    to_create = []
    to_update = []

    scanned = 0
    jpg_skipped = 0

    seen_paths = set()

    for base in BASE_PATHS:
        if not base.exists():
            print(f"Skipping missing path: {base}")
            continue

        print(f"\nScanning: {base}")

        for p in base.rglob('*'):

            if not p.is_file():
                continue

            if any(skip in p.parts for skip in SKIP_DIRS):
                continue

            suffix = p.suffix.lower()

            if suffix == '.jpg':
                jpg_skipped += 1
                if jpg_skipped > MAX_JPG:
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

            file_type = EXTENSIONS.get(suffix, 'other')

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
            if suffix in COUNT_EXTS:
                try:
                    with p.open(
                        'r',
                        encoding='utf-8',
                        errors='ignore'
                    ) as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    pass

            defaults = {
                'file_type': file_type,
                'line_count': line_count,
                'last_updated': mtime,
                'size_bytes': size_bytes,
                'is_dashboard_relevant': file_type in {
                    'py', 'html', 'index', 'script',
                    'doc', 'js', 'ts', 'java',
                    'json', 'yaml', 'sql',
                    'xml', 'cs', 'ruby', 'go'
                },
                'is_knowledge_relevant': file_type in {
                    'doc', 'script', 'py', 'js',
                    'ts', 'java', 'json',
                    'yaml', 'sql'
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
                    SourceFile(
                        path=db_path,
                        **defaults
                    )
                )

    # =====================================================
    # BULK DATABASE OPS
    # =====================================================
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
                'is_knowledge_relevant',
            ],
            batch_size=500
        )

    print("\n========================================")
    print("SYNC COMPLETE")
    print("========================================")
    print(f"Scanned Files   : {scanned}")
    print(f"Created Records : {len(to_create)}")
    print(f"Updated Records : {len(to_update)}")
    print(f"JPG Skipped     : {jpg_skipped}")
    print("========================================\n")

    return {
        "scanned": scanned,
        "created": len(to_create),
        "updated": len(to_update),
        "jpg_skipped": jpg_skipped,
        "bases": [str(p) for p in BASE_PATHS],
    }


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    sync_source_files()
