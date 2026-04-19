import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from dashboard.models import KnowledgeEntry, LLMConfig
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import QueryEngineTool
from chromadb import PersistentClient

chroma_db_path = "chroma_db"

embed_model = None

def get_embed_model():
    global embed_model
    if embed_model is None:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embed_model

DEFAULT_RAG_MODEL = 'llama3.2:1b'
DEFAULT_RAG_BASE_URL = 'http://localhost:11434'
DEFAULT_RAG_REQUEST_TIMEOUT = 120.0
DEFAULT_RAG_NUM_CTX = 4096
DEFAULT_RAG_NUM_PREDICT = 512


def get_llm():
    config = None
    try:
        config = LLMConfig.objects.filter(is_active=True).order_by('-created_at').first()
    except Exception:
        config = None

    model_name = os.environ.get('RAG_MODEL_NAME', config.model_name if config else DEFAULT_RAG_MODEL)
    base_url = os.environ.get('RAG_BASE_URL', config.base_url if config else DEFAULT_RAG_BASE_URL)
    request_timeout = float(os.environ.get('RAG_REQUEST_TIMEOUT', getattr(config, 'request_timeout', DEFAULT_RAG_REQUEST_TIMEOUT)))
    num_ctx = int(os.environ.get('RAG_NUM_CTX', getattr(config, 'num_ctx', DEFAULT_RAG_NUM_CTX)))
    num_predict = int(os.environ.get('RAG_NUM_PREDICT', getattr(config, 'num_predict', DEFAULT_RAG_NUM_PREDICT)))

    return Ollama(
        model=model_name,
        base_url=base_url,
        request_timeout=request_timeout,
        num_ctx=num_ctx,
        num_predict=num_predict,
    )


def get_index():
    from chromadb import PersistentClient
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
    
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, embed_model=get_embed_model())
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
        query_engine = get_index().as_query_engine(llm=get_llm())
        response = query_engine.query(query)
        return JsonResponse({'response': str(response)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

