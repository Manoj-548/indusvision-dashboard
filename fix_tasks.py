from pathlib import Path
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import sys
import django

sys.path.append('.')
django.setup()

from dashboard.models import SourceFile, KnowledgeEntry
from consolidate_knowledge import consolidate_knowledge

print("=== IndusVision FULL CONSOLIDATION START ===")

# Simple file scan without Django functions
base_paths = [
    Path.home() / "Desktop",
    Path.home() / "Downloads",
    Path.home() / "ConsolidatedProjects",
    Path.home() / "ollama-code-pilot-manoj548",
    Path(".").resolve()
]

updated = 0
for base in base_paths:
    print(f"Scanning {base}")
    for p in base.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.py', '.md', '.cs', '.unity', '.bat', '.ps1', '.html', '.js']:
            try:
                SourceFile.objects.get_or_create(
                    path=str(p),
                    defaults={
                        'file_type': p.suffix[1:] if p.suffix else 'other',
                        'line_count': sum(1 for _ in p.read_text(errors='ignore').splitlines()),
                        'size_bytes': p.stat().st_size,
                        'is_knowledge_relevant': True
                    }
                )
                updated += 1
            except Exception as e:
                print(f"Skip {p}: {e}")

print(f"Updated {updated} files in DB")

# Consolidate
kb = consolidate_knowledge()
print(f"Knowledge base: {kb}")

print("=== CONSOLIDATION COMPLETE ===")
print("Visit http://127.0.0.1:8000/dashboard/knowledge/ for results!")

