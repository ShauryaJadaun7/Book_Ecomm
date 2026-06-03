from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic automatically maps these variables to the matching keys in the .env file
    DATABASE_URL: str
    REDIS_URL: str
    APP_NAME: str = "BookMyBook Engine"
    DEBUG: bool = False
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    gemini_api_key: str

    # Configuration class layout
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 🧠 Changing this from "forbid" to "ignore" stops Pydantic from crashing
        # if extra/unmapped environment variables exist on your system.
        extra="ignore" 
    )

settings = Settings()