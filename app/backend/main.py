from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from pipeline import score_wallet
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] if you want specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/trust_score_model.pkl"
SCALER_PATH = "models/trust_score_scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

class WalletRequest(BaseModel):
    wallet_address: str

@app.get("/")
def read_root():
    return {"message": "WIRE-Wallet FastAPI is running"}

@app.post("/score_wallet")
def score_wallet_api(req: WalletRequest):
    try:
        result = score_wallet(
            wallet_address=req.wallet_address,
            model=model,
            scaler=scaler
        )
        return {
            "wallet": result['wallet'],
            "score": result['score'],
            "label": result['label'],
            "flags": result['flags']
        }
    except Exception as e:
        return {"error": str(e)}
