from sqlalchemy.orm import Session

from app import models
from app.schemas import TransactionInput, UserCreate


def get_user_by_email(db: Session, email: str):
    normalized_email = email.lower()

    return (
        db.query(models.User)
        .filter(models.User.email == normalized_email)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
    hashed_password: str,
):
    db_user = models.User(
        email=str(user.email).lower(),
        hashed_password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_prediction_record(
    db: Session,
    transaction: TransactionInput,
    prediction: str,
    fraud_probability: float,
    user_id: int,
):
    db_prediction = models.Prediction(
        user_id=user_id,
        transaction_type=transaction.type,
        amount=transaction.amount,
        oldbalanceOrg=transaction.oldbalanceOrg,
        newbalanceOrig=transaction.newbalanceOrig,
        oldbalanceDest=transaction.oldbalanceDest,
        newbalanceDest=transaction.newbalanceDest,
        prediction=prediction,
        fraud_probability=fraud_probability,
    )

    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction


def get_predictions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
):
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_prediction_by_id(
    db: Session,
    prediction_id: int,
    user_id: int,
):
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.id == prediction_id)
        .filter(models.Prediction.user_id == user_id)
        .first()
    )