# ml/postproc.py
import numpy as np
from skimage.morphology import binary_opening, binary_closing, disk
from skimage.measure import label, regionprops
from shapely.geometry import Polygon
from shapely.geometry import shape as shapely_shape
from shapely.geometry import mapping as shapely_mapping
from typing import List, Dict, Any
import json

def probability_to_polygons(probability_map: np.ndarray, threshold: float = 0.6, 
                           min_area: int = 50, transform: List = None) -> List[Dict]:
    """
    Probability map'i GeoJSON polygon'lara dönüştürür.
    
    Args:
        probability_map: [H, W] probability array
        threshold: Binary threshold değeri
        min_area: Minimum polygon alanı (piksel)
        transform: Raster to world coordinate transform
    
    Returns:
        GeoJSON feature listesi
    """
    # Threshold uygula
    binary_mask = probability_map > threshold
    
    # Morphological operations
    binary_mask = binary_opening(binary_mask, disk(2))
    binary_mask = binary_closing(binary_mask, disk(2))
    
    # Connected components
    labeled_mask = label(binary_mask)
    features = []
    
    for region in regionprops(labeled_mask):
        if region.area < min_area:
            continue
            
        # Bounding box coordinates
        min_row, min_col, max_row, max_col = region.bbox
        
        if transform:
            # Raster to world coordinate transformation
            x0 = min_col * transform[0] + transform[2]
            y0 = min_row * transform[4] + transform[5]
            x1 = max_col * transform[0] + transform[2]
            y1 = max_row * transform[4] + transform[5]
            
            polygon = Polygon([
                [x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]
            ])
        else:
            # Pixel coordinates
            polygon = Polygon([
                [min_col, min_row], [max_col, min_row], 
                [max_col, max_row], [min_col, max_row], [min_col, min_row]
            ])
        
        features.append({
            "type": "Feature",
            "properties": {
                "confidence": float(np.mean(probability_map[region.slice])),
                "area_pixels": region.area
            },
            "geometry": shapely_mapping(polygon)
        })
    
    return features

def test_postprocessing():
    """Postprocessing testi"""
    try:
        # Dummy probability map oluştur
        prob_map = np.random.rand(256, 256)
        
        # Merkezde yüksek probability alanı oluştur
        y, x = np.ogrid[:256, :256]
        center = (128, 128)
        mask = (x - center[0])**2 + (y - center[1])**2 <= 40**2
        prob_map[mask] = 0.8 + np.random.rand(*prob_map[mask].shape) * 0.2
        
        # Polygon'lara dönüştür
        features = probability_to_polygons(prob_map, threshold=0.6)
        
        print(f"✅ {len(features)} polygon oluşturuldu")
        if features:
            print(f"✅ İlk polygon: {json.dumps(features[0], indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Postprocessing error: {e}")
        return False

if __name__ == "__main__":
    test_postprocessing()