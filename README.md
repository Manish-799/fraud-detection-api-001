# Fraud Detection API

An end-to-end machine learning backend service for detecting fraudulent financial transactions.

This project uses a trained scikit-learn model served through a FastAPI backend. It supports user authentication, JWT-protected prediction endpoints, prediction history, model metadata, environment-based configuration, Docker support, and database logging.

---

## Features

* Fraud prediction using a trained machine learning model
* FastAPI backend with Swagger documentation
* User registration and login
* JWT authentication
* Protected prediction endpoint
* User-specific prediction history
* SQLAlchemy database integration
* SQLite database for local development
* Persistent local database storage
* Model threshold tuning
* Risk-level scoring
* Environment-based configuration
* Model metadata endpoint
* Docker and Docker Compose support

---

## Tech Stack

* Python
* FastAPI
* scikit-learn
* pandas
* SQLAlchemy
* SQLite
* JWT
* pwdlib Argon2
* Pydantic
* Uvicorn
* Docker
* Docker Compose

---

## Project Structure

```text
fraud_detection/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── security.py
│   ├── exceptions.py
│   │
│   └── ml/
│       ├── train_model.py
│       ├── predictor.py
│       └── fraud_model.pkl
│
├── data/
│   └── fraud.csv
│
├── docs/
│   └── test_flow.md
│
├── storage/
│   ├── .gitkeep
│   └── fraud_detection.db
│
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Dataset

This project uses the PaySim mobile money fraud detection dataset.

Expected dataset columns:

```text
type
amount
oldbalanceOrg
newbalanceOrig
oldbalanceDest
newbalanceDest
isFraud
```

The model uses these input features:

```text
type
amount
oldbalanceOrg
newbalanceOrig
oldbalanceDest
newbalanceDest
```

Target column:

```text
isFraud
```

The dataset file should be placed at:

```text
data/fraud.csv
```

---

## Model Training

The model is trained using a scikit-learn pipeline.

The pipeline includes:

* OneHotEncoder for transaction type
* StandardScaler for numerical features
* RandomForestClassifier for fraud classification

To train the model, run:

```bash
python app/ml/train_model.py
```

The trained model is saved to:

```text
app/ml/fraud_model.pkl
```

The saved model package contains:

* Trained model pipeline
* Selected fraud threshold
* Model version
* scikit-learn version
* Feature list

---

## Model Evaluation

The dataset is highly imbalanced, so accuracy alone is misleading.

A model can achieve very high accuracy by predicting almost every transaction as non-fraud. Therefore, this project evaluates the model using fraud-class focused metrics.

The model is evaluated using:

* Confusion matrix
* Fraud precision
* Fraud recall
* Fraud F1-score
* ROC-AUC
* PR-AUC
* Threshold analysis

The training script tests multiple probability thresholds and selects the best threshold based on F1-score.

Example threshold analysis:

```text
Threshold: 0.2 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.3 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.4 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.5 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.6 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.7 | Precision: ... | Recall: ... | F1: ...
Threshold: 0.8 | Precision: ... | Recall: ... | F1: ...
```

The selected threshold is stored with the model and used during API inference.

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
APP_NAME=Fraud Detection API
APP_VERSION=1.0.0

DATABASE_URL=sqlite:///./storage/fraud_detection.db

SECRET_KEY=change-this-secret-key-later
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MODEL_PATH=app/ml/fraud_model.pkl
DEFAULT_FRAUD_THRESHOLD=0.5
DEFAULT_MODEL_VERSION=v1.0
```

For production, replace `SECRET_KEY` with a secure secret key.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd fraud_detection
```

Replace `<your-repo-url>` with your actual GitHub repository URL.

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env`.

On Windows:

```bash
copy .env.example .env
```

### 5. Add dataset

Place the dataset at:

```text
data/fraud.csv
```

### 6. Train the model

```bash
python app/ml/train_model.py
```

### 7. Run the API server locally

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Docker Setup

Build and run the API using Docker Compose:

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000/docs
```

To stop the container:

```bash
docker compose down
```

The SQLite database is persisted locally at:

```text
storage/fraud_detection.db
```

This allows user accounts and prediction history to remain available after restarting the container.

---

## API Endpoints

| Method | Endpoint                       | Auth Required | Description                                 |
| ------ | ------------------------------ | ------------: | ------------------------------------------- |
| GET    | `/`                            |            No | Root endpoint                               |
| GET    | `/health`                      |            No | Health check                                |
| POST   | `/auth/register`               |            No | Register a new user                         |
| POST   | `/auth/login`                  |            No | Login and get JWT token                     |
| GET    | `/users/me`                    |           Yes | Get current logged-in user                  |
| GET    | `/model/info`                  |           Yes | Get loaded model metadata                   |
| POST   | `/predict`                     |           Yes | Predict whether a transaction is fraudulent |
| GET    | `/predictions`                 |           Yes | Get current user's prediction history       |
| GET    | `/predictions/{prediction_id}` |           Yes | Get one prediction by ID                    |

---

## Authentication Flow

### Register

Endpoint:

```text
POST /auth/register
```

Request body:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

### Login

Endpoint:

```text
POST /auth/login
```

The login endpoint uses form data.

In Swagger UI, enter:

```text
username: test@example.com
password: password123
```

Example response:

```json
{
  "access_token": "your-jwt-token",
  "token_type": "bearer"
}
```

Use this token through Swagger UI's `Authorize` button.

---

## Prediction Example

Endpoint:

```text
POST /predict
```

Request body:

```json
{
  "amount": 181.0,
  "oldbalanceOrg": 181.0,
  "newbalanceOrig": 0.0,
  "oldbalanceDest": 0.0,
  "newbalanceDest": 0.0,
  "type": "TRANSFER"
}
```

Example response:

```json
{
  "prediction_id": 1,
  "prediction": "fraud",
  "risk_level": "high",
  "fraud_probability": 0.999975,
  "threshold_used": 0.5,
  "model_version": "v1.0"
}
```

---

## Model Info Example

Endpoint:

```text
GET /model/info
```

Example response:

```json
{
  "model_version": "v1.0",
  "threshold_used": 0.5,
  "model_type": "Pipeline",
  "features": [
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest"
  ]
}
```

---

## Prediction History

Each prediction is stored in the database and linked to the authenticated user.

Endpoint:

```text
GET /predictions
```

Only the logged-in user's predictions are returned.

Example response:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "transaction_type": "TRANSFER",
    "amount": 181.0,
    "oldbalanceOrg": 181.0,
    "newbalanceOrig": 0.0,
    "oldbalanceDest": 0.0,
    "newbalanceDest": 0.0,
    "prediction": "fraud",
    "fraud_probability": 0.999975,
    "created_at": "2026-07-03T12:00:00"
  }
]
```

---

## Why Accuracy Is Not Enough

Fraud detection datasets are highly imbalanced. Most transactions are non-fraud.

A model can get very high accuracy by predicting every transaction as non-fraud. That is not useful for fraud detection.

This project focuses on:

* Fraud precision
* Fraud recall
* Fraud F1-score
* PR-AUC
* Threshold tuning

These metrics are more useful for evaluating performance on the minority fraud class.

---

## Current Status

Completed:

* FastAPI backend
* ML model training
* Model inference endpoint
* JWT authentication
* User registration and login
* Protected prediction endpoint
* User-specific prediction history
* SQLAlchemy database integration
* SQLite database persistence
* Environment variable configuration
* Model metadata endpoint
* Swagger API documentation
* Dockerfile
* Docker Compose setup

---

## Future Improvements

* PostgreSQL support
* Alembic database migrations
* Rate limiting
* Admin dashboard
* Streamlit frontend
* Better feature engineering
* Model calibration
* Automated tests
* CI/CD pipeline
* Deployment on Render or Railway
