# backend/test_model.py
import torch
from ml.improved_model import ImprovedSegModel
from ml.inference_ml import BatchInference
import numpy as np

def test_trained_model():
    print("✅ Eğitilmiş model test ediliyor...")
    
    # Modeli yükle
    model = ImprovedSegModel()
    model.load_state_dict(torch.load("hatay_trained_model.pth", map_location="cpu"))
    model.eval()
    
    # Test input'u oluştur
    test_input = torch.randn(1, 6, 256, 256)  # Before+After concatenated
    
    # Prediction yap
    with torch.no_grad():
        output = model(test_input)
    
    print(f"✅ Test başarılı!")
    print(f"📊 Input shape: {test_input.shape}")
    print(f"📊 Output shape: {output.shape}")
    print(f"📊 Output range: [{output.min():.3f}, {output.max():.3f}]")
    
    return output

if __name__ == "__main__":
    test_trained_model()