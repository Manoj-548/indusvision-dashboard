from dashboard.tasks import sync_source_files, consolidate_knowledge_task
print("Syncing source files...")
print(sync_source_files())
print("Consolidating knowledge...")
print(consolidate_knowledge_task())
print("Consolidation complete! Check http://localhost:8000/dashboard/")
