# backend/src/inference.py - ÜST KISMI ŞÖYLE YAP:

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from shapely.geometry import shape
from shapely.geometry import mapping
import rasterio
from rasterio.windows import Window
import sys
import os

# ML path'ini doğru ayarla
ml_path = Path("ml")

if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

print(f"🔍 ML path: {ml_path.absolute()}")
print(f"🔍 ML exists: {ml_path.exists()}")

# ML modüllerini import et
ML_AVAILABLE = False
try:
    if ml_path.exists():
        # ARTIK ABSOLUTE IMPORT KULLANABİLİRİZ
        from ml.tiling import create_tiles
        from ml.inference_ml import BatchInference, prepare_input
        from ml.postproc import probability_to_polygons
        ML_AVAILABLE = True
        print("✅ ML modülleri başarıyla yüklendi")
    else:
        print("⚠️  ML klasörü bulunamadı")
except ImportError as e:
    print(f"⚠️  ML modülleri yüklenemedi: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"⚠️  ML modülleri yüklenirken hata: {e}")
    import traceback
    traceback.print_exc()

def predict_image(image_path: str):
    """Tekil görüntü tahmini için"""
    # Basit bir fallback implementasyonu
    return "mask_path.png", "overlay_path.png"

def run_hatay_analysis(before_path: str, after_path: str, output_dir: str = "results"):
    """Hatay görüntülerini analiz et"""
    if not ML_AVAILABLE:
        print("⚠️  ML modülleri yok, fallback kullanılıyor")
        return fallback_analysis(before_path, after_path, output_dir)
    
    try:
        processor = HatayProcessor(batch_size=1)
        result = processor.process_hatay(before_path, after_path, output_dir)
        return result
    except Exception as e:
        print(f"❌ Hatay analysis error: {e}")
        return fallback_analysis(before_path, after_path, output_dir)

def fallback_analysis(before_path: str, after_path: str, output_dir: str):
    """Fallback analiz"""
    print("⚠️  Fallback analysis kullanılıyor")
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "confidence": 0.85,
                    "area_pixels": 1500,
                    "status": "fallback"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [512310, 4009841],
                        [512410, 4009841],
                        [512410, 4009741],
                        [512310, 4009741],
                        [512310, 4009841]
                    ]]
                }
            }
        ],
        "metadata": {
            "before_image": Path(before_path).name,
            "after_image": Path(after_path).name,
            "total_damage_areas": 1,
            "status": "fallback"
        }
    }

# ML modülleri yüklüyse HatayProcessor'ı tanımla
if ML_AVAILABLE:
    class HatayProcessor:
        def __init__(self, batch_size: int = 2):
            self.batch_size = batch_size
            self.inferencer = BatchInference(batch_size=batch_size)
        
        def load_and_preprocess(self, file_path: str) -> np.ndarray:
            """GeoTIFF yükle ve ön işleme yap"""
            try:
                with rasterio.open(file_path) as src:
                    data = src.read()
                    data = np.transpose(data, (1, 2, 0))
                    data = np.nan_to_num(data, nan=0.0)
                    if data.max() > 255:
                        data = (data - data.min()) / (data.max() - data.min()) * 255
                    return data.astype(np.uint8)
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                return None
        
        def create_tiles_from_array(self, image_array: np.ndarray, tile_size: int = 256, 
                                   overlap: int = 30) -> List[Tuple[np.ndarray, Dict]]:
            """Büyük görüntüden tile'lar oluştur"""
            tiles = []
            height, width, channels = image_array.shape
            
            for y in range(0, height, tile_size - overlap):
                for x in range(0, width, tile_size - overlap):
                    win_height = min(tile_size, height - y)
                    win_width = min(tile_size, width - x)
                    tile = image_array[y:y+win_height, x:x+win_width, :]
                    meta = {'x': x, 'y': y, 'width': win_width, 'height': win_height}
                    tiles.append((tile, meta))
            return tiles
        
        def process_hatay(self, before_path: str, after_path: str, output_dir: str) -> Dict:
            """Hatay verilerini işle"""
            print("🔍 Hatay verileri işleniyor...")
            
            before_image = self.load_and_preprocess(before_path)
            after_image = self.load_and_preprocess(after_path)
            
            if before_image is None or after_image is None:
                return fallback_analysis(before_path, after_path, output_dir)
            
            print(f"📊 Before shape: {before_image.shape}")
            print(f"📊 After shape: {after_image.shape}")
            
            # Tile'ları oluştur (ilk 1000x1000 px ile sınırla)
            before_image = before_image[:1000, :1000, :]  # ← TEST İÇİN SINIRLA
            after_image = after_image[:1000, :1000, :]    # ← TEST İÇİN SINIRLA
            
            before_tiles = self.create_tiles_from_array(before_image)
            after_tiles = self.create_tiles_from_array(after_image)
            
            # Tile çiftlerini eşleştir
            tile_pairs = []
            for (before_tile, before_meta), (after_tile, after_meta) in zip(before_tiles, after_tiles):
                if before_meta['x'] == after_meta['x'] and before_meta['y'] == after_meta['y']:
                    tile_pairs.append((before_tile, after_tile, before_meta))
            
            print(f"📊 Eşleşen tile çiftleri: {len(tile_pairs)}")
            
            # İlk 2 tile ile test
            test_tiles = tile_pairs[:2]
            before_after_pairs = [(before, after) for before, after, _ in test_tiles]
            
            # Inference
            print("🤖 Inference yapılıyor...")
            probability_maps = self.inferencer.process_batch(before_after_pairs)
            
            # Post-processing
            print("🎨 Polygon'a dönüştürülüyor...")
            all_features = []
            for i, (prob_map, (_, _, meta)) in enumerate(zip(probability_maps, test_tiles)):
                try:
                    features = probability_to_polygons(prob_map, threshold=0.6, min_area=50)
                    for feature in features:
                        geom = shape(feature['geometry'])
                        adjusted_geom = geom.translate(meta['x'], meta['y'])
                        feature['geometry'] = mapping(adjusted_geom)
                    all_features.extend(features)
                    print(f"   Tile {i+1}: {len(features)} hasar alanı")
                except Exception as e:
                    print(f"❌ Tile {i} işleme hatası: {e}")
                    continue
            
            # Sonuçları kaydet
            result = {
                "type": "FeatureCollection",
                "features": all_features,
                "metadata": {
                    "before_image": Path(before_path).name,
                    "after_image": Path(after_path).name,
                    "total_damage_areas": len(all_features),
                    "processed_tiles": len(test_tiles)
                }
            }
            
            os.makedirs(output_dir, exist_ok=True)
            output_file = Path(output_dir) / "hatay_analysis.geojson"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Sonuçlar kaydedildi: {output_file}")
            return result
else:
    # ML modülleri yoksa boş bir class tanımla
    class HatayProcessor:
        def __init__(self, batch_size: int = 2):
            pass
        
        def process_hatay(self, before_path: str, after_path: str, output_dir: str) -> Dict:
            return fallback_analysis(before_path, after_path, output_dir)