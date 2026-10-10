from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SANKET - AI Flood Early-Warning System"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/sanket.db"
    SHARED_DATA_DIR: Path = ROOT_DIR / "data"

    class Config:
        case_sensitive = True

settings = Settings()
