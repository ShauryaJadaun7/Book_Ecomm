from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    """
    Case-Resilient Settings Core: Manages type-safe configurations for Pydantic V2.
    Uses explicit property proxy methods to support both uppercase and lowercase 
    attribute access patterns across legacy and modern submodules concurrently.
    """
    # Core Application Configuration
    APP_NAME: str = "BookMyBook Backend Engine"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Persistent Storage Matrix
    DATABASE_URL: str

    # High-Speed Memory Layer & Background Task Queue
    REDIS_URL: str

    # Transactional Email Infrastructure
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Secure Payment Gateway
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    # Artificial Intelligence Orchestration
    GEMINI_API_KEY: str
    
    @field_validator("DATABASE_URL", "REDIS_URL", mode="before")
    @classmethod
    def clean_whitespaces(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v
    
    # Centralized WhatsApp Messaging Copy Template
    MARKETPLACE_MESSAGE_TEMPLATE: str = (
        "Hello {owner_name}! I saw your asset listing for '{title}' priced at "
        "₹{price} on BookMyBook. Let's arrange an exchange window!"
    )

    # ====================================================================
    # 🛡️ CASE-AGNOSTIC ATTRIBUTE PROXIES (Bridges Mixed Casing Files)
    # ====================================================================
    @property
    def database_url(self) -> str: return self.DATABASE_URL
    
    @property
    def redis_url(self) -> str: return self.REDIS_URL
    
    @property
    def smtp_host(self) -> str: return self.SMTP_HOST
    @property
    def smtp_port(self) -> int: return self.SMTP_PORT
    @property
    def smtp_user(self) -> str: return self.SMTP_USER
    @property
    def smtp_password(self) -> str: return self.SMTP_PASSWORD
    
    @property
    def razorpay_key_id(self) -> str: return self.RAZORPAY_KEY_ID
    @property
    def razorpay_key_secret(self) -> str: return self.RAZORPAY_KEY_SECRET
    
    @property
    def gemini_api_key(self) -> str: return self.GEMINI_API_KEY
    
    @property
    def marketplace_message_template(self) -> str: return self.MARKETPLACE_MESSAGE_TEMPLATE

    # Pydantic V2 Configuration Environment Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Softly discards arbitrary system environment flags
    )


# Instantiate the global application configuration context scope
settings = Settings()