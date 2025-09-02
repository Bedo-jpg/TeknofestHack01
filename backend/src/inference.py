import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMG_SIZE = 512
MODEL_PATH = "models/unet_epoch20.pth"  # Model path kontrol et!

def get_model(num_classes=2):
    model = models.segmentation.deeplabv3_resnet50(pretrained=False)
    model.classifier[4] = nn.Conv2d(256, num_classes, kernel_size=1)
    return model

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

def predict_image(image_path):
    """FastAPI için düzenlenmiş predict fonksiyonu"""
    # Modeli yükle
    model = get_model(num_classes=2).to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    
    # Tahmin yap
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)
    
    model.eval()
    with torch.no_grad():
        output = model(input_tensor)["out"]
        pred = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()
    
    # Çıktıları kaydet
    os.makedirs("outputs", exist_ok=True)
    filename = os.path.basename(image_path).split('.')[0]
    
    mask_path = f"outputs/{filename}_mask.png"
    overlay_path = f"outputs/{filename}_overlay.png"
    
    # Görüntüleri kaydet
    orig_img = np.array(image)
    cv2.imwrite(mask_path, (pred * 255).astype(np.uint8))
    
    # Overlay oluştur
    overlay = cv2.resize(orig_img, (pred.shape[1], pred.shape[0]))
    red_mask = np.zeros_like(overlay)
    red_mask[:, :, 0] = (pred * 255)
    blended = cv2.addWeighted(overlay, 0.7, red_mask, 0.3, 0)
    cv2.imwrite(overlay_path, blended)
    
    return mask_path, overlay_path

# Eski main kısmını kaldır (FastAPI kullanacaksın)