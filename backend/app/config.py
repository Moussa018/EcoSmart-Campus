import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "EcoSmart Campus API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # Security & JWT
    SECRET_KEY: str = "supersecret_ecosmart_jwt_key_change_in_production_!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ecosmart:ecosmart_secret@localhost:5432/ecosmart_db"
    SYNC_DATABASE_URL: str = "postgresql://ecosmart:ecosmart_secret@localhost:5432/ecosmart_db"

    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_BROKER_WS_PORT: int = 9001
    MQTT_KEEPALIVE: int = 60

    # LLM Assistant
    LLM_MODEL: str = "mock:demo"
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
