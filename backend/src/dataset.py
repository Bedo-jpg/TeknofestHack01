import os
import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import torchvision.transforms as T

class BuildingDamageDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform

        self.images = sorted(os.listdir(image_dir))
        self.masks = sorted(os.listdir(mask_dir))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.masks[idx])

        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        image = np.array(image)
        mask = np.array(mask)
        mask = (mask > 127).astype(np.uint8)

        if self.transform:
            augmented = self.transform(image=image, mask=mask)
            image = augmented["image"]
            mask = augmented["mask"]

        image = T.ToTensor()(image)
        mask = torch.tensor(mask, dtype=torch.long)

        return image, mask

if __name__ == "__main__":
    dataset = BuildingDamageDataset(
        image_dir="data/scenes/tiles/images",
        mask_dir="data/scenes/tiles/masks"
    )
    img, mask = dataset[0]
    print("Image shape:", img.shape)
    print("Mask shape:", mask.shape)
