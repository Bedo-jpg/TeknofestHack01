# backend/train_real.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import StepLR  # ← BU SATIRI EKLE
from ml.improved_model import ImprovedSegModel
from ml.dataset import DisasterDataset
from pathlib import Path
import numpy as np

# tqdm yüklü değilse, basit bir progress bar yapalım
try:
    from tqdm import tqdm
except ImportError:
    # tqdm yoksa basit bir progress bar
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None):
            self.iterable = iterable
            self.desc = desc or ""
            self.total = total or len(iterable) if iterable else 0
            self.count = 0
        
        def __iter__(self):
            for item in self.iterable:
                self.count += 1
                yield item
        
        def set_postfix(self, **kwargs):
            pass
        
        def close(self):
            pass

class RealTrainer:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"✅ Training device: {self.device}")
        
        self.model = ImprovedSegModel().to(self.device)
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # STEPLR SCHEDULER EKLE ← YENİ
        self.scheduler = StepLR(self.optimizer, step_size=3, gamma=0.5)
        # step_size=3: Her 3 epoch'ta bir LR güncelle
        # gamma=0.5: Learning rate'i yarıya düşür
        
        # VERİ YOLU
        self.data_dir = Path(r"C:\Users\ozges\OneDrive\Masaüstü\1c__Hatay_Enkaz_Bina_Etiketleme")
    
    def train(self, epochs=10, batch_size=8):  # ← Batch size 8 olarak güncellendi
        """Gerçek eğitim loop'u"""
        print("🚀 Gerçek Hatay verileriyle eğitim başlıyor...")
        print(f"📁 Veri yolu: {self.data_dir}")
        print(f"📦 Batch size: {batch_size}")
        print(f"🔄 Total epochs: {epochs}")
        
        # Dataset ve DataLoader oluştur
        dataset = DisasterDataset(data_dir=self.data_dir)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        print(f"📊 {len(dataset)} training patch'i yüklendi")
        
        for epoch in range(epochs):
            total_loss = 0
            print(f"\nEpoch {epoch+1}/{epochs}")
            
            # Learning rate'i al
            current_lr = self.scheduler.get_last_lr()[0]
            print(f"📉 Learning Rate: {current_lr:.6f}")
            
            for batch_idx, (before_batch, after_batch) in enumerate(dataloader):
                # Input'u hazırla: [B, 6, 256, 256]
                inputs = torch.cat([before_batch, after_batch], dim=1).to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                
                # Loss hesapla - GEÇİCİ: Rastgele target
                targets = torch.sigmoid(torch.randn_like(outputs)).to(self.device)
                loss = self.criterion(outputs, targets)
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                
                # Her 5 batch'te bir progress göster
                if batch_idx % 5 == 0:
                    print(f"  Batch {batch_idx}/{len(dataloader)}, Loss: {loss.item():.4f}")
            
            # STEPLR'ı GÜNCELLE ← YENİ
            self.scheduler.step()
            
            avg_loss = total_loss / len(dataloader)
            print(f"📊 Epoch {epoch+1}/{epochs}, Average Loss: {avg_loss:.4f}")
            
            # Her 2 epoch'ta modeli kaydet
            if (epoch + 1) % 2 == 0:
                model_path = f"hatay_model_epoch_{epoch+1}.pth"
                torch.save(self.model.state_dict(), model_path)
                print(f"💾 Model kaydedildi: {model_path}")
        
        # Final modeli kaydet
        model_path = "hatay_trained_model_final.pth"
        torch.save(self.model.state_dict(), model_path)
        print(f"✅ Model eğitimi tamamlandı ve kaydedildi: {model_path}")
        
        return avg_loss

if __name__ == "__main__":
    # VERİ YOLUNU KONTROL ET
    data_path = Path(r"C:\Users\ozges\OneDrive\Masaüstü\1c__Hatay_Enkaz_Bina_Etiketleme")
    
    if not data_path.exists():
        print(f"❌ VERİ YOLU BULUNAMADI: {data_path}")
    else:
        print(f"✅ Veri yolu bulundu: {data_path}")
        
        before_path = data_path / "HATAY MERKEZ-2 2015.tif"
        after_path = data_path / "HATAY MERKEZ-2 2023.tif"
        
        if before_path.exists() and after_path.exists():
            print("✅ Before ve after dosyaları bulundu")
            
            # Eğitimi başlat - BATCH SIZE 8 İLE ← GÜNCELLENDİ
            trainer = RealTrainer()
            trainer.train(epochs=10, batch_size=8)
        else:
            print("❌ Before/after dosyaları bulunamadı!")