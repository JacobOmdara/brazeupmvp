import torch
import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
import io
from model import UNet
# utilizing pytorch (what Awais used) n downloading models from HuggingFace

MODEL = None  # placeholder for model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DEFECT_CLASSES = {
    0: "background",
    1: "crazing",
    2: "inclusion",
    3: "patches",
    4: "pitted_surface",
    5: "rolled-in_scale",
    6: "scratches",
}

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)  # using gpu otherwise use cpu


MODEL_IS_REAL = False  # Track if we have real trained weights

def load_model():  # getting model HuggingFace
    global MODEL, MODEL_IS_REAL
    if MODEL is None:
        try:
            # Try to download from HF (Awais's repo)
            print("Attempting to download model from Awais-H/MetalSegmentation...")
            model_path = hf_hub_download(
                repo_id="Awais-H/MetalSegmentation", filename="best_model.pth"
            )
            print(f"Model downloaded to: {model_path}")
            
            checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=False)
            print(f"Checkpoint type: {type(checkpoint)}")
            if isinstance(checkpoint, dict):
                print(f"Checkpoint keys: {checkpoint.keys()}")
            
            MODEL = UNet(
                in_channels=3,
                out_channels=7,
                base_filters=64,
                depth=4,
            )
            
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                MODEL.load_state_dict(checkpoint["model_state_dict"])
                print("Loaded model_state_dict from checkpoint")
            else:
                MODEL.load_state_dict(checkpoint)
                print("Loaded checkpoint directly as state_dict")
                
            MODEL.to(DEVICE)
            MODEL.eval()
            MODEL_IS_REAL = True
            print(f"SUCCESS: Real model loaded from HuggingFace on {DEVICE}")

        except Exception as e:
            # Fallback: create a MOCK model for testing
            import traceback
            print(f"ERROR: HF download failed: {e}")
            print(traceback.format_exc())
            print("WARNING: Using MOCK model - predictions will be random!")
            MODEL = UNet(
                in_channels=3,
                out_channels=7,
                base_filters=64,
                depth=4,
            )
            MODEL.to(DEVICE)
            MODEL.eval()
            MODEL_IS_REAL = False
            print(f"Mock model created on {DEVICE}")


def predict_defects(image_bytes):  #
    """
    Run ML interference on uploaded img

    Arguments:
        image_bytes: raw bytes of uploaded img
    Returns:
        List of detected defects w bounding boxes and true model confidence
    """
    load_model()

    # reading the upload

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_size = image.size

    # preprocess resize to what model expects
    image_resized = image.resize((256, 256), Image.BILINEAR)
    image_array = np.array(image_resized, dtype=np.float32) / 255.0

    # convert to PyTorch
    image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
    image_tensor = image_tensor.to(DEVICE)

    # run model inference
    with torch.no_grad():
        output = MODEL(image_tensor)
        
        # Apply softmax to get true probabilities
        probabilities = torch.softmax(output, dim=1)[0]  # Shape: (7, 256, 256)
        
        # Get predicted class per pixel
        prediction = torch.argmax(output, dim=1)[0].cpu().numpy()
        
        # Get confidence (max probability) per pixel
        confidence_map = probabilities.max(dim=0)[0].cpu().numpy()  # Shape: (256, 256)
        
        # Debug: Log prediction statistics
        unique, counts = np.unique(prediction, return_counts=True)
        class_distribution = dict(zip([DEFECT_CLASSES.get(int(u), f"unknown_{u}") for u in unique], counts.tolist()))
        print(f"Prediction stats - Using real model: {MODEL_IS_REAL}")
        print(f"Class distribution: {class_distribution}")
        print(f"Total pixels: {prediction.size}, Non-background: {(prediction > 0).sum()}")

    # Convert segmentation mask to defect detections with true confidence
    defects = process_segmentation_mask(prediction, confidence_map, original_size)

    return defects


def process_segmentation_mask(mask, confidence_map, original_size):
    """
    Convert segmentation mask to list of defects with bounding boxes and true model confidence

    Arguments:
        mask: numpy array of shape (256, 256) with class predictions
        confidence_map: numpy array of shape (256, 256) with softmax probabilities
        original_size: tuple (width, height) of original image
    Returns:
        List of detected defects with true model confidence scores
    """
    from scipy import ndimage

    defects = []
    scale_x, scale_y = original_size[0] / 256, original_size[1] / 256

    for class_id in range(1, 7):
        class_mask = (mask == class_id).astype(np.uint8)
        if class_mask.sum() == 0:
            continue

        labeled_mask, num_features = ndimage.label(class_mask)

        for i in range(1, num_features + 1):
            component = labeled_mask == i
            rows, cols = np.where(component)

            bbox = [
                int(cols.min() * scale_x),
                int(rows.min() * scale_y),
                int(cols.max() * scale_x),
                int(rows.max() * scale_y),
            ]

            # Calculate TRUE model confidence: average softmax probability for this region
            region_confidence = float(confidence_map[component].mean())

            defects.append(
                {
                    "type": DEFECT_CLASSES[class_id],
                    "confidence": round(region_confidence * 100, 1),  # As percentage
                    "bounding_box": bbox,
                }
            )

    return defects
