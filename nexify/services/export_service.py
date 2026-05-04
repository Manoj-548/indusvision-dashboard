from django.http import HttpResponse
from ..models import NexifyProject, NexifyAnnotation


def generate_yolo_labels(project):
    "Generate normalized YOLO labels for project with class mapping."
    anns = NexifyAnnotation.objects.filter(
        image__folder__project=project,
        type="bbox"
    ).select_related('image', 'label_class')

    class_map = {c.name: i for i, c in enumerate(project.label_classes.all())}
    output = []

    for a in anns:
        pts = a.data
        if len(pts) < 2 or not a.image.width or not a.image.height:
            continue

        x1 = min(p['x'] for p in pts)
        y1 = min(p['y'] for p in pts)
        x2 = max(p['x'] for p in pts)
        y2 = max(p['y'] for p in pts)

        w = (x2 - x1) / a.image.width
        h = (y2 - y1) / a.image.height
        xc = ((x1 + x2) / 2) / a.image.width
        yc = ((y1 + y2) / 2) / a.image.height

        cls_id = class_map.get(a.label_class.name, 0)
        output.append(f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")

    return '\n'.join(output)


def export_dataset_response(project):
    "Return HttpResponse for export."
    labels = generate_yolo_labels(project)
    response = HttpResponse(labels, content_type="text/plain")
    response['Content-Disposition'] = f'attachment; filename="{project.name}_labels.txt"'
    return response

