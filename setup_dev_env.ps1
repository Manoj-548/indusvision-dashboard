# ================================
# INDUSVISION DEV ENV AUTO SETUP
# ================================

$projectPath = "C:\Users\manoj\ConsolidatedProjects\indusvision-dashboard"
$pythonEnvPath = "C:\Users\manoj\IndusVision_WorkBook\Scripts\python.exe"
$jdkPath = "C:\Program Files\Java\jdk-21"

Write-Host "`n[1/6] Moving to Project Directory..."
Set-Location $projectPath

Write-Host "[2/6] Ensuring .vscode folder exists..."
New-Item -ItemType Directory -Force -Path ".vscode" | Out-Null

Write-Host "[3/6] Writing VS Code settings.json..."
$settings = @{
    "python.defaultInterpreterPath" = $pythonEnvPath
    "java.jdt.ls.java.home"         = $jdkPath
} | ConvertTo-Json -Depth 5

$settings | Set-Content ".vscode\settings.json"

Write-Host "[4/6] Setting JAVA_HOME for current session..."
$env:JAVA_HOME = $jdkPath
$env:Path = "$jdkPath\bin;$env:Path"

Write-Host "[5/6] Installing Python Dependencies..."
& $pythonEnvPath -m pip install --upgrade pip
& $pythonEnvPath -m pip install -r requirements.txt
Write-Host "Dependencies installed."

Write-Host "[6/6] Verifying Environment..."
Write-Host "`nPython Path:"
& $pythonEnvPath -c "import sys; print(sys.executable)"

Write-Host "`nPython Version:"
& $pythonEnvPath --version

Write-Host "`nOpenCV Check:"
& $pythonEnvPath -c "import cv2; print('OpenCV version:', cv2.__version__)"

Write-Host "`nDjango Check:"
& $pythonEnvPath -c "import django; print('Django version:', django.get_version())"

Write-Host "`nJava Version:"
java -version

Write-Host "[7/7] Setup Complete! Run: python manage.py runserver."

# OPTIONAL CLEANUP (UNCOMMENT ONLY IF SAFE)
# Remove-Item "C:\Users\manoj\.venv" -Recurse -Force
# Remove-Item "C:\Users\manoj\Projects.bak.20260220024449\python_api\.venv" -Recurse -Force

Write-Host "`nDONE: VS Code + Python + Java configured for IndusVision."
