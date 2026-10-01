"""
FastAPI backend using the trained model to create precictions via website.

Run Locally: 
    uvicorn app:app

Then open http://127.0.0.1:8000/docs
"""

import json 

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core import load_model, predict_difficulty

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

model = load_model()

# Main root of website
@app.get("/")
def root():
    return {"message": "Web app is running"}

# Upload route 
@app.post("/files/upload")
async def upload(file: UploadFile):
    contents = await file.read()
    level_json = json.loads(contents)

    tier, raw_score = predict_difficulty(level_json, model)

    return {
        "predicted_difficulty": tier,
        "raw_score": round(float(raw_score), 2),
    }
