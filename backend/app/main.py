from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from backend.app.config import get_settings
from backend.app.database import db_session, ensure_user_and_session, init_database
from backend.app.recommender.catalog import Song, load_catalog, upsert_catalog
from backend.app.recommender.embeddings import emotion_embedding
from backend.app.recommender.emotion import EmotionSmoother, build_detector
from backend.app.recommender.personalization import get_user_embedding, update_user_embedding
from backend.app.recommender.ranker import rank_candidates
from backend.app.recommender.retrieval import RetrievalEngine
from backend.app.schemas import (
    EmotionRequest,
    EmotionResponse,
    FeedbackRequest,
    FeedbackResponse,
    RecommendationRequest,
    RecommendationResponse,
    SongRecommendation,
)


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = build_detector(settings.emotion_provider, deepface_home=settings.deepface_home)
smoother = EmotionSmoother(settings.smoothing_window)
songs: list[Song] = []
retrieval_engine: RetrievalEngine | None = None


@app.on_event("startup")
def startup() -> None:
    global songs, retrieval_engine
    init_database()
    songs = load_catalog(settings.catalog_path)
    upsert_catalog(songs)
    retrieval_engine = RetrievalEngine(songs)


@app.get("/api/health")
def health() -> Dict[str, object]:
    return {
        "status": "ok",
        "catalog_size": len(songs),
        "configured_emotion_provider": settings.emotion_provider,
        "active_emotion_provider": detector.provider_name,
        "emotion_provider_error": detector.last_error,
        "retrieval": "faiss" if retrieval_engine and retrieval_engine.index is not None else "numpy",
    }


@app.post("/api/emotion", response_model=EmotionResponse)
def detect_emotion(request: EmotionRequest) -> EmotionResponse:
    ensure_user_and_session(request.user_id, request.session_id)
    if request.reset_smoothing:
        smoother.clear(request.session_id)
    probabilities = detector.predict(request.image_base64)
    smoothed = smoother.add(request.session_id, probabilities)
    top_emotion = max(smoothed, key=smoothed.get)
    with db_session() as conn:
        conn.execute(
            text(
                """
                INSERT INTO emotion_history (
                    session_id, user_id, probabilities, smoothed_probabilities, top_emotion, created_at
                )
                VALUES (:session_id, :user_id, :probabilities, :smoothed, :top_emotion, :created_at)
                """
            ),
            {
                "session_id": request.session_id,
                "user_id": request.user_id,
                "probabilities": json.dumps(probabilities),
                "smoothed": json.dumps(smoothed),
                "top_emotion": top_emotion,
                "created_at": datetime.utcnow(),
            },
        )
    return EmotionResponse(
        emotion=top_emotion,
        probabilities=probabilities,
        smoothed_probabilities=smoothed,
        provider=detector.provider_name,
        provider_error=detector.last_error,
    )


def _feedback_counts() -> Dict[str, Dict[str, int]]:
    counts: Dict[str, Dict[str, int]] = {}
    with db_session() as conn:
        rows = conn.execute(text("SELECT song_id, action, COUNT(*) FROM feedback GROUP BY song_id, action")).all()
    for song_id, action, count in rows:
        counts.setdefault(song_id, {})[action] = int(count)
    return counts


@app.post("/api/recommendations", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    ensure_user_and_session(request.user_id, request.session_id)
    if retrieval_engine is None:
        raise RuntimeError("Retrieval engine not initialized")
    query_embedding = emotion_embedding(request.probabilities)
    candidates = retrieval_engine.search(query_embedding, settings.top_k_candidates)
    user_embedding = get_user_embedding(request.user_id, len(query_embedding))
    ranked = rank_candidates(candidates, user_embedding, request.limit, _feedback_counts(), request.probabilities, request.language)
    recommendation_id = str(uuid.uuid4())
    song_ids = [song.song_id for song, _, _ in ranked]
    with db_session() as conn:
        conn.execute(
            text(
                """
                INSERT INTO recommendations (
                    recommendation_id, user_id, session_id, emotion_embedding, song_ids, created_at
                )
                VALUES (:recommendation_id, :user_id, :session_id, :embedding, :song_ids, :created_at)
                """
            ),
            {
                "recommendation_id": recommendation_id,
                "user_id": request.user_id,
                "session_id": request.session_id,
                "embedding": json.dumps(query_embedding),
                "song_ids": json.dumps(song_ids),
                "created_at": datetime.utcnow(),
            },
        )
    recommendations = [
        SongRecommendation(
            song_id=song.song_id,
            track_name=song.track_name,
            artist_name=song.artist_name,
            genre=song.genre,
            language=song.language,
            valence=song.features["valence"],
            energy=song.features["energy"],
            tempo=song.features["tempo"],
            danceability=song.features["danceability"],
            popularity=song.popularity,
            rank_score=score,
            reasons=reasons,
        )
        for song, score, reasons in ranked
    ]
    return RecommendationResponse(
        recommendation_id=recommendation_id,
        emotion_embedding=query_embedding,
        recommendations=recommendations,
    )


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    ensure_user_and_session(request.user_id, request.session_id)
    song = next((item for item in songs if item.song_id == request.song_id), None)
    if song is None:
        raise RuntimeError("Song not found")
    with db_session() as conn:
        conn.execute(
            text(
                """
                INSERT INTO feedback (user_id, song_id, session_id, recommendation_id, action, created_at)
                VALUES (:user_id, :song_id, :session_id, :recommendation_id, :action, :created_at)
                """
            ),
            {
                "user_id": request.user_id,
                "song_id": request.song_id,
                "session_id": request.session_id,
                "recommendation_id": request.recommendation_id,
                "action": request.action,
                "created_at": datetime.utcnow(),
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO listening_history (user_id, song_id, session_id, event_type, created_at)
                VALUES (:user_id, :song_id, :session_id, :event_type, :created_at)
                """
            ),
            {
                "user_id": request.user_id,
                "song_id": request.song_id,
                "session_id": request.session_id,
                "event_type": request.action,
                "created_at": datetime.utcnow(),
            },
        )
    embedding = update_user_embedding(request.user_id, song.embedding, request.action)
    return FeedbackResponse(status="recorded", user_embedding=embedding)


frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
