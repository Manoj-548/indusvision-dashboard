from django.urls import path
from . import views
from dashboard import rag

urlpatterns = [
    path("sensor/", views.api_sensor),
    path("projects/", views.api_projects),
    path("knowledge/", views.api_knowledge),
    path("ai-suggest/", views.ai_suggest),
    # RAG Engine endpoints
    path("rag/agent/", rag.rag_agent),
    path("rag/agent/stream/", rag.rag_agent_stream),
    path("rag/status/", rag.rag_status),
    path("rag/knowledge/", rag.rag_knowledge),
    path("rag/index/", rag.rag_index_knowledge),
    path("rag/feedback/", rag.rag_feedback),
    path("rag/config/", rag.rag_config),
    path("rag/models/", rag.rag_models),
]
