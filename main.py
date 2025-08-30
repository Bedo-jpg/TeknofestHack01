from fastapi import FastAPI, UploadFile, File
from src.inference import predict_image  # birazdan inference.py’ye ekleyeceğiz

app = FastAPI()

@app.get("/imagery/scenes")
def get_scenes():
    return {"scenes": ["scene1", "scene2"]}

@app.post("/aoi/analyze")
def analyze_aoi():
    return {"job_id": "1234", "status": "PENDING"}

@app.get("/results/{job_id}")
def get_results(job_id: str):
    return {"job_id": job_id, "status": "READY", "result": "dummy_geojson"}

# =========================
# Yeni Eklenen: Prediction
# =========================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Upload edilen dosyayı geçici kaydet
    input_path = f"temp_{file.filename}"
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # inference.py’den model tahmini al
    mask_path, overlay_path = predict_image(input_path)

    return {
        "mask_path": mask_path,
        "overlay_path": overlay_path
    }