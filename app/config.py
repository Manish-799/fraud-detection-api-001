from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fraud Detection API"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./fraud_detection.db"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_path: str = "app/ml/fraud_model.pkl"
    default_fraud_threshold: float = 0.5
    default_model_version: str = "v1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()