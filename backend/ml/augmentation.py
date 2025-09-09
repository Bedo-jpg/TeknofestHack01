# backend/ml/augmentation.py
import albumentations as A
from albumentations.pytorch import ToTensorV2

def get_train_transforms():
    return A.Compose([
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.GaussianBlur(p=0.3),
        ToTensorV2()
    ])

def get_val_transforms():
    return A.Compose([
        ToTensorV2()
    ])