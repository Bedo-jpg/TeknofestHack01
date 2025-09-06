import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { checkHealth } from "./services/api";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import axios from "axios";
import SwipeControl from './SwipeControl';
import { getImageURL } from './services/api';

const features = [
  { icon: "🛰️", title: "Deprem Öncesi & Sonrası", desc: "İHA görüntülerinden fark analizi" },
  { icon: "🏚️", title: "Otomatik Yıkık Bina Tespiti", desc: "Derin öğrenme tabanlı segmentasyon ve sınıflandırma" },
  { icon: "🖼️", title: "Etiketlenmiş Veri", desc: "Manuel doğrulama için bina maskeleri ve poligonlar" },
  { icon: "📂", title: "GeoJSON & Harita Entegrasyonu", desc: "Yıkık bina sonuçlarının interaktif haritada gösterimi" },
  { icon: "⚡", title: "Asenkron Görev İşleme", desc: "Redis + RQ ile yüksek hacimli görüntülerin işlenmesi" },
  { icon: "🔄", title: "Swipe Görselleştirme", desc: "Öncesi / sonrası görüntü karşılaştırması" },
  { icon: "🛡️", title: "Error Handling & Durum Yönetimi", desc: "Job durumları: 202 (PENDING), 200 (READY)" },
];

const team = [
  { name: "1. Kişi", role: "Frontend Developer" },
  { name: "2. Kişi", role: "Backend Developer" },
  { name: "3. Kişi", role: "ML Engineer" },
];

export default function App() {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);
  const drawRef = useRef(null);  const [currentJobId, setCurrentJobId] = useState(null);
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [drawnShapes, setDrawnShapes] = useState([]);
  const [jobStatus, setJobStatus] = useState(null);
  const [beforeId, setBeforeId] = useState('2023-02-01'); // Backend'den alacağın değer
  const [afterId, setAfterId] = useState('2023-02-08');   // Backend'den alacağın değer
  const [showSwipe, setShowSwipe] = useState(false);      // Swipe'ı gösterme/gizleme

  // ✅ Backend bağlantı testi
  const testConnection = async () => {
    try {
      const response = await checkHealth();
      alert(`✅ Backend sağlıklı: ${response.data.status}`);
    } catch (error) {
      alert("❌ Backend bağlantı hatası!");
    }
  };

  // ✅ Çizilen poligonları backend'e gönder
  const sendPolygonsToBackend = async (geojson) => {
    try {
      const response = await axios.post("http://localhost:8000/aoi/analyze", geojson);
      setCurrentJobId(response.data.job_id);
      setJobStatus('PENDING');

      alert("✅ Poligonlar backend'e gönderildi! Job ID: " + response.data.job_id);
      console.log("Backend response:", response.data);
      
    } catch (err) {
      console.error("Backend error:", err);
      alert("❌ Poligon gönderilemedi! Backend: http://localhost:8000/aoi/analyze");
    }
  };

  // ✅ Polling mekanizması
  useEffect(() => {
    let intervalId;
    
    if (currentJobId) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/jobs/${currentJobId}/status`);
          const status = response.data.status;
          setJobStatus(status);
          console.log("Job durumu:", status);
          
          if (status === 'SUCCESS') {
            // ✅ İşlem tamamlandı, sonuçları al
            const resultResponse = await axios.get(`http://localhost:8000/jobs/${currentJobId}/results`);
            const resultGeoJSON = resultResponse.data;
            
            // Sonuçları haritaya işle
            if (mapRef.current && mapRef.current.getSource('damage-data')) {
              mapRef.current.getSource('damage-data').setData(resultGeoJSON);
            }
            setGeoJsonData(resultGeoJSON);
            
            // Polling'i durdur ve job id'sini sıfırla
            clearInterval(intervalId);
            setCurrentJobId(null);
            alert("✅ Analiz tamamlandı!");
          } else if (status === 'FAILURE') {
            // ❌ Hata durumu
            clearInterval(intervalId);
            setCurrentJobId(null);
            setJobStatus(null);
            alert("❌ Analiz başarısız oldu!");
          }
          // PENDING veya STARTED durumlarında bir şey yapma, bir sonraki poll'u bekler
        } catch (error) {
          console.error("Polling hatası:", error);
          clearInterval(intervalId);
          setCurrentJobId(null);
          setJobStatus(null);
        }
      }, 2000); // Her 2 saniyede bir sorgula
    }
    
    // Component unmount olduğunda veya jobId değiştiğinde interval'i temizle
    return () => clearInterval(intervalId);
  }, [currentJobId]);

  const loadSampleData = () => {
    const sampleData = {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { damage: "high", confidence: 0.92 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [36.248, 36.248],
                [36.25, 36.248],
                [36.25, 36.25],
                [36.248, 36.25],
                [36.248, 36.248],
              ],
            ],
          },
        },
      ],
    };

    const map = mapRef.current;
    if (map && map.getSource("damage-data")) {
      map.getSource("damage-data").setData(sampleData);
      setGeoJsonData(sampleData);
      alert("✅ Örnek veri haritaya yüklendi!");
    } else {
      alert("⚠️ Önce harita yüklenmeli!");
    }
  };

  // ✅ Harita init
  useEffect(() => {
    if (mapContainer.current && !mapRef.current) {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: "https://demotiles.maplibre.org/style.json",
        center: [36.25, 36.25],
        zoom: 10,
      });

      map.on("load", () => {
        map.addSource("damage-data", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        map.addLayer({
          id: "damaged-buildings",
          type: "fill",
          source: "damage-data",
          paint: {
            "fill-color": [
              "case",
              ["==", ["get", "damage"], "high"], "#ff0000",
              ["==", ["get", "damage"], "medium"], "#ff9900",
              "#00ff00",
            ],
            "fill-opacity": 0.6,
          },
        });

        map.addLayer({
          id: "building-outlines",
          type: "line",
          source: "damage-data",
          paint: { "line-color": "#000", "line-width": 1 },
        });

        // ✅ DRAW Tool
        const draw = new MapboxDraw({
          displayControlsDefault: false,
          controls: { polygon: true, trash: true },
        });
        map.addControl(draw);
        drawRef.current = draw;

        // Çizim tamamlandığında
        draw.on("draw.create", (e) => {
          const data = draw.getAll();
          setDrawnShapes(data.features);
        });

        draw.on("draw.update", (e) => {
          const data = draw.getAll();
          setDrawnShapes(data.features);
        });
      });

      mapRef.current = map;

      return () => {
        if (mapRef.current) {
          mapRef.current.remove();
          mapRef.current = null;
        }
      };
    }
  }, []);

  return (
    <div className="font-sans text-gray-900 min-h-screen">
      {/* Navbar */}
      <nav className="flex justify-between items-center px-8 py-4 bg-gray-800 text-white fixed w-full z-50 shadow-md">
        <div>
          <img src="/tabname.png" alt="Logo" className="w-32 h-auto" />
        </div>
        <ul className="flex space-x-6">
          <li className="hover:text-yellow-400 cursor-pointer">Yıkık Bina Tespiti</li>
          <li className="hover:text-yellow-400 cursor-pointer">Haritalama</li>
          <li className="hover:text-yellow-400 cursor-pointer">Görüntü İşleme</li>
          <li className="hover:text-yellow-400 cursor-pointer">Görselleştirme</li>
        </ul>
        
        {/* İşlem durumu göstergesi */}
        {jobStatus && (
          <div className="text-sm">
            Durum: {jobStatus === 'PENDING' ? '⏳ İşlem sürüyor' : '✅ Tamamlandı'}
          </div>
        )}
      </nav>

      {/* Hero + Map */}
      <section className="relative min-h-screen bg-gradient-to-br from-green-700 to-indigo-900 flex items-center justify-center px-6 pt-16">
        <div className="flex gap-6 w-full max-w-6xl">
          {/* Sol Taraf - Butonlar ve Başlık */}
          <div className="flex flex-col items-center text-center w-1/4">
            <motion.h1 
              initial={{ opacity: 0, y: -50 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ duration: 1 }}
              className="text-white text-4xl font-bold drop-shadow-lg mb-8"
            >
              Güzel Ülkemiz İçin Varız
            </motion.h1>
            
            <div className="flex flex-col gap-4 w-full">
              <button 
                onClick={testConnection}
                className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 w-full"
              >
                Backend Test
              </button>
              
              <button 
                onClick={loadSampleData}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 w-full"
              >
                Örnek Veri Yükle
              </button>

              {/* İşlem durumu */}
              {jobStatus && (
                <div className="p-2 bg-white rounded-lg text-center">
                  <div className="font-semibold">İşlem Durumu</div>
                  <div>{jobStatus === 'PENDING' ? '⏳ Analiz yapılıyor...' : '✅ Analiz tamamlandı'}</div>
                </div>
              )}
            </div>
          </div>

          {/* Orta - Harita */}
          <div 
            ref={mapContainer} 
            className="flex-1 h-[70vh] rounded-lg shadow-xl border-2 border-white bg-white relative"
          />
          {showSwipe && (
          <SwipeControl 
            map={mapRef.current} 
            beforeId={beforeId} 
            afterId={afterId} 
          />
        )}

          {/* Sağ Taraf - Çizim Paneli */}
          <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-xl border-2 border-gray-300 w-1/4 h-fit">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">🎨 Çizim Araçları</h3>
            
            <div className="flex flex-col gap-3">
              <button 
                className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center gap-2"
                onClick={() => {
                  if (drawRef.current) {
                    drawRef.current.changeMode('draw_polygon');
                  } else {
                    console.error("Draw tool henüz yüklenmedi!");
                  }
                }}
              >
                <span>🔷</span>
                Polygon Çiz
              </button>
              
              <button 
                onClick={() => {
                  if (drawRef.current) {
                    drawRef.current.changeMode('direct_select');
                  } else {
                    console.error("Draw tool henüz yüklenmedi!");
                  }
                }}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center gap-2"
              >
                <span>✏️</span>
                Düzenle
              </button>
              
              <button  
                onClick={() => {
                  if (drawRef.current) {
                    drawRef.current.deleteAll();
                    setDrawnShapes([]);
                  } else {
                    console.error("Draw tool henüz yüklenmedi!");
                  }
                }}
                className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center gap-2"
              >
                <span>🗑️</span>
                Temizle
              </button>

              <div className="border-t border-gray-300 my-3"></div>

              <button 
                onClick={() => setShowSwipe(!showSwipe)}
                className="bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center gap-2"
              >
                <span>🔄</span>
                {showSwipe ? 'Swipe Kapat' : 'Swipe Aç'}
              </button>

              <button 
                onClick={() => {
                  if (drawnShapes.length > 0) {
                    sendPolygonsToBackend({
                      type: "FeatureCollection",
                      features: drawnShapes
                    });
                  }
                }}
                disabled={drawnShapes.length === 0 || jobStatus === 'PENDING'}
                className="bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center gap-2"
              >
                <span>📤</span>
                Analiz Et ({drawnShapes.length})
              </button>
            </div>

            {/* Çizilen Şekil Bilgisi */}
            {drawnShapes.length > 0 && (
              <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-yellow-800 text-center">
                  🎯 {drawnShapes.length} şekil çizildi
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 md:px-20 bg-gray-100">
        <h2 className="text-4xl font-bold text-center mb-12">Ürün Özellikleri</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f, idx) => (
            <motion.div key={idx} whileHover={{ scale: 1.05 }} className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition">
              <div className="text-4xl mb-4">{f.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
              <p className="text-gray-600">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="py-20 px-6 md:px-20 bg-white">
        <h2 className="text-4xl font-bold text-center mb-12">Ekip</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {team.map((t, idx) => (
            <div key={idx} className="text-center bg-gray-50 p-6 rounded-xl shadow-md hover:shadow-xl transition">
              <div className="text-6xl mb-4">👤</div>
              <h3 className="text-xl font-semibold">{t.name}</h3>
              <p className="text-gray-600">{t.role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 md:px-20 bg-gray-800 text-white">
        <p className="text-center">© 2025 QuakeVisionAI | Tüm Hakları Saklıdır</p>
      </footer>
    </div>
  );
 }

