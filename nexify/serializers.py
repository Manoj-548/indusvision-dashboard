from rest_framework import serializers
from .models import NexifyWorkspace, NexifyProject, NexifyImage, NexifyAnnotation, NexifyLabelClass

class LabelClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = NexifyLabelClass
        fields = '__all__'

class AnnotationSerializer(serializers.ModelSerializer):
    label_class = LabelClassSerializer(read_only=True)
    class Meta:
        model = NexifyAnnotation
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True, read_only=True)
    class Meta:
        model
