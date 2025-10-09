from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Template WebApp"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str

    # Fuseki
    FUSEKI_URL: str = "http://localhost:3030"
    FUSEKI_DATASET: str = "template_dataset"
    FUSEKI_ADMIN_USER: str = "admin"
    FUSEKI_ADMIN_PASSWORD: str = "admin"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # SLD Generator Configuration - Layout
    SLD_BUSBAR_HEIGHT: int = 80
    SLD_BAY_WIDTH: int = 150
    SLD_EQUIPMENT_HEIGHT: int = 40
    SLD_EQUIPMENT_WIDTH: int = 100
    SLD_VERTICAL_SPACING: int = 60
    SLD_HORIZONTAL_SPACING: int = 50
    SLD_MARGIN: int = 50

    # SLD Generator Configuration - Colors (hex without #)
    SLD_COLOR_CBR: str = "FF6B6B"  # Breaker - Red
    SLD_COLOR_DIS: str = "4ECDC4"  # Disconnector - Cyan
    SLD_COLOR_CTR: str = "95E1D3"  # Current Transformer - Light Green
    SLD_COLOR_VTR: str = "F38181"  # Voltage Transformer - Pink
    SLD_COLOR_PTR: str = "AA96DA"  # Power Transformer - Purple
    SLD_COLOR_CAP: str = "FCBAD3"  # Capacitor - Light Pink
    SLD_COLOR_REA: str = "FFFFD2"  # Reactor - Yellow
    SLD_COLOR_GEN: str = "A8D8EA"  # Generator - Light Blue
    SLD_COLOR_BAT: str = "FED766"  # Battery - Yellow
    SLD_COLOR_DEFAULT: str = "CCCCCC"  # Default - Gray

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
