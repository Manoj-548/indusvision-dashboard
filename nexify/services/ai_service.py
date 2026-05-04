# AI Services (SAM, Auto-Annotation)

from ..sam_utils import generate_sam_polygon

def sam_predict(image_path, x=None, y=None):
    "SAM polygon from click point."
    if x is None or y is None:
        return {"error": "Provide x,y click point"}
    polygon = generate_sam_polygon(image_path, x, y)
    ann_data = [{"x": p["x"], "y": p["y"]} for p in polygon]
    return {"type": "polygon", "data": ann_data, "polygon": polygon}


def auto_annotate_image(image_id, model='sam', x=None, y=None):
    "Auto annotate with SAM click."
    from ..models import NexifyImage
    image = NexifyImage.objects.get(id=image_id)
    result = sam_predict(image.file.path, x=x, y=y)
    return result
