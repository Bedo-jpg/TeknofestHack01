# ml/inference_ml.py
import torch
import numpy as np
from typing import List, Tuple
import time
import sys
import os

# SADECE gerçek modeli import et
try:
    from improved_model import ImprovedSegModel
except ImportError:
    from .improved_model import ImprovedSegModel

def prepare_input(before_tile: np.ndarray, after_tile: np.ndarray) -> torch.Tensor:
    """
    Before/after tile'ları model input'una hazırlar.
    """
    # Channel dimension kontrol et
    if before_tile.shape[0] not in [1, 3, 4]:
        before_tile = before_tile.transpose(2, 0, 1)
    if after_tile.shape[0] not in [1, 3, 4]:
        after_tile = after_tile.transpose(2, 0, 1)
    
    # İlk 3 channel'ı al (RGB için)
    before_tile = before_tile[:3] if before_tile.shape[0] >= 3 else before_tile
    after_tile = after_tile[:3] if after_tile.shape[0] >= 3 else after_tile
    
    # Normalize [0, 255] -> [0, 1]
    before_tile = before_tile.astype(np.float32) / 255.0
    after_tile = after_tile.astype(np.float32) / 255.0
    
    # Before ve after'ı birleştir [6, H, W]
    combined = np.concatenate([before_tile, after_tile], axis=0)
    
    # Tensor'a çevir ve batch dimension ekle [1, 6, H, W]
    return torch.from_numpy(combined).unsqueeze(0)


class BatchInference:
    def __init__(self, batch_size: int = 4, model_path: str = "hatay_trained_model.pth"):  # ← Varsayılan yol
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"✅ Using device: {self.device}")
        
        self.model = self._load_model(model_path)
        self.model.eval()
        self.batch_size = batch_size
    
    def _load_model(self, model_path: str = "hatay_trained_model.pth"):  # ← Varsayılan yol
        """Eğitilmiş modeli yükle"""
        try:
            model = ImprovedSegModel()
            
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"✅ Eğitilmiş model yüklendi: {model_path}")
            else:
                print(f"⚠️  Eğitilmiş model bulunamadı, yeni model oluşturuldu: {model_path}")
                
        except Exception as e:
            raise Exception(f"❌ Model yükleme hatası: {e}")
        
        return model.to(self.device)
    
    def process_batch(self, before_after_pairs: List[Tuple[np.ndarray, np.ndarray]]) -> List[np.ndarray]:
        """Batch halinde inference yapar"""
        results = []
        
        for i in range(0, len(before_after_pairs), self.batch_size):
            batch = before_after_pairs[i:i + self.batch_size]
            batch_tensors = []
            
            for before, after in batch:
                try:
                    input_tensor = prepare_input(before, after)
                    batch_tensors.append(input_tensor)
                except Exception as e:
                    print(f"❌ Input preparation error: {e}")
                    continue
            
            if batch_tensors:
                try:
                    # Batch'i birleştir [B, 6, H, W]
                    batch_tensor = torch.cat(batch_tensors, dim=0).to(self.device)
                    
                    # Inference
                    with torch.no_grad():
                        output = self.model(batch_tensor)
                    
                    # CPU'ya taşı ve numpy'a çevir
                    output = output.cpu().numpy()
                    
                    # Sonuçları ekle
                    for j in range(output.shape[0]):
                        results.append(output[j, 0])  # [H, W] probability map
                        
                except Exception as e:
                    print(f"❌ Inference error: {e}")
                    # Artık fallback yok, hata fırlat
                    raise Exception("Inference başarısız")
        
        return results

def test_inference():
    """Model testi"""
    print("🚀 Model testi başlıyor...")
    
    try:
        # Test verisi oluştur
        test_pairs = []
        for i in range(2):
            before = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
            after = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
            test_pairs.append((before, after))
        
        # Inference
        inferencer = BatchInference(batch_size=2)
        results = inferencer.process_batch(test_pairs)
        
        print(f"✅ {len(results)} sonuç elde edildi")
        if results:
            print(f"✅ Sonuç şekli: {results[0].shape}")
            print(f"✅ Min/Max: [{results[0].min():.3f}, {results[0].max():.3f}]")
            print("🎉 MODEL BAŞARIYLA ÇALIŞTI!")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_inference()