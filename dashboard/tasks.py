from datetime import datetime
from pathlib import Path
from django.utils import timezone
from django.db import close_old_connections, transaction
from celery import shared_task

from .models import SourceFile, KnowledgeEntry


# =========================================================
# FILE SCANNER
# =========================================================
def sync_source_files():
    """
    Scan configured directories and sync into SourceFile table.
    SQLite-safe and optimized for bulk scanning.
    """

    close_old_connections()

    base_paths = [
        Path(__file__).resolve().parents[1],
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "ConsolidatedProjects",
        Path.home() / "ollama-code-pilot-manoj548",
    ]

    updated = 0
    jpg_count = 0

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
        '.unity': 'doc'
    }

    count_exts = set(extensions.keys())

    for base in base_paths:
        if not base.exists():
            continue

        print(f"Scanning {base}")

        for p in base.rglob("*"):

            if not p.is_file():
                continue

            skip_parts = {
                "venv",
                "__pycache__",
                ".git",
                ".idea",
                ".vscode",
                "node_modules"
            }

            if any(part in skip_parts for part in p.parts):
                continue

            try:
                rel_path = str(p.relative_to(base))
            except Exception:
                rel_path = str(p)

            suffix = p.suffix.lower()

            if suffix == ".jpg":
                jpg_count += 1
                if jpg_count > 300:
                    continue

            file_type = extensions.get(suffix, "other")

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
                    with p.open("r", encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    pass

            with transaction.atomic():
                SourceFile.objects.update_or_create(
                    path=rel_path,
                    defaults={
                        "file_type": file_type,
                        "line_count": line_count,
                        "last_updated": mtime,
                        "size_bytes": size_bytes,
                        "is_dashboard_relevant": file_type in {
                            "py", "html", "index", "script",
                            "doc", "js", "ts", "java",
                            "json", "yaml", "sql", "xml",
                            "cs", "ruby", "go"
                        },
                        "is_knowledge_relevant": file_type in {
                            "doc", "script", "py", "js",
                            "ts", "java", "json", "yaml",
                            "sql", "md"
                        },
                    }
                )

            updated += 1

    close_old_connections()

    print(f"Sync complete → {updated} files, {jpg_count} jpg skipped")

    return {
        "updated": updated,
        "jpg_count": jpg_count,
    }


# =========================================================
# KNOWLEDGE CONSOLIDATION
# =========================================================
def consolidate_knowledge_task():
    """
    Build/update KnowledgeEntry records.
    """

    close_old_connections()

    try:
        from consolidate_knowledge import consolidate_knowledge
    except ImportError as e:
        return {"error": str(e)}

    kb = consolidate_knowledge()

    if "error" in kb:
        return kb

    created = 0

    for extract in kb.get("extracts", []):

        try:
            sf = SourceFile.objects.get(path=extract["path"])

            _, new = KnowledgeEntry.objects.update_or_create(
                source_file=sf,
                defaults={
                    "knowledge_type": (
                        "script"
                        if "script_" in extract["path"]
                        else "doc"
                    ),
                    "title": extract.get("title", ""),
                    "content_preview": extract.get("content_preview", ""),
                    "extracted_data": extract,
                }
            )

            if new:
                created += 1

        except SourceFile.DoesNotExist:
            continue

    close_old_connections()

    return {
        "created": created,
        "total_extracted": len(kb.get("extracts", []))
    }


# =========================================================
# CELERY WRAPPERS
# =========================================================
@shared_task
def celery_sync_source_files():
    return sync_source_files()


@shared_task
def celery_consolidate_knowledge_task():
    return consolidate_knowledge_task()