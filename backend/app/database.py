from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from backend.app.config import get_settings


def _connect_args(database_url: str) -> dict:
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


engine: Engine = create_engine(
    get_settings().database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args(get_settings().database_url),
)


@contextmanager
def db_session():
    with engine.begin() as conn:
        yield conn


def init_database() -> None:
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            display_name TEXT,
            user_embedding TEXT,
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            started_at TIMESTAMP NOT NULL,
            ended_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS songs (
            song_id TEXT PRIMARY KEY,
            track_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            genre TEXT NOT NULL,
            language TEXT NOT NULL,
            popularity REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS song_features (
            song_id TEXT PRIMARY KEY,
            valence REAL NOT NULL,
            energy REAL NOT NULL,
            tempo REAL NOT NULL,
            danceability REAL NOT NULL,
            acousticness REAL NOT NULL,
            speechiness REAL NOT NULL,
            instrumentalness REAL NOT NULL,
            liveness REAL NOT NULL,
            loudness REAL NOT NULL,
            embedding TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS emotion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            probabilities TEXT NOT NULL,
            smoothed_probabilities TEXT NOT NULL,
            top_emotion TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS listening_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            song_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            song_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            recommendation_id TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            emotion_embedding TEXT NOT NULL,
            song_ids TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """,
    ]
    with db_session() as conn:
        for statement in ddl:
            conn.execute(text(statement))


def ensure_user_and_session(user_id: str, session_id: str) -> None:
    now = datetime.utcnow()
    with db_session() as conn:
        exists = conn.execute(text("SELECT 1 FROM users WHERE user_id=:user_id"), {"user_id": user_id}).first()
        if not exists:
            conn.execute(
                text("INSERT INTO users (user_id, display_name, user_embedding, created_at) VALUES (:u, :d, :e, :c)"),
                {"u": user_id, "d": "Demo User", "e": "[]", "c": now},
            )
        session = conn.execute(text("SELECT 1 FROM sessions WHERE session_id=:session_id"), {"session_id": session_id}).first()
        if not session:
            conn.execute(
                text("INSERT INTO sessions (session_id, user_id, started_at) VALUES (:s, :u, :c)"),
                {"s": session_id, "u": user_id, "c": now},
            )
