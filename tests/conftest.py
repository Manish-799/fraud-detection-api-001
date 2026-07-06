import os

import pytest


os.environ["DATABASE_URL"] = (
    "sqlite:///./storage/test_fraud_detection.db"
)
os.environ["SECRET_KEY"] = "test-secret-key"


from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client