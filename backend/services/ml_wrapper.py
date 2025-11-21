import torch 
import numpy as np 
from PIL import Image
from huggingface_hub import hf_hub_download
import io 
# utilizing pytorch (what Awais used) n downloading models from HuggingFace

MODEL = None # placeholder for model
DEVICE = torch.device ('cuda' if torch.cuda.is_available() else 'cpu') #using gpu otherwise use cpu
def load_model(): # getting model HuggingFace
    global MODEL
    if MODEL is None:
        # download model from HF
        model_path = hf_hub_download(
            repo_id = "Awais-H/MetalSegmentation",
            filename = "best_model.pth"
        )

        # @awais need you to share the model Architecture Unet class deff
        # MODEL = UNet(...)  
        # MODEL.load_state_dict(torch.load(model_path, map_location=DEVICE))
        # MODEL.eval() 
        pass
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
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    original_size = image.size
    
    # preprocess resize to what model expects
    image_resized = image.resize((256, 256), Image.BILINEAR)
    image_array = np.array(image_resized, dtype=np.float32) / 255.0
    
    # convert to PyTorch 
    image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
    image_tensor = image_tensor.to(DEVICE)
    
    # run model inference (uncomment when model architecture ready)
    # with torch.no_grad():
    #     output = MODEL(image_tensor)
    #     prediction = torch.argmax(output, dim=1)[0].cpu().numpy()

    # mock data for now 
    return [
        {
            "type": "crazing",
            "confidence": 0.92,
            "bounding_box": [10, 10, 100, 100],
            "severity": 0.8
        }
    ]