from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import settings

from app import crud, models
from app.database import engine, get_db
#from app.ml.predictor import predict_transaction
from fastapi.responses import JSONResponse

from app.exceptions import ModelPredictionError
from app.ml.predictor import get_model_info, predict_transaction

from app.schemas import (
    PredictionRecord,
    PredictionResponse,
    Token,
    TransactionInput,
    UserCreate,
    UserResponse,
    ModelInfoResponse,
)

from app.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API for predicting fraudulent transactions",
    version=settings.app_version,
)

@app.exception_handler(ModelPredictionError)
def model_prediction_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Model prediction failed. Please check transaction input format."
        },
    )

@app.get("/")
def root():
    return {
        "message": "Welcome to Fraud Detection API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Fraud Detection API is running",
    }

@app.get("/model/info", response_model=ModelInfoResponse)
def model_info(
    current_user: models.User = Depends(get_current_user),
):
    return get_model_info()


@app.post("/auth/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = crud.get_user_by_email(
        db=db,
        email=user.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    return crud.create_user(
        db=db,
        user=user,
        hashed_password=hashed_password,
    )


@app.post("/auth/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: models.User = Depends(get_current_user),
):
    return current_user


@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(
    transaction: TransactionInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction_data = transaction.model_dump()

    result = predict_transaction(transaction_data)

    db_prediction = crud.create_prediction_record(
        db=db,
        transaction=transaction,
        prediction=result["prediction"],
        fraud_probability=result["fraud_probability"],
        user_id=current_user.id,
    )

    return PredictionResponse(
        prediction_id=db_prediction.id,
        prediction=result["prediction"],
        risk_level=result["risk_level"],
        fraud_probability=result["fraud_probability"],
        threshold_used=result["threshold_used"],
        model_version=result["model_version"],
    )


@app.get("/predictions", response_model=List[PredictionRecord])
def read_predictions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_predictions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@app.get("/predictions/{prediction_id}", response_model=PredictionRecord)
def read_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    prediction = crud.get_prediction_by_id(
        db=db,
        prediction_id=prediction_id,
        user_id=current_user.id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return prediction