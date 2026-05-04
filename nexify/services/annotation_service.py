from django.contrib.auth.models import User
from ..models import NexifyAnnotation, NexifyImage, NexifyLabelClass

def create_annotation(image_id, annotator, type_, data, label_class_id=None, confidence=1.0):
    "Create new annotation."
    annotation = NexifyAnnotation.objects.create(
        image_id=image_id,
        annotator=annotator,
        type=type_,
        data=data,
        confidence=confidence,
    )
    if label_class_id:
        annotation.label_class_id = label_class_id
        annotation.save(update_fields=['label_class'])
    return annotation

def list_annotations_for_image(image_id):
    "List annotations for image with prefetch."
    return NexifyAnnotation.objects.filter(image_id=image_id).select_related('label_class', 'annotator')

def review_annotation(annotation_id, reviewer):
    "Approve annotation."
    annotation = NexifyAnnotation.objects.get(id=annotation_id)
    annotation.is_approved = True
    annotation.save(update_fields=['is_approved'])
    return annotation

