import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from src.dataset import BuildingDamageDataset
from torchvision import models
import albumentations as A
from albumentations.pytorch import ToTensorV2
import os

# ======================
# 1. Hyperparameters
# ======================
BATCH_SIZE = 4
EPOCHS = 20
LR = 1e-4
IMG_SIZE = 512
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ======================
# 2. Data Augmentation
# ======================
train_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    ToTensorV2()
])

val_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    ToTensorV2()
])

# ======================
# 3. Dataset & DataLoader
# ======================
dataset = BuildingDamageDataset(
    image_dir="data/scenes/tiles/images",
    mask_dir="data/scenes/tiles/masks",
    transform=train_transform
)

val_size = int(0.2 * len(dataset))
train_size = len(dataset) - val_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
val_dataset.dataset.transform = val_transform

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ======================
# 4. Model (DeepLabV3)
# ======================
model = models.segmentation.deeplabv3_resnet50(pretrained=True)
model.classifier[4] = nn.Conv2d(256, 2, kernel_size=1)
model = model.to(DEVICE)

# ======================
# 5. Loss & Optimizer
# ======================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ======================
# 6. Training & Validation
# ======================
def train_one_epoch(loader, model, optimizer, criterion):
    model.train()
    epoch_loss = 0
    for imgs, masks in loader:
        imgs, masks = imgs.to(DEVICE), masks.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(imgs)['out']
        loss = criterion(outputs, masks)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    return epoch_loss / len(loader)

def evaluate(loader, model, criterion):
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for imgs, masks in loader:
            imgs, masks = imgs.to(DEVICE), masks.to(DEVICE)
            outputs = model(imgs)['out']
            loss = criterion(outputs, masks)
            val_loss += loss.item()
    return val_loss / len(loader)

# ======================
# 7. Main Loop
# ======================
if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    for epoch in range(EPOCHS):
        train_loss = train_one_epoch(train_loader, model, optimizer, criterion)
        val_loss = evaluate(val_loader, model, criterion)

        print(f"Epoch [{epoch+1}/{EPOCHS}] "
              f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

        torch.save(model.state_dict(), f"models/unet_epoch{epoch+1}.pth")
