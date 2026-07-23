from pathlib import Path
from datetime import datetime

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
)
from services.audit_logger import AuditLogger
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from auth.auth import create_access_token
from auth.dependencies import ( 
    get_current_user,
    require_admin,)
from auth.users import USERS

from monitoring.model_monitor import ModelMonitor

from inference.predictor import (
    predict,
    DRIFT_MONITOR,
    METADATA,
)

from inference.schemas import (
    PredictionRequest,
    PredictionResponse,
    ModelListResponse,
    ModelInfoResponse,
    MonitoringResponse,
    ActivateModelRequest,
    RegisterModelRequest,
    OperationResponse,
)

from services.feature_validator import (
    FeatureValidationError,
)
from services.model_registry import ModelRegistry
from services.model_manager import ModelManager


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# Model Services
# ==========================================================

registry = ModelRegistry(
    BASE_DIR / "models" / "registry.json"
)

model_manager = ModelManager(BASE_DIR)


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(
    title="Fraud Detection API",
    description="Real-Time Fraud Detection using XGBoost",
    version="1.0.0",
)


# ==========================================================
# Authentication
# ==========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
def root():

    active_model = registry.get_active_model()

    return {
        "message": "Fraud Detection API",
        "version": active_model["version"],
        "active_model": active_model["model_id"],
    }


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
def health():

    active_model = registry.get_active_model()

    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": active_model["version"],
        "active_model": active_model["model_id"],
    }


# ==========================================================
# Login
# ==========================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):

    user = USERS.get(form_data.username)

    if user is None:

        AuditLogger.log(
            username=form_data.username,
            role="UNKNOWN",
            action="LOGIN",
            status="FAILED",
            details="Unknown username",
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not pwd_context.verify(
        form_data.password,
        user["hashed_password"],
    ):

        AuditLogger.log(
            username=user["username"],
            role=user["role"],
            action="LOGIN",
            status="FAILED",
            details="Invalid password",
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"],
        }
    )

    AuditLogger.log(
        username=user["username"],
        role=user["role"],
        action="LOGIN",
        status="SUCCESS",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
    }


# ==========================================================
# Monitoring
# ==========================================================

@app.get(
    "/monitoring",
    response_model=MonitoringResponse,
)
def monitoring(
    current_user=Depends(get_current_user),
):

    return MonitoringResponse(
        **ModelMonitor.get_statistics()
    )
# ==========================================================
# List All Registered Models
# ==========================================================

@app.get(
    "/models",
    response_model=ModelListResponse,
)

def list_models(
    current_user=Depends(get_current_user)
):

    models = registry.list_models()

    active = registry.get_active_model()

    return ModelListResponse(
        active_model=active["model_id"],
        models=[
            ModelInfoResponse(**model)
            for model in models
        ],
    )


# ==========================================================
# Get Active Model
# ==========================================================

@app.get(
    "/models/active",
    response_model=ModelInfoResponse,
)
def get_active_model(
    current_user=Depends(get_current_user),
):

    active_model = registry.get_active_model()

    return ModelInfoResponse(
        **active_model
    )


# ==========================================================
# Get Model By ID
# ==========================================================

@app.get(
    "/models/{model_id}",
    response_model=ModelInfoResponse,
)
def get_model(
    model_id: str,
    current_user=Depends(get_current_user),
):

    model = registry.get_model(model_id)

    if model is None:

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="GET_MODEL",
            status="FAILED",
            details=f"{model_id} not found",
        )

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": f"Model '{model_id}' not found."
            },
        )

    return ModelInfoResponse(
        **model
    )


# ==========================================================
# Activate Model
# ==========================================================

@app.post(
    "/models/activate",
    response_model=OperationResponse,
)
def activate_model(
    request: ActivateModelRequest,
    current_user=Depends(require_admin),
):

    model = registry.get_model(
        request.model_id
    )

    if model is None:

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": (
                    f"Model '{request.model_id}' not found."
                ),
            },
        )

    try:

        model_manager.switch_model(
            request.model_id
        )

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="ACTIVATE_MODEL",
            status="SUCCESS",
            details=request.model_id,
        )

        return OperationResponse(
            success=True,
            message=(
                f"Active model changed to "
                f"'{request.model_id}'."
            ),
        )

    except Exception as e:
        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="ACTIVATE_MODEL",
            status="FAILED",
            details=str(e),
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(e),
            },
        )


# ==========================================================
# Register New Model
# ==========================================================

@app.post(
    "/models/register",
    response_model=OperationResponse,
)
def register_model(
    request: RegisterModelRequest,
    current_user=Depends(require_admin),
):

    if registry.get_model(request.model_id):

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="REGISTER_MODEL",
            status="FAILED",
            details=f"{request.model_id} already exists",
        )

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": (
                    f"Model '{request.model_id}' "
                    "already exists."
                ),
            },
        )

    model_data = request.model_dump()

    model_data["status"] = "INACTIVE"

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    model_data["created_at"] = today
    model_data["updated_at"] = today

    registry.register_model(
        model_data
    )

    AuditLogger.log(
        username=current_user["sub"],
        role=current_user["role"],
        action="REGISTER_MODEL",
        status="SUCCESS",
        details=request.model_id,
    )

    return OperationResponse(
        success=True,
        message=(
            f"Model '{request.model_id}' "
            "registered successfully."
        ),
    )

# ==========================================================
# Prediction Endpoint
# ==========================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_transaction(
    request: PredictionRequest,
):

    try:

        payload = request.model_dump()

        result = predict(payload)

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="PREDICTION",
            status="SUCCESS",
        )

        return PredictionResponse(
            **result
        )

    except FeatureValidationError as e:

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="PREDICTION",
            status="FAILED",
            details=str(e),
        )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        AuditLogger.log(
            username=current_user["sub"],
            role=current_user["role"],
            action="PREDICTION",
            status="FAILED",
            details=str(e),
        )

        import logging
        logging.getLogger(__name__).exception("Prediction error")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )


# ==========================================================
# Drift Monitoring
# ==========================================================

@app.get("/drift")
def get_drift_statistics(
    current_user=Depends(get_current_user),
):

    return DRIFT_MONITOR.detect_drift(
        METADATA
    )


# ==========================================================
# Health Endpoints
# ==========================================================

@app.get("/health/live")
def live():

    return {
        "status": "alive",
    }


@app.get("/health/ready")
def ready():

    active_model = registry.get_active_model()

    return {
        "status": "ready",
        "model": active_model["model_id"],
        "version": active_model["version"],
    }