import React, { useEffect, useRef } from 'react';

// ✅ getImageURL fonksiyonunu buraya taşı
const getImageURL = (imageId) => {
  return `http://localhost:8000/imagery/${imageId}`;
};

const SwipeControl = ({ map, beforeId, afterId }) => {
  const swipeContainer = useRef(null);
  
  useEffect(() => {
    if (!map || !beforeId || !afterId) return;

    // 1. Before ve After layer'larını ekle
    map.addSource('before', {
      type: 'raster',
      url: getImageURL(beforeId)
    });
    
    map.addSource('after', {
      type: 'raster',
      url: getImageURL(afterId)
    });

    map.addLayer({
      id: 'before-layer',
      type: 'raster',
      source: 'before',
      paint: { 'raster-opacity': 1 }
    });

    map.addLayer({
      id: 'after-layer',
      type: 'raster',
      source: 'after',
      paint: { 'raster-opacity': 0.5 }
    });

    // 2. Swipe için DOM elementi oluştur
    const swipeLine = document.createElement('div');
    swipeLine.style.position = 'absolute';
    swipeLine.style.width = '2px';
    swipeLine.style.height = '100%';
    swipeLine.style.backgroundColor = 'white';
    swipeLine.style.zIndex = '1000';
    swipeLine.style.cursor = 'ew-resize';
    swipeLine.style.boxShadow = '0 0 10px rgba(0,0,0,0.5)';
    
    swipeContainer.current.appendChild(swipeLine);

    // 3. Swipe olayını ekle
    let isMoving = false;
    
    const moveSwipe = (e) => {
      if (!isMoving) return;
      
      const rect = swipeContainer.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const position = (x / rect.width) * 100;
      
      if (position >= 0 && position <= 100) {
        swipeLine.style.left = `${position}%`;
        map.setPaintProperty('after-layer', 'raster-opacity', position / 100);
      }
    };

    swipeLine.addEventListener('mousedown', () => { isMoving = true; });
    document.addEventListener('mouseup', () => { isMoving = false; });
    document.addEventListener('mousemove', moveSwipe);

    // 4. Temizlik fonksiyonu
    return () => {
      document.removeEventListener('mousemove', moveSwipe);
      document.removeEventListener('mouseup', () => { isMoving = false; });
      
      if (map.getSource('before')) map.removeSource('before');
      if (map.getSource('after')) map.removeSource('after');
      if (map.getLayer('before-layer')) map.removeLayer('before-layer');
      if (map.getLayer('after-layer')) map.removeLayer('after-layer');
    };
  }, [map, beforeId, afterId]);

  if (!beforeId || !afterId) return null;

  return (
    <div
      ref={swipeContainer}
      style={{
        position: 'absolute',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        zIndex: '999',
        pointerEvents: 'none'
      }}
    />
  );
};

export default SwipeControl;