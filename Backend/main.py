from fastapi import FastAPI

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
