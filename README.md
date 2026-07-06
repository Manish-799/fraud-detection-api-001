# Fraud Detection API

A production-oriented machine learning backend for real-time financial transaction fraud detection.

The project serves a trained scikit-learn fraud detection pipeline through a JWT-secured FastAPI REST API. It supports authenticated predictions, user-specific prediction history, PostgreSQL persistence, model metadata, Dockerized deployment, and probability-threshold tuning for an imbalanced fraud dataset.

## Live API

**Swagger UI:**
https://fraud-detection-api-tzp4.onrender.com/docs

**Health Check:**
https://fraud-detection-api-tzp4.onrender.com/health

> The API is hosted on Render. The first request may take longer when the free service is inactive.

---

## Features

* Real-time fraud probability prediction
* FastAPI REST API with interactive OpenAPI/Swagger documentation
* User registration and login
* JWT-based authentication
* Argon2 password hashing
* Protected prediction endpoints
* User-specific prediction history
* SQLAlchemy ORM integration
* PostgreSQL persistence in production
* SQLite support for local development
* Validation-based classification threshold tuning
* Fraud risk-level scoring
* Model version and metadata endpoint
* Environment-based configuration
* Docker and Docker Compose support
* Render deployment

---

## Tech Stack

### Backend

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic

### Machine Learning

* scikit-learn
* pandas
* Random Forest Classifier
* joblib

### Authentication

* JSON Web Tokens
* python-jose
* Argon2 password hashing through pwdlib

### Database

* SQLAlchemy
* PostgreSQL with Neon in production
* SQLite for local development
* Psycopg 3

### Deployment

* Docker
* Docker Compose
* Render
* Neon PostgreSQL

---

## Architecture

```text
                         Client / Swagger UI
                                  |
                                  v
                           FastAPI REST API
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
          JWT Authentication                Prediction Endpoint
                 |                                 |
                 v                                 v
             User Identity                 ML Inference Pipeline
                                                    |
                                                    v
                                          Fraud Probability
                                                    |
                                                    v
                                      Validation-Selected Threshold
                                                    |
                                                    v
                                      Prediction + Risk Level
                                                    |
                 +----------------------------------+
                 |
                 v
          PostgreSQL Database
                 |
          +------+------+
          |             |
        Users      Prediction History
```

---

## Project Structure

```text
fraud-detection-api/
|
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
│   └── .gitkeep
│
├── storage/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The raw dataset and local SQLite database are excluded from Git.

The trained model artifact is included so the API can perform inference immediately after setup without retraining the model.

---

## Dataset

The project uses the PaySim mobile money fraud detection dataset.

The model uses the following transaction features:

```text
type
amount
oldbalanceOrg
newbalanceOrig
oldbalanceDest
newbalanceDest
```

Target:

```text
isFraud
```

The training sample contains 1,000,000 transactions:

| Class     | Samples |
| --------- | ------: |
| Non-fraud | 998,734 |
| Fraud     |   1,266 |

The severe class imbalance makes accuracy alone unsuitable as the primary evaluation metric.

---

## Model Training Pipeline

The machine learning pipeline consists of:

```text
Transaction Data
       |
       v
ColumnTransformer
       |
       +---- Transaction Type ----> OneHotEncoder
       |
       +---- Numerical Features ---> StandardScaler
       |
       v
RandomForestClassifier
       |
       v
Fraud Probability
```

The Random Forest is configured with class balancing to account for the highly imbalanced target distribution.

The complete preprocessing and classifier pipeline is persisted using `joblib`.

The saved model package contains:

* trained scikit-learn pipeline;
* selected fraud threshold;
* model version;
* scikit-learn version;
* expected feature list.

---

## Train, Validation and Test Strategy

The 1,000,000 transaction sample is split into:

| Dataset    | Percentage | Samples |
| ---------- | ---------: | ------: |
| Training   |        70% | 700,000 |
| Validation |        15% | 150,000 |
| Test       |        15% | 150,000 |

The training set is used to fit the model.

The validation set is used to select the binary fraud classification threshold based on fraud-class F1 score.

The test set remains untouched during threshold selection and is used only for final model evaluation.

```text
Training Set
     |
     v
Fit ML Pipeline

Validation Set
     |
     v
Threshold Analysis
     |
     v
Select Best Threshold

Untouched Test Set
     |
     v
Final Evaluation
```

---

## Threshold Analysis

Fraud classification is not performed using the default `0.5` probability threshold automatically.

Multiple thresholds are evaluated on the validation set:

| Threshold |  Precision |     Recall |         F1 |
| --------: | ---------: | ---------: | ---------: |
|       0.2 |     0.0502 |     0.9737 |     0.0955 |
|       0.3 |     0.0716 |     0.9632 |     0.1333 |
|       0.4 |     0.1078 |     0.9474 |     0.1937 |
|       0.5 |     0.1525 |     0.9316 |     0.2620 |
|       0.6 |     0.2182 |     0.9105 |     0.3520 |
|       0.7 |     0.3340 |     0.8842 |     0.4848 |
|   **0.8** | **0.5236** | **0.8158** | **0.6379** |

The best validation F1 score is obtained at:

```text
Fraud Threshold = 0.8
```

The selected threshold is stored with the trained model and loaded by the inference service.

---

## Final Test Performance

The selected threshold is evaluated on the untouched 150,000-transaction test set.

### Fraud Class Metrics

| Metric    |  Score |
| --------- | -----: |
| Precision |   0.55 |
| Recall    |   0.86 |
| F1 Score  |   0.67 |
| ROC-AUC   | 0.9992 |
| PR-AUC    | 0.8643 |

### Confusion Matrix

```text
                 Predicted
               Normal   Fraud

Actual Normal   149675    135
Actual Fraud        26    164
```

The model detected 164 of 190 fraudulent transactions in the test set while falsely flagging 135 legitimate transactions.

Because fraud represents a very small fraction of the dataset, the project focuses primarily on fraud recall, fraud precision, fraud F1 score and PR-AUC rather than overall accuracy.

---

## API Endpoints

| Method | Endpoint                       | Authentication | Description                    |
| ------ | ------------------------------ | -------------- | ------------------------------ |
| GET    | `/`                            | No             | API root                       |
| GET    | `/health`                      | No             | Service health check           |
| POST   | `/auth/register`               | No             | Register a user                |
| POST   | `/auth/login`                  | No             | Login and obtain a JWT         |
| GET    | `/users/me`                    | Yes            | Get authenticated user         |
| GET    | `/model/info`                  | Yes            | Get loaded model metadata      |
| POST   | `/predict`                     | Yes            | Run fraud inference            |
| GET    | `/predictions`                 | Yes            | Get user prediction history    |
| GET    | `/predictions/{prediction_id}` | Yes            | Get a specific user prediction |

---

## Authentication Flow

```text
Register
   |
   v
Password hashed using Argon2
   |
   v
User stored in PostgreSQL

Login
   |
   v
Credentials verified
   |
   v
JWT access token issued

Authenticated Request
   |
   v
Bearer token validated
   |
   v
Current user resolved
   |
   v
Protected endpoint executed
```

### Register

```http
POST /auth/register
```

Example request:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

### Login

```http
POST /auth/login
```

The login endpoint accepts OAuth2-compatible form data.

Example:

```text
username: test@example.com
password: password123
```

Successful authentication returns:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

The token can be supplied through Swagger UI using the `Authorize` button.

---

## Prediction Example

```http
POST /predict
```

Example request:

```json
{
  "type": "TRANSFER",
  "amount": 181,
  "oldbalanceOrg": 181,
  "newbalanceOrig": 0,
  "oldbalanceDest": 0,
  "newbalanceDest": 0
}
```

Example response:

```json
{
  "prediction_id": 1,
  "prediction": "fraud",
  "risk_level": "high",
  "fraud_probability": 0.999975,
  "threshold_used": 0.8,
  "model_version": "v1.0"
}
```

The binary fraud decision uses the validation-selected model threshold.

Risk level is a separate descriptive probability band and does not determine the binary fraud classification.

---

## Prediction History

Every prediction is associated with the authenticated user and persisted in the database.

```http
GET /predictions
```

Only predictions owned by the currently authenticated user are returned.

A user cannot retrieve another user's prediction by supplying its prediction ID.

---

## Model Metadata

```http
GET /model/info
```

The endpoint exposes metadata about the currently loaded inference artifact.

Example:

```json
{
  "model_version": "v1.0",
  "threshold_used": 0.8,
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

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Manish-799/fraud-detection-api-001.git
cd fraud-detection-api-001
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment configuration

Copy `.env.example` to `.env`.

Windows:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

For local development, SQLite can be used:

```env
DATABASE_URL=sqlite:///./storage/fraud_detection.db
SECRET_KEY=replace-with-a-secure-secret
```

### 5. Start the API

The trained model artifact is already included in the repository.

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Retraining the Model

Retraining requires the PaySim dataset.

Place the dataset at:

```text
data/fraud.csv
```

Run:

```bash
python -m app.ml.train_model
```

The newly trained artifact is saved to:

```text
app/ml/fraud_model.pkl
```

Threshold selection is performed on the validation set before final evaluation on the untouched test set.

---

## Docker

Build the image:

```bash
docker build -t fraud-detection-api .
```

Run locally:

```bash
docker run --rm -p 8000:8000 --env-file .env fraud-detection-api
```

The container reads the server port from the `PORT` environment variable and defaults to port `8000` for local execution.

Docker Compose is also supported:

```bash
docker compose up --build
```

---

## Production Deployment

The API is deployed using:

```text
GitHub
   |
   v
Render Docker Web Service
   |
   v
FastAPI + ML Inference
   |
   v
Neon PostgreSQL
```

Render builds the service directly from the repository Dockerfile.

Production secrets and the PostgreSQL connection URL are supplied through environment variables and are not committed to Git.

---

## Future Improvements

* Automated API tests
* GitHub Actions CI pipeline
* Alembic database migrations
* Persist model version and decision threshold with each prediction record
* Model probability calibration
* Advanced fraud feature engineering
* Rate limiting

---

## Disclaimer

This project is an educational machine learning and backend engineering system.

It is not intended for real-world financial decision-making without further model validation, calibration, monitoring, security review and domain-specific risk controls.
