from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = 'Football Data Platform'
    API_V1_STR: str = '/api/v1'
    DEBUG: bool = False
    MONGODB_URL: str = 'mongodb://localhost:27017'
    MONGODB_DB_STATSBOMB_RAW: str = 'statsbomb_raw'
    MONGODB_DB_UNDERSTAT_RAW: str = 'understat_raw'
    MONGODB_DB_FBREF_RAW: str = 'fbref_raw'
    MONGODB_DB_UNIFIED: str = 'football_unified'
    SECRET_KEY: Optional[str] = None
    RATE_LIMIT_GLOBAL: str = '60/minute'
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True)
settings = Settings()