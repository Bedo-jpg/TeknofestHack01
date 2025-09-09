import rasterio
from rasterio.windows import Window
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import json

def create_tiles(image_path: str, tile_size: int = 256, overlap: int = 25) -> List[Dict]:
    """
    Büyük ortomozaikten tile'lar oluşturur.
    
    Args:
        image_path: Giriş TIFF dosya yolu
        tile_size: Tile boyutu (default: 256)
        overlap: Tile'lar arası overlap piksel sayısı (default: 25)
    
    Returns:
        Tile metadata listesi
    """
    tiles_metadata = []
    
    with rasterio.open(image_path) as src:
        width, height = src.width, src.height
        transform = src.transform
        crs = src.crs
        
        # Tile'ları oluştur
        for y in range(0, height, tile_size - overlap):
            for x in range(0, width, tile_size - overlap):
                # Pencere boyutunu ayarla (sınırları aşmayacak şekilde)
                win = Window(
                    x, y,
                    min(tile_size, width - x),
                    min(tile_size, height - y)
                )
                
                # Görüntüyü oku
                tile_data = src.read(window=win)
                
                # Tile metadata'sını oluştur
                tile_meta = {
                    'x': x,
                    'y': y,
                    'width': win.width,
                    'height': win.height,
                    'transform': transform * transform.translation(x, y),
                    'crs': crs.to_string() if crs else None
                }
                
                tiles_metadata.append(tile_meta)
                
                # DEBUG: İlk birkaç tile'ı kaydet
                if len(tiles_metadata) <= 3:
                    output_path = f"tile_{x}_{y}.npy"
                    np.save(output_path, tile_data)
                    print(f"DEBUG: Tile kaydedildi: {output_path}")
    
    return tiles_metadata

# Test fonksiyonu
def test_tiling():
    """Tiling modülünü test et"""
    try:
        # Örnek bir TIFF dosyası kullan
        sample_path = "../data/scenes/before_01.tif"
        if Path(sample_path).exists():
            tiles = create_tiles(sample_path)
            print(f"✅ {len(tiles)} tile oluşturuldu")
            print(f"✅ İlk tile metadata: {json.dumps(tiles[0], indent=2, default=str)}")
            return True
        else:
            print("⚠️  Test dosyası bulunamadı, dummy metadata döndürülüyor")
            # Dummy metadata üret
            return [{
                'x': 0, 'y': 0, 'width': 256, 'height': 256,
                'transform': [0.1, 0, 0, 0, -0.1, 0],
                'crs': 'EPSG:4326'
            }]
    except Exception as e:
        print(f"❌ Tiling hatası: {e}")
        return []

if __name__ == "__main__":
    test_tiling()