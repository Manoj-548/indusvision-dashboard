
import sys
sys.path.append('.')
from dashboard.tasks_fixed import sync_source_files, consolidate_knowledge_task
print("=== FULL WORKSPACE CONSOLIDATION ===")
print(sync_source_files())
print(consolidate_knowledge_task())
print("Consolidation complete! Visit dashboard.")

print(sync_source_files())
print(consolidate_knowledge_task())
