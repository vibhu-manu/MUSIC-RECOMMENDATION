from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from sqlalchemy import text
from backend.app.database import db_session
from backend.app.recommender.embeddings import FEATURES, song_embedding


@dataclass
class Song:
    song_id: str
    track_name: str
    artist_name: str
    genre: str
    language: str
    popularity: float
    features: Dict[str, float]
    embedding: List[float]


def load_catalog(path: str) -> List[Song]:
    songs: List[Song] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            normalized = {
                "song_id": row.get("song_id") or row.get("id") or f"song-{index + 1}",
                "track_name": row.get("track_name") or row.get("name") or "Unknown Track",
                "artist_name": row.get("artist_name") or row.get("artists") or "Unknown Artist",
                "genre": row.get("genre") or row.get("track_genre") or "unknown",
                "language": row.get("language") or "english",
            }
            features = {feature: float(row.get(feature, 0) or 0) for feature in FEATURES}
            if features["popularity"] == 0 and row.get("popularity"):
                features["popularity"] = float(row["popularity"])
            songs.append(
                Song(
                    song_id=normalized["song_id"],
                    track_name=normalized["track_name"],
                    artist_name=normalized["artist_name"],
                    genre=normalized["genre"],
                    language=normalized["language"],
                    popularity=features["popularity"],
                    features=features,
                    embedding=song_embedding(features),
                )
            )
    return songs


def upsert_catalog(songs: List[Song]) -> None:
    with db_session() as conn:
        conn.execute(text("DELETE FROM song_features"))
        conn.execute(text("DELETE FROM songs"))
        for song in songs:
            conn.execute(
                text(
                    """
                    INSERT INTO songs (song_id, track_name, artist_name, genre, language, popularity)
                    VALUES (:song_id, :track_name, :artist_name, :genre, :language, :popularity)
                    ON CONFLICT(song_id) DO UPDATE SET
                        track_name=excluded.track_name,
                        artist_name=excluded.artist_name,
                        genre=excluded.genre,
                        language=excluded.language,
                        popularity=excluded.popularity
                    """
                ),
                {
                    "song_id": song.song_id,
                    "track_name": song.track_name,
                    "artist_name": song.artist_name,
                    "genre": song.genre,
                    "language": song.language,
                    "popularity": song.popularity,
                },
            )
            params = {"song_id": song.song_id, "embedding": json.dumps(song.embedding)}
            params.update(song.features)
            conn.execute(
                text(
                    """
                    INSERT INTO song_features (
                        song_id, valence, energy, tempo, danceability, acousticness, speechiness,
                        instrumentalness, liveness, loudness, embedding
                    )
                    VALUES (
                        :song_id, :valence, :energy, :tempo, :danceability, :acousticness, :speechiness,
                        :instrumentalness, :liveness, :loudness, :embedding
                    )
                    ON CONFLICT(song_id) DO UPDATE SET
                        valence=excluded.valence,
                        energy=excluded.energy,
                        tempo=excluded.tempo,
                        danceability=excluded.danceability,
                        acousticness=excluded.acousticness,
                        speechiness=excluded.speechiness,
                        instrumentalness=excluded.instrumentalness,
                        liveness=excluded.liveness,
                        loudness=excluded.loudness,
                        embedding=excluded.embedding
                    """
                ),
                params,
            )
