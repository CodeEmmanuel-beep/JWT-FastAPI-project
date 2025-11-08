from pydantic_settings import BaseSettings


class SETTINGS(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SENDGRID_API_KEY: str
    SENDGRID_SENDER: str
    SECRET_KEY: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    DATABASE_URL: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DEBUG: bool = False
    model_config = {"env_file": ".env"}


settings = SETTINGS()
