# IndusVision Dashboard - Run Server & Optimization TODO

## Phase 1: Run Server with IndusVision_WorkBook
- [x] 1. Run setup_dev_env.ps1 to configure environment
- [x] 2. CD to project directory  
- [x] 3. Run python manage.py migrate (if needed)
- [x] 4. Run python manage.py collectstatic --noinput
- [x] 5. Start Django server with WorkBook Python
- [x] 6. Verify server at http://localhost:8000

## Phase 2: Environment Cleanup (Consolidate & Free Space)
- [ ] 1. Identify all .venv directories across workspace (use cleanup_venvs.bat?)
- [ ] 2. Keep only IndusVision_WorkBook, remove others
- [ ] 3. Run cleanup_venvs.bat if applicable

## Phase 3: Ollama Model Optimization (Fix 11.5GiB Memory Error)
- [x] 1. Delete duplicate codellama models: ollama rm codellama:latest (keep :7b)
- [x] 2. Pull quantized efficient models:
  - Fastest: ollama pull llama3.2:1b
  - Balance: [x] llama3.2:3b  
  - Reasoning: qwen2.5:3b
- [x] 3. Update dashboard/rag.py model to quantized version ('llama3.2:3b')
- [ ] 4. Test RAG endpoint without memory error

## Phase 4: Additional Services (If Needed)
- [ ] Start Redis (required for Celery)
- [ ] Start Celery worker/beat
- [ ] Verify full stack (Django + Celery + RAG)

**Status: Phase 1 ✅ COMPLETE | Server running at http://localhost:8000 | Next: Ollama optimization**

## Phase 2: Environment Cleanup (Consolidate & Free Space)
- [ ] 1. Identify all .venv directories across workspace (use cleanup_venvs.bat?)
- [ ] 2. Keep only IndusVision_WorkBook, remove others
- [ ] 3. Run cleanup_venvs.bat if applicable

## Phase 3: Ollama Model Optimization (Fix 11.5GiB Memory Error)
- [ ] 1. Delete duplicate codellama models: ollama rm codellama:latest (keep :7b)
- [ ] 2. Pull quantized efficient models:
  - Fastest: ollama pull llama3.2:1b
  - Balance: llama3.2:3b  
  - Reasoning: qwen2.5:3b
- [ ] 3. Update dashboard/rag.py model to quantized version (e.g., 'llama3.2:3b-q4_0')
- [ ] 4. Test RAG endpoint without memory error

## Phase 4: Additional Services (If Needed)
- [ ] Start Redis (required for Celery)
- [ ] Start Celery worker/beat
- [ ] Verify full stack (Django + Celery + RAG)

**Status: Starting Phase 1**
