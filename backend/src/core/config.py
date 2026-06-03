from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic automatically maps these variables to the matching keys in the .env file
    DATABASE_URL: str
    REDIS_URL: str
    APP_NAME: str = "BookMyBook Engine"
    DEBUG: bool = False
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Configuration class telling Pydantic where to look for the environment file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instantiate a global settings object to import across the project
settings = Settings()