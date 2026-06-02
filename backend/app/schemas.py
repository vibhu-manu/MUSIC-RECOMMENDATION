from typing import Dict, List, Optional
from pydantic import BaseModel, Field


EMOTIONS = ["happy", "sad", "angry", "fear", "surprise", "disgust", "love"]

class EmotionRequest(BaseModel):
    image_base64: Optional[str] = Field(default=None, description="Webcam frame as base64 data URL or raw base64.")
    session_id: str
    user_id: str = "demo-user"
    reset_smoothing: bool = False


class EmotionResponse(BaseModel):
    emotion: str
    probabilities: Dict[str, float]
    smoothed_probabilities: Dict[str, float]
    provider: str
    provider_error: Optional[str] = None


class RecommendationRequest(BaseModel):
    user_id: str = "demo-user"
    session_id: str
    probabilities: Dict[str, float]
    limit: int = 10
    language: str = "english"


class SongRecommendation(BaseModel):
    song_id: str
    track_name: str
    artist_name: str
    genre: str
    language: str
    valence: float
    energy: float
    tempo: float
    danceability: float
    popularity: float
    rank_score: float
    mood_match_score: float
    reasons: List[str]


class RecommendationResponse(BaseModel):
    recommendation_id: str
    emotion_embedding: List[float]
    recommendations: List[SongRecommendation]


class FeedbackRequest(BaseModel):
    user_id: str = "demo-user"
    session_id: str
    recommendation_id: str
    song_id: str
    action: str = Field(pattern="^(like|dislike|skip)$")


class FeedbackResponse(BaseModel):
    status: str
    user_embedding: List[float]
