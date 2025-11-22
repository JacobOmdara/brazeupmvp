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


def load_model():  # getting model HuggingFace
    global MODEL
    if MODEL is None:
        # download model from HF
        model_path = hf_hub_download(
            repo_id="Awais-H/MetalSegmentation", filename="best_model.pth"
        )
        # @awais need you to share the model Architecture Unet class deff
        # MODEL = UNet(...)
        # MODEL.load_state_dict(torch.load(model_path, map_location=DEVICE))
        # MODEL.eval()
        MODEL = UNet(
            in_channels=3,  # RGB images
            out_channels=7,  # Background + 6 defect classes
            base_filters=64,
            depth=4,
        )

        # Load the trained weights
        checkpoint = torch.load(model_path, map_location=DEVICE)
        MODEL.load_state_dict(checkpoint["model_state_dict"])
        MODEL.to(DEVICE)
        MODEL.eval()

        print(f"Model loaded successfully on {DEVICE}")


def predict_defects(image_file):  #
    """
    Run ML interference on uploaded img

    Arguments:
        image_file: which is a FileStorage obj from Flask rq
    Returns:
        List of detected defects w bounding boxes
    """
    load_model()

    # reading the upload

    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_size = image.size

    # preprocess resize to what model expects
    image_resized = image.resize((256, 256), Image.BILINEAR)
    image_array = np.array(image_resized, dtype=np.float32) / 255.0

    # convert to PyTorch
    image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
    image_tensor = image_tensor.to(DEVICE)

    # run model inference (uncomment when model architecture ready)
    with torch.no_grad():
        output = MODEL(image_tensor)
        prediction = torch.argmax(output, dim=1)[0].cpu().numpy()

    # Convert segmentation mask to defect detections
    defects = process_segmentation_mask(prediction, original_size)

    return defects


def process_segmentation_mask(mask, original_size):
    """
    Convert segmentation mask to list of defects with bounding boxes

    Arguments:
        mask: numpy array of shape (256, 256) with class predictions
        original_size: tuple (width, height) of original image
    Returns:
        List of detected defects
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

            area = (rows.max() - rows.min() + 1) * (cols.max() - cols.min() + 1)

            defects.append(
                {
                    "type": DEFECT_CLASSES[class_id],
                    "confidence": float(component.sum() / area),
                    "bounding_box": bbox,
                }
            )

    return defects
