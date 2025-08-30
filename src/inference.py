import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMG_SIZE = 512
MODEL_PATH = "models/unet_epoch20.pth"
INPUT_IMAGE = "data/scenes/tiles/images/img_0001.png"
OUTPUT_MASK = "outputs/mask_0001.png"
OUTPUT_OVERLAY = "outputs/overlay_0001.png"

def get_model(num_classes=2):
    model = models.segmentation.deeplabv3_resnet50(pretrained=False)
    model.classifier[4] = nn.Conv2d(256, num_classes, kernel_size=1)
    return model

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

def predict(model, image_path):
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)
    model.eval()
    with torch.no_grad():
        output = model(input_tensor)["out"]
        pred = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()
    return np.array(image), pred

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    model = get_model(num_classes=2).to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    orig_img, mask = predict(model, INPUT_IMAGE)
    cv2.imwrite(OUTPUT_MASK, (mask * 255).astype(np.uint8))
    overlay = cv2.resize(orig_img, (mask.shape[1], mask.shape[0]))
    red_mask = np.zeros_like(overlay)
    red_mask[:, :, 0] = (mask * 255)
    blended = cv2.addWeighted(overlay, 0.7, red_mask, 0.3, 0)
    cv2.imwrite(OUTPUT_OVERLAY, blended)
    print(f"[OK] Çıktılar kaydedildi:\n - Maske: {OUTPUT_MASK}\n - Overlay: {OUTPUT_OVERLAY}")