from datetime import datetime
import random
from celery import shared_task
from .models import MetricRecord


@shared_task(name='dashboard.update_heartbeat_metrics')
def update_heartbeat_metrics():
    """Minute-level heartbeat metrics for all IndusVision functional modules."""
    modules = ['annotation', 'automation', 'sandbox', 'spider', 'wrangling', 'sensor', 'camera']
    created_count = 0
    for m in modules:
        value = random.randint(0, 100)
        status = 'healthy' if value > 15 else 'idle'
        info = {
            'last_check': datetime.utcnow().isoformat() + 'Z',
            'build_minute': datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
            'msg': f'{m} telemetry updates',
        }
        MetricRecord.objects.create(module=m, value=value, status=status, info=info)
        created_count += 1
    return {'created': created_count, 'run': datetime.utcnow().isoformat() + 'Z'}


@shared_task(name='dashboard.rollup_active_summary')
def rollup_active_summary():
    """Compute a summary snapshot for dashboard display."""
    summary = []
    recent = MetricRecord.objects.order_by('-collected_at')[:7]
    for r in recent:
        summary.append({
            'module': r.module,
            'value': r.value,
            'status': r.status,
            'collected_at': r.collected_at.isoformat(),
        })
    return {'summary': summary, 'generated_at': datetime.utcnow().isoformat() + 'Z'}


@shared_task(name='dashboard.sync_source_files')
def sync_source_files():
    """Crawl the consolidated workspace and store file metadata for dashboard insights."""
    import os
    from django.utils.timezone import make_aware
    from pathlib import Path
    from .models import SourceFile

    repo_root = Path(__file__).resolve().parents[1]
    extensions = {
        '.py': 'py',
        '.html': 'html',
        '.htm': 'html',
        '.index': 'index',
        '.json': 'other',
        '.md': 'other',
    }

    updated = 0
    for p in repo_root.rglob('*'):
        if not p.is_file():
            continue
        if p.match('**/venv/**') or p.match('**/__pycache__/**') or p.match('**/.git/**'):
            continue

        ext = p.suffix.lower()
        if ext not in extensions:
            file_type = 'other'
        else:
            file_type = extensions[ext]

        try:
            mtime = datetime.utcfromtimestamp(p.stat().st_mtime)
            mtime = make_aware(mtime)
        except Exception:
            mtime = None

        line_count = 0
        try:
            if p.suffix.lower() in ['.py', '.html', '.htm', '.index']:
                with p.open('r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
        except Exception:
            line_count = 0

        sf, created = SourceFile.objects.update_or_create(
            path=str(p.relative_to(repo_root)),
            defaults={
                'file_type': file_type,
                'line_count': line_count,
                'last_updated': mtime,
                'size_bytes': p.stat().st_size,
                'is_dashboard_relevant': file_type in ['py', 'html', 'index'],
            },
        )
        updated += 1

    return {'updated': updated, 'run': datetime.utcnow().isoformat() + 'Z'}


@shared_task(name='dashboard.load_model_weights')
def load_model_weights():
    """Load and register available model weights from the yolo-training-project."""
    import os
    from pathlib import Path
    from .models import ModelWeights

    # Path to yolo-training-project
    yolo_path = Path(__file__).resolve().parents[1] / 'yolo-training-project'

    if not yolo_path.exists():
        return {'error': 'yolo-training-project not found', 'run': datetime.utcnow().isoformat() + 'Z'}

    # Look for model files (.pt, .pth, .onnx, etc.)
    model_extensions = ['.pt', '.pth', '.onnx', '.engine']
    loaded_count = 0

    for ext in model_extensions:
        for model_file in yolo_path.rglob(f'*{ext}'):
            try:
                model_name = model_file.stem
                model_path = str(model_file.relative_to(yolo_path.parent))

                # Try to determine model type and classes
                model_type = 'yolo'
                num_classes = 95  # Default for OCR, can be updated

                # Check if data.yaml exists for class info
                data_yaml = yolo_path / 'data.yaml'
                if data_yaml.exists():
                    try:
                        import yaml
                        with open(data_yaml, 'r') as f:
                            data = yaml.safe_load(f)
                        num_classes = len(data.get('names', []))
                    except:
                        pass

                # Update or create model record
                model, created = ModelWeights.objects.update_or_create(
                    name=model_name,
                    defaults={
                        'path': model_path,
                        'model_type': model_type,
                        'num_classes': num_classes,
                        'status': 'available',
                        'metadata': {
                            'file_size': model_file.stat().st_size,
                            'extension': ext,
                            'source': 'yolo-training-project'
                        }
                    }
                )
                if created:
                    loaded_count += 1

            except Exception as e:
                print(f"Error loading model {model_file}: {e}")

    return {'loaded': loaded_count, 'run': datetime.utcnow().isoformat() + 'Z'}


@shared_task(name='dashboard.run_model_detection')
def run_model_detection(model_name, image_path=None):
    """Run object detection using a loaded model."""
    from .models import ModelWeights
    import os
    from pathlib import Path

    try:
        model = ModelWeights.objects.get(name=model_name, status='available')
    except ModelWeights.DoesNotExist:
        return {'error': f'Model {model_name} not found or not available'}

    # Update last_used
    from django.utils import timezone
    model.last_used = timezone.now()
    model.save()

    # Path to model file
    model_full_path = Path(__file__).resolve().parents[1] / model.path

    if not model_full_path.exists():
        return {'error': f'Model file not found: {model_full_path}'}

    # For now, return mock detection results
    # In production, integrate with actual inference code
    detections = [
        {'class': 'object', 'confidence': 0.85, 'bbox': [100, 100, 200, 200]},
        {'class': 'text', 'confidence': 0.92, 'bbox': [50, 50, 150, 150]},
    ]

    return {
        'model': model_name,
        'detections': detections,
        'image_path': image_path,
        'run': datetime.utcnow().isoformat() + 'Z'
    }
