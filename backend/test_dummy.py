# backend/test_dummy.py
import sys
import os
from pathlib import Path

# Backend içindeki ML modülüne erişim
backend_path = Path(__file__).parent
ml_path = backend_path / "ml"
if str(ml_path) not in sys.path:
    sys.path.append(str(ml_path))

try:
    from model import DummySegModel
except ImportError:
    from backend.ml.improved_model import DummySegModel

import torch

def test_dummy_model():
    """Dummy model testi - Backend içinden"""
    try:
        model = DummySegModel()
        print("✅ Dummy model başarıyla yüklendi.")
        
        x = torch.randn(1, 6, 256, 256)
        print(f"✅ Input shape: {x.shape}")
        
        with torch.no_grad():
            y = model(x)
        
        print(f"✅ Output shape: {y.shape}")
        print(f"✅ Output min/max: {y.min():.4f}, {y.max():.4f}")
        print("🎉 Model testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dummy_model()
    exit(0 if success else 1)