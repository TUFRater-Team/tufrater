"""
FastAPI backend using the trained model to create precictions via website.

Run Locally: 
    uvicorn app:app -- reload

Then open http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, UploadFile
from core import load_model, safe_parse_level, predict_difficulty, extract_gameplay_features
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
model = load_model()

@app.get("/")
def main():
    return {"message": "Server is running"}

@app.post("/files/upload")
async def predict(file: UploadFile):
    contents = await file.read()
    level_json = safe_parse_level(contents)
    features = extract_gameplay_features(level_json)
    tier, raw_number = predict_difficulty(level_json, model)
    return {"difficulty": tier, "raw_score": raw_number, "features": features}    
