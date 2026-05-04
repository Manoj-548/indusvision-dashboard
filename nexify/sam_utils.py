"""
SAM (Segment Anything Model) Utils for Nexify Auto-Annotation
"""
import os
import numpy as np
import cv2
from django.conf import settings

# SAM path relative to BASE_DIR
SAM_MODEL_PATH = os.path.join(settings.BASE_DIR, "sam_models", "sam_vit_h_4b8939.pth")

# Global predictor instance
_predictor = None


def get_sam_predictor():
    """Initialize and return SAM predictor (lazy loading)"""
    global _predictor
    
    if _predictor is None:
        try:
            from segment_anything import sam_model_registry, SamPredictor
            
            # Load SAM model
            sam = sam_model_registry["vit_h"](checkpoint=SAM_MODEL_PATH)
            sam.to(device="cpu")  # Use "cuda" if GPU available
            
            _predictor = SamPredictor(sam)
            print("SAM model loaded successfully")
        except Exception as e:
            print(f"Error loading SAM model: {e}")
            raise
    
    return _predictor


def generate_sam_polygon(image_path, x, y):
    """
    Generate polygon mask using SAM from a click point
    
    Args:
        image_path: Path to the image file
        x: X coordinate of click point
        y: Y coordinate of click point
    
    Returns:
        List of {x, y} points representing the polygon contour
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Get predictor
    predictor = get_sam_predictor()
    
    # Set image for prediction
    predictor.set_image(image)
    
    # Create input point and label
    input_point = np.array([[int(x), int(y)]])
    input_label = np.array([1])  # 1 = foreground
    
    # Get masks with multimask output
    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    
    # Select best mask based on scores
    best_idx = np.argmax(scores)
    mask = masks[best_idx]
    
    # Find contours in the mask
    contours, _ = cv2.findContours(
        mask.astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    polygon = []
    if contours:
        # Get largest contour
        cnt = max(contours, key=cv2.contourArea)
        
        # Simplify contour to reduce points
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # Convert to list of {x, y} dicts
        for p in approx:
            polygon.append({
                "x": int(p[0][0]),
                "y": int(p[0][1])
            })
    
    return polygon


def generate_sam_mask(image_path, x, y):
    """
    Generate binary mask using SAM from a click point
    
    Args:
        image_path: Path to the image file
        x: X coordinate of click point
        y: Y coordinate of click point
    
    Returns:
        Binary mask as numpy array
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    predictor = get_sam_predictor()
    predictor.set_image(image)
    
    input_point = np.array([[int(x), int(y)]])
    input_label = np.array([1])
    
    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    
    best_idx = np.argmax(scores)
    return masks[best_idx]
