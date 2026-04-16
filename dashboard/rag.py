import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from dashboard.models import KnowledgeEntry
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import QueryEngineTool
from chromadb import PersistentClient

chroma_db_path = "chroma_db"

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Ollama(model="qwen2.5-coder:3b", base_url="http://localhost:11434", request_timeout=120.0, num_ctx=4096, num_predict=512)  # qwen2.5-coder:3b BEST coder model

def get_index():
    chroma_client = PersistentClient(path=chroma_db_path)
    chroma_collection = chroma_client.get_or_create_collection("knowledge")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    docs = []
    for ke in KnowledgeEntry.objects.all():
        doc = Document(
            text=ke.content_preview or "",
            metadata={"title": ke.title, "path": ke.source_file.path, "type": ke.knowledge_type}
        )
        docs.append(doc)
    
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, embed_model=embed_model)
    return index

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["POST"])
def rag_agent(request):
    query = request.POST.get('query', '')

    if not query:
        return JsonResponse({'error': 'No query'}, status=400)

    from django.db.models import Count
    if KnowledgeEntry.objects.aggregate(total=Count('id'))['total'] == 0:
        return JsonResponse({'response': 'No knowledge indexed yet. Run `python consolidate_all.py` to scan codebase.'})

    
    try:
        query_engine = get_index().as_query_engine(llm=llm)
        response = query_engine.query(query)
        return JsonResponse({'response': str(response)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

