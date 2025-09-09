# backend/ml/dataset.py
import torch
from torch.utils.data import Dataset
import rasterio
import numpy as np
from pathlib import Path

class DisasterDataset(Dataset):
    def __init__(self, data_dir, tile_size=256):
        self.data_dir = Path(data_dir)
        self.tile_size = tile_size
        self.tile_pairs = self._load_tile_pairs()
    
    def _load_tile_pairs(self):
        """Before/after tile çiftlerini yükle"""
        tile_pairs = []
        
        before_path = self.data_dir / "HATAY MERKEZ-2 2015.tif"
        after_path = self.data_dir / "HATAY MERKEZ-2 2023.tif"
        
        print(f"📂 Loading data from: {self.data_dir}")
        
        try:
            with rasterio.open(before_path) as src_before, rasterio.open(after_path) as src_after:
                print(f"📊 Before size: {src_before.width}x{src_before.height}")
                print(f"📊 After size: {src_after.width}x{src_after.height}")
                
                # Daha küçük bir örnek için sınırla (test için)
                max_tiles = 100  # Tüm veriyi yüklemek için bu satırı kaldır
                
                for y in range(0, min(src_before.height, src_after.height), self.tile_size):
                    for x in range(0, min(src_before.width, src_after.width), self.tile_size):
                        if len(tile_pairs) >= max_tiles:  # Test için sınır
                            break
                            
                        before_tile = src_before.read(
                            window=rasterio.windows.Window(x, y, self.tile_size, self.tile_size)
                        )
                        after_tile = src_after.read(
                            window=rasterio.windows.Window(x, y, self.tile_size, self.tile_size)
                        )
                        
                        if before_tile.shape[1:] == (self.tile_size, self.tile_size):
                            tile_pairs.append((before_tile, after_tile))
        
        except Exception as e:
            print(f"❌ Data loading error: {e}")
        
        return tile_pairs
    
    def __len__(self):
        return len(self.tile_pairs)
    
    def __getitem__(self, idx):
        before, after = self.tile_pairs[idx]
        
        # İlk 3 bandı al ve normalize et
        before_tensor = torch.from_numpy(before[:3].astype(np.float32) / 255.0)
        after_tensor = torch.from_numpy(after[:3].astype(np.float32) / 255.0)
        
        return before_tensor, after_tensor