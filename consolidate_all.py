import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'indusvision.settings'
django.setup()

from pathlib import Path
from dashboard.tasks import sync_source_files, consolidate_knowledge_task

print("Syncing source files...")
print(sync_source_files())

print("Consolidating knowledge...")
print(consolidate_knowledge_task())

print("Complete! Check /dashboard/ and /dashboard/knowledge/")
