import React from "react";
import { motion } from "framer-motion";

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
  return (
    <div className="font-sans text-gray-900">
      {/* Navbar */}
      <nav className="flex justify-between items-center px-8 py-4 bg-gray-800 text-white fixed w-full z-50 shadow-md">
        <div><img src="/tabname.png" alt="QuackVisionAI Logo" className="w-32 h-auto"/>
</div>
        <ul className="flex space-x-6">
          <li className="hover:text-yellow-400 cursor-pointer">Yıkık Bina Tespiti</li>
          <li className="hover:text-yellow-400 cursor-pointer">Haritalama</li>
          <li className="hover:text-yellow-400 cursor-pointer">Görüntü İşleme</li>
          <li className="hover:text-yellow-400 cursor-pointer">Görselleştirme</li>
        </ul>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen bg-gradient-to-br from-green-700 to-indigo-900 flex items-center justify-center text-center px-6">
        <motion.h1 
          initial={{ opacity: 0, y: -50 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 1 }}
          className="text-white text-5xl md:text-7xl font-bold drop-shadow-lg"
        >
          Güzel Ülkemiz İçin Varız
        </motion.h1>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 md:px-20 bg-gray-100">
        <h2 className="text-4xl font-bold text-center mb-12">Ürün Özellikleri</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f, idx) => (
            <motion.div 
              key={idx} 
              whileHover={{ scale: 1.05 }} 
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition"
            >
              <div className="text-4xl mb-4">{f.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
              <p className="text-gray-600">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 px-6 md:px-20">
        <h2 className="text-4xl font-bold text-center mb-12">Ekip</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {team.map((t, idx) => (
            <div key={idx} className="text-center bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition">
              <div className="text-6xl mb-4">👤</div>
              <h3 className="text-xl font-semibold">{t.name}</h3>
              <p className="text-gray-600">{t.role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 md:px-20 bg-gray-800 text-white">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          
          <div className="mb-4 md:mb-0 mr-6">
            <img src="/icon.png" alt="QuakeVisionAI Logo" className="h-20 w-auto"/>
          </div>
          <ul className="flex flex-wrap gap-4 text-sm md:text-base">
            <li className="hover:text-yellow-400 cursor-pointer">Kurumsal</li>
            <li className="hover:text-yellow-400 cursor-pointer">Tarihçe</li>
            <li className="hover:text-yellow-400 cursor-pointer">Gizlilik ve Çerez Politikası</li>
            <li className="hover:text-yellow-400 cursor-pointer">Aydınlatma Metni</li>
            <li className="hover:text-yellow-400 cursor-pointer">Podcast</li>
            <li className="hover:text-yellow-400 cursor-pointer">Dosyalar</li>
            <li className="hover:text-yellow-400 cursor-pointer">Habercilik ve KVKK İlkeleri</li>
            <li className="hover:text-yellow-400 cursor-pointer">AA WhatsApp Kanalları</li>
            <li className="hover:text-yellow-400 cursor-pointer">Yayın İlkeleri</li>
            <li className="hover:text-yellow-400 cursor-pointer">Künye</li>
            <li className="hover:text-yellow-400 cursor-pointer">Sosyal Medya</li>
            <li className="hover:text-yellow-400 cursor-pointer">Logolar</li>
          </ul>
        </div>
      </footer>
    </div>
  );
}
