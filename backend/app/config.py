from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


import os

class Settings(BaseSettings):
    app_name: str = "Mood-Based Music Recommendation System"
    database_url: str = "sqlite:////tmp/mood_music.db" if os.environ.get("VERCEL") else "sqlite:///./mood_music.db"
    catalog_path: str = str(Path(__file__).resolve().parents[1] / "data" / "sample_spotify_tracks.csv")
    deepface_home: str = "/tmp/.models" if os.environ.get("VERCEL") else str(PROJECT_ROOT / ".models")
    emotion_provider: str = "deepface"
    top_k_candidates: int = 300
    recommendation_count: int = 10
    smoothing_window: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MOOD_MUSIC_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
