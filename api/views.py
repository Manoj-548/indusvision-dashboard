from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from dashboard.models import SourceFile, KnowledgeEntry
# from dashboard.tasks import load_model_weights, run_model_detection


class ModelWeightsViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing model weights and running detections."""
    queryset = []  # ModelWeights not available
    lookup_field = 'name'
    
    def get_serializer_data(self, obj):
        return {
            'name': obj.name,
            'model_type': obj.model_type,
            'path': obj.path,
            'num_classes': obj.num_classes,
            'accuracy': obj.accuracy,
            'status': obj.status,
            'trained_at': obj.trained_at.isoformat() if obj.trained_at else None,
            'last_used': obj.last_used.isoformat() if obj.last_used else None,
            'metadata': obj.metadata,
        }
    
    def list(self, request):
        """List all available model weights."""
        models = []
        data = [self.get_serializer_data(m) for m in models]
        return Response({
            'count': len(data),
            'models': data
        })
    
    @action(detail=False, methods=['post'])
    def scan_models(self, request):
        """Scan and load available models."""
        return Response({'status': 'scan initiated'})
    
    @action(detail=True, methods=['post'])
    def run_detection(self, request, name=None):
        """Mock detection."""
        return Response({'status': 'detection started', 'model': name})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get model statistics."""
        total_models = 0
        return Response({'total': total_models})


class MetricRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for querying metric records."""
    queryset = []  # MetricRecord not available
    
    def list(self, request):
        """List recent metrics."""
        qs = self.queryset[:25]
        data = [{'module': m.module, 'value': m.value, 'collected_at': m.collected_at.isoformat()} for m in qs]
        return Response(data)


class SourceFileViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for source file inventory."""
    queryset = SourceFile.objects.all().order_by('-last_updated')
    
    def list(self, request):
        """List source files."""
        qs = self.queryset[:50]
        data = [{'path': f.path, 'file_type': f.file_type, 'line_count': f.line_count} for f in qs]
        return Response(data)

class KnowledgeViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for KnowledgeEntry."""
    queryset = KnowledgeEntry.objects.all().order_by('-created_at')
    
    def list(self, request):
        """List knowledge entries."""
        qs = self.queryset[:50]
        data = [{
            'id': k.id,
            'title': k.title,
            'type': k.knowledge_type,
            'source_path': k.source_file.path,
            'preview': k.content_preview[:200],
            'consolidated_at': k.consolidated_at.isoformat() if k.consolidated_at else None
        } for k in qs]
        return Response(data)

class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for scripts (SourceFile filter)."""
    queryset = SourceFile.objects.filter(file_type='script').order_by('-last_updated')
    
    def list(self, request):
        """List scripts."""
        qs = self.queryset[:30]
        data = [{'path': s.path, 'line_count': s.line_count, 'last_updated': s.last_updated.isoformat() if s.last_updated else None} for s in qs]
        return Response(data)

