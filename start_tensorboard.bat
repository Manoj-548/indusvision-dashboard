@echo off
cd /d "C:\Users\manoj\ConsolidatedProjects\indusvision-dashboard"
call python -m pip install --user --upgrade setuptools wheel tensorboard
"C:\Users\manoj\AppData\Roaming\Python\Python314\Scripts\tensorboard.exe" --logdir tensorboard_logs --port 6006 --host 0.0.0.0
pause

