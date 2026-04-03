from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from dashboard.models import MetricRecord, SourceFile, ModelWeights
from dashboard.tasks import load_model_weights, run_model_detection


class ModelWeightsViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing model weights and running detections."""
    queryset = ModelWeights.objects.all()
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
        models = ModelWeights.objects.order_by('-last_used')
        data = [self.get_serializer_data(m) for m in models]
        return Response({
            'count': len(data),
            'models': data
        })
    
    def retrieve(self, request, name=None):
        """Retrieve a specific model by name."""
        try:
            model = ModelWeights.objects.get(name=name)
            return Response(self.get_serializer_data(model))
        except ModelWeights.DoesNotExist:
            return Response({'error': f'Model {name} not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def scan_models(self, request):
        """Scan and load available models from yolo-training-project."""
        result = load_model_weights.delay()
        return Response({
            'task_id': result.id,
            'status': 'scanning',
            'message': 'Model scanning initiated in background'
        })
    
    @action(detail=True, methods=['post'])
    def run_detection(self, request, name=None):
        """Run detection with a specific model."""
        try:
            model = ModelWeights.objects.get(name=name)
        except ModelWeights.DoesNotExist:
            return Response({'error': f'Model {name} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        image_path = request.data.get('image_path')
        if not image_path:
            return Response({'error': 'image_path is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update last_used
        model.last_used = timezone.now()
        model.save()
        
        # Run detection asynchronously
        result = run_model_detection.delay(name, image_path)
        
        return Response({
            'task_id': result.id,
            'model': name,
            'image_path': image_path,
            'status': 'processing',
            'message': 'Detection started'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get model statistics."""
        total_models = ModelWeights.objects.count()
        available_models = ModelWeights.objects.filter(status='available').count()
        avg_accuracy = ModelWeights.objects.filter(accuracy__gt=0).values_list('accuracy', flat=True)
        avg_acc = sum(avg_accuracy) / len(avg_accuracy) if avg_accuracy else 0
        
        return Response({
            'total_models': total_models,
            'available_models': available_models,
            'average_accuracy': float(avg_acc),
            'model_types': list(set(ModelWeights.objects.values_list('model_type', flat=True))),
        })


class MetricRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for querying metric records."""
    queryset = MetricRecord.objects.all().order_by('-collected_at')
    
    def get_serializer_data(self, obj):
        return {
            'id': obj.id,
            'module': obj.module,
            'value': obj.value,
            'status': obj.status,
            'info': obj.info,
            'collected_at': obj.collected_at.isoformat(),
        }
    
    def list(self, request):
        """List recent metrics."""
        module = request.query_params.get('module')
        limit = int(request.query_params.get('limit', 25))
        
        qs = MetricRecord.objects.order_by('-collected_at')[:limit]
        if module:
            qs = qs.filter(module=module)
        
        data = [self.get_serializer_data(m) for m in qs]
        return Response({
            'count': len(data),
            'metrics': data
        })


class SourceFileViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for source file inventory."""
    queryset = SourceFile.objects.all().order_by('-last_updated')
    
    def get_serializer_data(self, obj):
        return {
            'path': obj.path,
            'file_type': obj.file_type,
            'components': obj.components,
            'line_count': obj.line_count,
            'size_bytes': obj.size_bytes,
            'last_updated': obj.last_updated.isoformat() if obj.last_updated else None,
            'is_dashboard_relevant': obj.is_dashboard_relevant,
        }
    
    def list(self, request):
        """List source files with filtering."""
        file_type = request.query_params.get('file_type')
        limit = int(request.query_params.get('limit', 50))
        
        qs = SourceFile.objects.order_by('-last_updated')[:limit]
        if file_type:
            qs = qs.filter(file_type=file_type)
        
        data = [self.get_serializer_data(f) for f in qs]
        total = SourceFile.objects.count()
        
        return Response({
            'total_files': total,
            'count': len(data),
            'files': data
        })

