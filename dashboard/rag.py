"""
IndusVision RAG Engine - Enhanced with Modern LLM Features
Powered by LlamaIndex, Ollama, and ChromaDB
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from dashboard.models import KnowledgeEntry, LLMConfig, SourceFile, FeedbackMemory
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank
from chromadb import PersistentClient

logger = logging.getLogger(__name__)

# Configuration
CHROMA_DB_PATH = getattr(settings, 'CHROMA_DB_PATH', 'chroma_db')
DEFAULT_EMBED_MODEL = getattr(settings, 'DEFAULT_EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
DEFAULT_RAG_MODEL = getattr(settings, 'DEFAULT_RAG_MODEL', 'llama3.2:1b')
DEFAULT_RAG_BASE_URL = getattr(settings, 'DEFAULT_RAG_BASE_URL', 'http://localhost:11434')

# Global resources
embed_model = None
chroma_client = None


def get_embed_model(model_name: str = DEFAULT_EMBED_MODEL):
    """Get or create embedding model with caching"""
    global embed_model
    if embed_model is None:
        try:
            embed_model = HuggingFaceEmbedding(
                model_name=model_name,
                cache_folder=os.path.join(settings.BASE_DIR, '.cache', 'embeddings')
            )
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Using default.")
            embed_model = HuggingFaceEmbedding(model_name=DEFAULT_EMBED_MODEL)
    return embed_model


def get_chroma_client():
    """Get or create ChromaDB client with caching"""
    global chroma_client
    if chroma_client is None:
        chroma_client = PersistentClient(path=CHROMA_DB_PATH)
    return chroma_client


def get_llm(config: Optional[LLMConfig] = None) -> Ollama:
    """Get LLM instance with configuration"""
    cfg = config
    if cfg is None:
        try:
            cfg = LLMConfig.objects.filter(is_active=True).order_by('-is_default', '-created_at').first()
        except Exception:
            pass
    
    model_name = cfg.model_name if cfg else os.environ.get('RAG_MODEL_NAME', DEFAULT_RAG_MODEL)
    base_url = cfg.base_url if cfg else os.environ.get('RAG_BASE_URL', DEFAULT_RAG_BASE_URL)
    timeout = cfg.request_timeout if cfg else float(os.environ.get('RAG_REQUEST_TIMEOUT', '120.0'))
    num_ctx = cfg.num_ctx if cfg else int(os.environ.get('RAG_NUM_CTX', '4096'))
    num_predict = cfg.num_predict if cfg else int(os.environ.get('RAG_NUM_PREDICT', '512'))
    temperature = cfg.temperature if cfg else float(os.environ.get('RAG_TEMPERATURE', '0.7'))

    return Ollama(
        model=model_name,
        base_url=base_url,
        timeout=timeout,
        num_ctx=num_ctx,
        additional_kwargs={"num_predict": num_predict},
        temperature=temperature,
    )


def get_index(knowledge_type: Optional[str] = None, force_refresh: bool = False):
    """Get or create vector index with optional filtering by knowledge type"""
    from llama_index.core import load_index_from_storage
    
    chroma_client = get_chroma_client()
    collection_name = knowledge_type or "knowledge"
    
    try:
        chroma_collection = chroma_client.get_or_create_collection(collection_name)
    except Exception:
        chroma_collection = chroma_client.create_collection(collection_name)
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Build documents from knowledge entries
    qs = KnowledgeEntry.objects.all()
    if knowledge_type:
        qs = qs.filter(knowledge_type=knowledge_type)
    
    docs = []
    for ke in qs:
        doc = Document(
            text=ke.content_preview or "",
            metadata={
                "title": ke.title,
                "path": ke.source_file.path if ke.source_file else "",
                "type": ke.knowledge_type,
                "entry_id": str(ke.id)
            }
        )
        docs.append(doc)
    
    if docs:
        embed = get_embed_model()
        index = VectorStoreIndex.from_documents(
            docs, 
            storage_context=storage_context, 
            embed_model=embed
        )
    else:
        try:
            index = load_index_from_storage(storage_context)
        except:
            index = VectorStoreIndex.from_documents([], storage_context=storage_context)
    
    return index


# ============ API ENDPOINTS ============

@csrf_exempt
@require_http_methods(["POST"])
def rag_agent(request):
    """Main RAG agent endpoint - enhanced with multiple retrieval strategies"""
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}
    
    query = body.get('query', body.get('prompt', ''))
    knowledge_type = body.get('type')  # doc, script, config
    use_rerank = body.get('rerank', True)
    top_k = body.get('top_k', 3)
    stream = body.get('stream', False)
    
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)
    
    # Check for knowledge
    total_count = KnowledgeEntry.objects.aggregate(total=Count('id'))['total']
    if total_count == 0:
        return JsonResponse({
            'response': 'No knowledge indexed. Run `python consolidate_all.py` to scan codebase.',
            'sources': []
        })
    
    try:
        # Get index and query engine
        index = get_index(knowledge_type=knowledge_type)
        llm = get_llm()
        
        # Configure retriever
        retriever = index.as_retriever(similarity_top_k=top_k * 2)
        
        # Add reranking if enabled
        if use_rerank:
            try:
                rerank = SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L6-v2", top_n=top_k)
                query_engine = index.as_query_engine(
                    llm=llm,
                    retriever=retriever,
                    node_postprocessors=[rerank]
                )
            except Exception:
                query_engine = index.as_query_engine(llm=llm, retriever=retriever)
        else:
            query_engine = index.as_query_engine(llm=llm, retriever=retriever)
        
        # Execute query
        response = query_engine.query(query)
        
        # Extract sources
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes[:top_k]:
                sources.append({
                    "title": node.node.metadata.get("title", "Unknown"),
                    "type": node.node.metadata.get("type", "doc"),
                    "score": node.score if hasattr(node, 'score') else None
                })
        
        return JsonResponse({
            'response': str(response),
            'sources': sources,
            'model': llm.model,
            'stream': stream
        })
    
    except Exception as e:
        logger.error(f"RAG agent error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def rag_agent_stream(request):
    """Streaming RAG agent for real-time responses"""
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}
    
    query = body.get('query', body.get('prompt', ''))
    knowledge_type = body.get('type')
    top_k = body.get('top_k', 3)
    
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)
    
    total_count = KnowledgeEntry.objects.aggregate(total=Count('id'))['total']
    if total_count == 0:
        return JsonResponse({
            'response': 'No knowledge indexed. Run `python consolidate_all.py` to scan codebase.',
            'sources': []
        })
    
    def generate():
        try:
            index = get_index(knowledge_type=knowledge_type)
            llm = get_llm()
            retriever = index.as_retriever(similarity_top_k=top_k)
            query_engine = index.as_query_engine(llm=llm, retriever=retriever)
            
            response = query_engine.query(query)
            
            # Stream response in chunks
            response_text = str(response)
            chunk_size = 50
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Send sources at end
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes[:top_k]:
                    sources.append({
                        "title": node.node.metadata.get("title", "Unknown"),
                        "type": node.node.metadata.get("type", "doc")
                    })
            yield f"data: {json.dumps({'sources': sources, 'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingHttpResponse(generate(), content_type='text/event-stream')


@require_http_methods(["GET"])
def rag_status(request):
    """Get RAG system status"""
    try:
        chroma = get_chroma_client()
        collections = chroma.list_collections()
        
        # Count knowledge entries
        total_entries = KnowledgeEntry.objects.count()
        by_type = list(KnowledgeEntry.objects.values('knowledge_type').annotate(count=Count('id')))
        
        # Get available LLM configs
        llm_configs = list(LLMConfig.objects.values(
            'id', 'name', 'model_name', 'base_url', 'is_active', 'is_default'
        ))
        
        return JsonResponse({
            'status': 'ok',
            'embed_model': DEFAULT_EMBED_MODEL,
            'llm_model': DEFAULT_RAG_MODEL,
            'chroma_collections': [c.name for c in collections],
            'total_entries': total_entries,
            'entries_by_type': by_type,
            'llm_configs': llm_configs,
            'embedding_status': 'loaded' if embed_model else 'not_loaded'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def rag_knowledge(request):
    """List indexed knowledge"""
    knowledge_type = request.GET.get('type')
    limit = int(request.GET.get('limit', 50))
    
    qs = KnowledgeEntry.objects.all().order_by('-created_at')
    if knowledge_type:
        qs = qs.filter(knowledge_type=knowledge_type)
    
    entries = list(qs.values(
        'id', 'title', 'knowledge_type', 'content_preview', 'created_at'
    )[:limit])
    
    return JsonResponse({'entries': entries, 'count': len(entries)})


@require_http_methods(["POST"])
def rag_index_knowledge(request):
    """Manually trigger knowledge indexing"""
    try:
        # This would ideally run in background, but for now return status
        count = KnowledgeEntry.objects.count()
        return JsonResponse({
            'status': 'indexed',
            'total_entries': count,
            'message': f'Already have {count} entries. Use consolidate_all.py for full reindex.'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def rag_feedback(request):
    """Store feedback for RAG responses to improve future results"""
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}
    
    prompt = body.get('prompt', '')
    response = body.get('response', '')
    improved = body.get('improved', False)
    
    if not prompt or not response:
        return JsonResponse({'error': 'Missing prompt or response'}, status=400)
    
    try:
        feedback = FeedbackMemory.objects.create(
            prompt=prompt,
            response=response,
            improved=improved
        )
        return JsonResponse({
            'status': 'saved',
            'id': feedback.id,
            'improved': improved
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET", "POST"])
def rag_config(request):
    """Manage LLM configurations"""
    if request.method == "GET":
        configs = list(LLMConfig.objects.values(
            'id', 'name', 'model_name', 'base_url', 'request_timeout',
            'num_ctx', 'num_predict', 'temperature', 'is_active', 'is_default'
        ))
        return JsonResponse({'configs': configs})
    
    # POST - create or update config
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}
    
    config_id = body.get('id')
    name = body.get('name', 'new-config')
    model_name = body.get('model_name', DEFAULT_RAG_MODEL)
    base_url = body.get('base_url', DEFAULT_RAG_BASE_URL)
    request_timeout = float(body.get('request_timeout', 120.0))
    num_ctx = int(body.get('num_ctx', 4096))
    num_predict = int(body.get('num_predict', 512))
    temperature = float(body.get('temperature', 0.7))
    is_active = body.get('is_active', False)
    is_default = body.get('is_default', False)
    
    try:
        if config_id:
            config = LLMConfig.objects.get(id=config_id)
            config.name = name
            config.model_name = model_name
            config.base_url = base_url
            config.request_timeout = request_timeout
            config.num_ctx = num_ctx
            config.num_predict = num_predict
            config.temperature = temperature
            config.is_active = is_active
            config.is_default = is_default
            config.save()
        else:
            config = LLMConfig.objects.create(
                name=name,
                model_name=model_name,
                base_url=base_url,
                request_timeout=request_timeout,
                num_ctx=num_ctx,
                num_predict=num_predict,
                temperature=temperature,
                is_active=is_active,
                is_default=is_default
            )
        
        return JsonResponse({
            'status': 'saved',
            'config': {
                'id': config.id,
                'name': config.name,
                'model_name': config.model_name
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def rag_models(request):
    """List available Ollama models"""
    import requests
    
    try:
        base_url = os.environ.get('RAG_BASE_URL', DEFAULT_RAG_BASE_URL)
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        models = resp.json().get('models', [])
        return JsonResponse({
            'models': [
                {
                    'name': m.get('name'),
                    'size': m.get('size'),
                    'modified': m.get('modified_at')
                }
                for m in models
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============ LEGACY SUPPORT ============

def rag_agent_legacy(request):
    """Legacy endpoint for backward compatibility"""
    return rag_agent(request)
 