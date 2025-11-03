"""FastAPI app exposing endpoints for model training and prediction."""

import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from config import config
from data import SQLiteHandler
from model import VolatilityModel

app = FastAPI()

class FitRequest(BaseModel):
    ticker: str
    refresh_data: bool
    n_points: int
    p: int
    q: int

class FitResponse(FitRequest):
    success: bool
    message: str

class PredictRequest(BaseModel):
    ticker: str
    days: int

class PredictResponse(PredictRequest):
    success: bool
    forecast: dict
    message: str

def create_model_instance(symbol, refresh):
    conn = sqlite3.connect(config.database_name, check_same_thread=False)
    repo = SQLiteHandler(conn)
    return VolatilityModel(ticker=symbol, db_repo=repo, refresh_data=refresh)

@app.get("/ping", status_code=200)
def ping():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/train", status_code=200, response_model=FitResponse)
def train_model(request: FitRequest):
    """Train GARCH model for specified ticker."""
    response = request.dict()
    try:
        model = create_model_instance(request.ticker, request.refresh_data)
        model.prepare_data(request.n_points)
        model.train(request.p, request.q)
        filename = model.save_model()
        response.update(success=True, message=f"Model saved as {filename}.")
    except Exception as e:
        response.update(success=False, message=str(e))
    return response

@app.post("/forecast", status_code=200, response_model=PredictResponse)
def forecast_volatility(request: PredictRequest):
    """Generate future volatility predictions."""
    response = request.dict()
    try:
        model = create_model_instance(request.ticker, False)
        model.load_model()
        predictions = model.predict(request.days)
        response.update(success=True, forecast=predictions, message="")
    except Exception as e:
        response.update(success=False, forecast={}, message=str(e))
    return response
