# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any
import uuid
from ml.inference_ml import BatchInference

inferencer = BatchInference()  # Otomatik hatay_trained_model.pth yüklenecek

from inference import predict_image, run_hatay_analysis

app = FastAPI(title="QuakeVisionAI API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm origin'lere izin ver (güvenlik için production'da kısıtlayın)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "QuakeVisionAI API çalışıyor! 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Tekil görüntü tahmini"""
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(400, "Sadece PNG/JPG/JPEG dosyaları yükleyebilirsiniz")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    
    try:
        mask_path, overlay_path = predict_image(temp_path)
        return {
            "success": True,
            "mask_path": mask_path,
            "overlay_path": overlay_path
        }
    except Exception as e:
        raise HTTPException(500, f"Tahmin hatası: {str(e)}")
    finally:
        os.unlink(temp_path)

@app.post("/api/analyze/hatay")
async def analyze_hatay(background_tasks: BackgroundTasks):
    """Hatay görüntülerini analiz et"""
    try:
        # Sabit yollar (sonra dinamik yapılabilir)
        data_dir = Path(r"C:\Users\ozges\OneDrive\Masaüstü\1c__Hatay_Enkaz_Bina_Etiketleme")
        before_path = data_dir / "HATAY MERKEZ-2 2015.tif"
        after_path = data_dir / "HATAY MERKEZ-2 2023.tif"
        
        if not before_path.exists() or not after_path.exists():
            raise HTTPException(404, "Hatay görüntüleri bulunamadı")
        
        # Background task olarak başlat
        task_id = str(uuid.uuid4())
        background_tasks.add_task(
            run_hatay_analysis_task, 
            str(before_path), 
            str(after_path), 
            task_id
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Hatay analizi başlatıldı"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Analiz hatası: {str(e)}")

def run_hatay_analysis_task(before_path: str, after_path: str, task_id: str):
    """Background task for Hatay analysis"""
    try:
        result = run_hatay_analysis(before_path, after_path, "results")
        
        # Sonucu task_id ile kaydet
        output_file = Path("results") / f"hatay_analysis_{task_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Hatay analysis completed: {task_id}")
        
    except Exception as e:
        print(f"❌ Hatay analysis failed: {e}")

@app.get("/api/results/hatay/{task_id}")
async def get_hatay_results(task_id: str):
    """Hatay analiz sonuçlarını getir"""
    result_file = Path("results") / f"hatay_analysis_{task_id}.json"
    
    if not result_file.exists():
        raise HTTPException(404, "Sonuçlar bulunamadı")
    
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results

# Mevcut endpoint'leri koruyalım
@app.get("/imagery/scenes")
def get_scenes():
    return {"scenes": ["scene1", "scene2"]}

@app.post("/aoi/analyze")
def analyze_aoi():
    return {"job_id": "1234", "status": "PENDING"}

@app.get("/results/{job_id}")
def get_results(job_id: str):
    return {"job_id": job_id, "status": "READY", "result": "dummy_geojson"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)