from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import pandas as pd
import os
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time

# Métricas de Prometheus
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['method', 'endpoint'])
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')

app = FastAPI(title="Adult Income Prediction API", version="1.0.0")

# Cargar modelo de MLflow
MODEL_NAME = os.getenv("MODEL_NAME", "adult-income")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "champion")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

try:
    model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Model loaded successfully from {model_uri}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


class PredictionInput(BaseModel):
    age: int
    workclass: str
    fnlwgt: int
    education: str
    education_num: int
    marital_status: str
    occupation: str
    relationship: str
    race: str
    sex: str
    capital_gain: int
    capital_loss: int
    hours_per_week: int
    native_country: str

    class Config:
        json_schema_extra = {
            "example": {
                "age": 39,
                "workclass": "State-gov",
                "fnlwgt": 77516,
                "education": "Bachelors",
                "education_num": 13,
                "marital_status": "Never-married",
                "occupation": "Adm-clerical",
                "relationship": "Not-in-family",
                "race": "White",
                "sex": "Male",
                "capital_gain": 2174,
                "capital_loss": 0,
                "hours_per_week": 40,
                "native_country": "United-States"
            }
        }


@app.get("/")
async def root():
    """Health check endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    return {
        "message": "Adult Income Prediction API",
        "version": "1.0.0",
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    start_time = time.time()
    
    health_status = {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "model_name": MODEL_NAME,
        "model_alias": MODEL_ALIAS,
        "mlflow_uri": MLFLOW_TRACKING_URI
    }
    
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method='GET', endpoint='/health').observe(latency)
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
    
    return health_status


@app.post("/predict")
async def predict(input_data: PredictionInput):
    """Make a prediction"""
    start_time = time.time()
    
    if model is None:
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='500').inc()
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Convertir input a DataFrame
        input_dict = input_data.dict()
        df = pd.DataFrame([input_dict])
        
        # Hacer predicción
        prediction = model.predict(df)
        
        # Incrementar contador de predicciones
        PREDICTION_COUNT.inc()
        
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method='POST', endpoint='/predict').observe(latency)
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()
        
        return {
            "prediction": int(prediction[0]),
            "prediction_label": ">50K" if prediction[0] == 1 else "<=50K",
            "latency_seconds": round(latency, 4)
        }
    
    except Exception as e:
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")