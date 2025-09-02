from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from inference import predict_image  # inference.py'den import

app = FastAPI(title="QuakeVisionAI API")

# CORS Middleware (FRONTEND İÇİN ŞART!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175", 
        "http://localhost:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177"
    ],    
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
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(400, "Sadece PNG/JPG/JPEG dosyaları yükleyebilirsiniz")
    
    # Güvenli geçici dosya oluştur
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    
    try:
        # Tahmin işlemi
        mask_path, overlay_path = predict_image(temp_path)
        return {
            "success": True,
            "mask_path": mask_path,
            "overlay_path": overlay_path
        }
    except Exception as e:
        raise HTTPException(500, f"Tahmin hatası: {str(e)}")
    finally:
        # Geçici dosyayı sil
        os.unlink(temp_path)

# Diğer endpoint'ler
@app.get("/imagery/scenes")
def get_scenes():
    return {"scenes": ["scene1", "scene2"]}

@app.post("/aoi/analyze")
def analyze_aoi():
    return {"job_id": "1234", "status": "PENDING"}

@app.get("/results/{job_id}")
def get_results(job_id: str):
    return {"job_id": job_id, "status": "READY", "result": "dummy_geojson"}