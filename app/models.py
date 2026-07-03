from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship(
        "Prediction",
        back_populates="user",
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    oldbalanceOrg = Column(Float, nullable=False)
    newbalanceOrig = Column(Float, nullable=False)

    oldbalanceDest = Column(Float, nullable=False)
    newbalanceDest = Column(Float, nullable=False)

    prediction = Column(String, nullable=False)
    fraud_probability = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="predictions",
    )