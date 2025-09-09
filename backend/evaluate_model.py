# backend/evaluate_model.py
import torch
from ml.improved_model import ImprovedSegModel
from ml.dataset import DisasterDataset
from torch.utils.data import DataLoader
import numpy as np

def evaluate_model(model_path="hatay_trained_model.pth"):
    """Modeli değerlendir"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Modeli yükle
    model = ImprovedSegModel().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Test datası
    dataset = DisasterDataset()
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False)
    
    # Metrikler
    total_loss = 0
    predictions = []
    
    with torch.no_grad():
        for before, after in dataloader:
            inputs = torch.cat([before, after], dim=1).to(device)
            outputs = model(inputs)
            
            # Burada gerçek metrikleri hesapla
            predictions.extend(outputs.cpu().numpy())
    
    print(f"✅ Model değerlendirme tamamlandı")
    print(f"📊 Toplam örnek: {len(dataset)}")
    print(f"📊 Prediction şekli: {predictions[0].shape}")
    
    return predictions