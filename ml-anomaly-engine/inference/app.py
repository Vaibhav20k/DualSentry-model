from fastapi import FastAPI
from fastapi.responses import JSONResponse

from inference.schemas import (
    PredictionRequest,
    PredictionResponse,
)

from inference.predictor import (
    predict,
    MODEL_VERSION,
)


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(

    title="Fraud Detection API",

    description="Real-Time Fraud Detection using XGBoost",

    version="1.0.0",

)


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")

def health():

    return {

        "status": "healthy",

        "model_loaded": True,

        "model_version": MODEL_VERSION,

    }


# ==========================================================
# Root
# ==========================================================

@app.get("/")

def root():

    return {

        "message": "Fraud Detection API",

        "version": MODEL_VERSION,

    }


# ==========================================================
# Prediction Endpoint
# ==========================================================

@app.post(

    "/predict",

    response_model=PredictionResponse,

)

def make_prediction(

    request: PredictionRequest,

):

    try:

        result = predict(

            request.model_dump()

        )

        return PredictionResponse(

            **result

        )

    except Exception as e:

        return JSONResponse(

            status_code=500,

            content={

                "error": str(e)

            },

        )