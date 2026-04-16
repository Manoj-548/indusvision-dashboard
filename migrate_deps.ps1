# Migrate .venv deps to IndusVision_WorkBook env
$projectPath = 'C:\Users\manoj\ConsolidatedProjects\indusvision-dashboard'
$workbookPip = 'C:\Users\manoj\IndusVision_WorkBook\Scripts\pip.exe'
$projectVenvPip = "$projectPath\venv\Scripts\pip.exe"

Set-Location $projectPath

# Export project .venv deps
& $projectVenvPip freeze | Out-File -FilePath 'requirements_project_venv.txt' -Encoding utf8

# Install into IndusVision_WorkBook (ignore already satisfied)
& $workbookPip install -r requirements_project_venv.txt --upgrade

Write-Host 'Migration complete. Updated IndusVision_WorkBook with .venv deps.'
Write-Host 'Run: .\\setup_dev_env.ps1'
Write-Host 'Then: python manage.py runserver'
