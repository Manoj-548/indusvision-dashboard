# Adapted minimal cleanup for PostgreSQL setup
# Remove SQLite if exists (switching to Postgres)
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

# Clear ALL migrations across apps (fresh start)
Get-ChildItem -Recurse -Directory -Filter "migrations" | ForEach-Object {
    Get-ChildItem $_.FullName -File | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
}

# Clear pycache everywhere
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Output "Cleanup complete. Run: python manage.py makemigrations && python manage.py migrate"

