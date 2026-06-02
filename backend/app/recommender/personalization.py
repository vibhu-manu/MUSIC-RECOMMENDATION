from __future__ import annotations
import json
from typing import List
from sqlalchemy import text
from backend.app.database import db_session
from backend.app.recommender.embeddings import normalize


ACTION_WEIGHTS = {"like": 0.30, "skip": -0.08, "dislike": -0.22}


def get_user_embedding(user_id: str, dimensions: int) -> List[float]:
    with db_session() as conn:
        row = conn.execute(text("SELECT user_embedding FROM users WHERE user_id=:u"), {"u": user_id}).first()
    if not row:
        return [0.0] * dimensions
    values = json.loads(row[0] or "[]")
    return values if len(values) == dimensions else [0.0] * dimensions


def update_user_embedding(user_id: str, song_embedding: List[float], action: str) -> List[float]:
    current = get_user_embedding(user_id, len(song_embedding))
    weight = ACTION_WEIGHTS[action]
    updated = [(0.92 * old) + (weight * new) for old, new in zip(current, song_embedding)]
    if action == "like":
        updated = normalize(updated)
    with db_session() as conn:
        conn.execute(
            text("UPDATE users SET user_embedding=:embedding WHERE user_id=:user_id"),
            {"embedding": json.dumps(updated), "user_id": user_id},
        )
    return updated
