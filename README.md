# 🌌 Takım İsmi
**LuminAI**

---

## 👥 Takım Üyeleri
- Bedirhan Portakal – Backend/ML Developer
- Özge Sanal  – Frontend Developer
- Sinem İzgi – Machine Learning Engineer

---

## 📍 Ürün İsmi
**QuakeVisionAI** – Deprem Sonrası Otomatik Yıkık Bina Tespiti

---

## 🗂️ Product Backlog URL
👉 [Trello Panosu](https://trello.com/)

---

## 🏚️ Ürün Açıklaması
Bu ürün, **6 Şubat 2023 Kahramanmaraş Depremi** sonrasında Hatay ili Antakya ilçesinde çekilen **CBSGM İHA görüntülerini** kullanarak:

- Deprem **öncesi ve sonrası görüntülerden** binaları analiz eder,
- **Yıkık bina tespiti** yapar,
- Çıkan sonuçları **etiketlenmiş veri** ve **otomatik hasar haritası** olarak sunar.

Amaç, afet yönetimi ve kriz bölgelerinde hızlı ve güvenilir hasar analizi sağlayarak hem **arama-kurtarma ekiplerine** hem de **uzun vadeli şehir planlamasına** destek olmaktır.

---

## 🔑 Ürün Özellikleri
- 🛰️ **Deprem Öncesi & Sonrası Görüntü Karşılaştırma**  
  İHA görüntülerinden fark analizi

- 🏚️ **Otomatik Yıkık Bina Tespiti**  
  Derin öğrenme tabanlı segmentasyon ve sınıflandırma

- 🖼️ **Etiketlenmiş Veri Üretimi**  
  Manuel doğrulama için bina maskeleri ve poligonlar

- 📂 **GeoJSON & Harita Entegrasyonu**  
  Yıkık bina sonuçlarının interaktif haritada gösterimi

- ⚡ **Asenkron Görev İşleme**  
  Redis + RQ ile yüksek hacimli görüntülerin işlenmesi

- 🔄 **SwipeControl Görselleştirme**  
  Öncesi / sonrası görüntülerin üst üste karşılaştırılması

- 🛡️ **Error Handling & Durum Yönetimi**  
  Job durumları: 202 (*PENDING*), 200 (*READY*)

---

## 🎯 Hedef Kitle
- 🚑 Afet yönetimi ve kriz merkezleri
- 🛠️ Arama-kurtarma ekipleri
- 🏛️ Yerel yönetimler ve şehir planlamacıları
- 📊 Afet sonrası hasar analizi yapan araştırmacılar

---

## 🛠️ Kullanılan Teknolojiler
- **Backend** → FastAPI, Redis, RQ
- **Frontend** → React (Vite), MapLibre
- **ML** → PyTorch, Shapely, scikit-image
- **Veri Formatları** → GeoJSON, İHA görüntüleri (öncesi/sonrası)
- **Containerization** → Docker & Docker Compose
- **Proje Yönetimi** → Trello
- **Diğer** → Pydantic (veri validasyonu), Uvicorn (server), Tailwind (UI styling)
