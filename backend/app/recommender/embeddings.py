from __future__ import annotations
import math
from typing import Dict, Iterable, List
import numpy as np
from backend.app.schemas import EMOTIONS


FEATURES = [
    "valence",
    "energy",
    "danceability",
    "acousticness",
    "speechiness",
    "instrumentalness",
    "liveness",
    "tempo",
    "loudness",
    "popularity",
]


EMOTION_CENTROIDS = {
    "happy": [0.90, 0.76, 0.82, 0.22, 0.10, 0.05, 0.22, 126, -6, 74],
    "sad": [0.18, 0.30, 0.34, 0.72, 0.08, 0.18, 0.16, 82, -14, 52],
    "angry": [0.24, 0.91, 0.56, 0.10, 0.14, 0.08, 0.34, 146, -5, 60],
    "fear": [0.20, 0.62, 0.38, 0.34, 0.10, 0.28, 0.30, 112, -10, 46],
    "surprise": [0.72, 0.82, 0.74, 0.18, 0.16, 0.10, 0.28, 132, -6, 66],
    "neutral": [0.52, 0.50, 0.54, 0.38, 0.08, 0.10, 0.18, 104, -9, 58],
    "disgust": [0.16, 0.70, 0.42, 0.20, 0.18, 0.16, 0.24, 118, -8, 42],
    "love": [0.85, 0.50, 0.55, 0.60, 0.05, 0.10, 0.15, 100, -8, 65],
}


def _scale_feature(name: str, value: float) -> float:
    if name == "tempo":
        return max(0.0, min(1.0, (value - 60.0) / 140.0))
    if name == "loudness":
        return max(0.0, min(1.0, (value + 60.0) / 60.0))
    if name == "popularity":
        return max(0.0, min(1.0, value / 100.0))
    return max(0.0, min(1.0, value))


def normalize(vector: Iterable[float]) -> List[float]:
    arr = np.array(list(vector), dtype=np.float32)
    norm = float(np.linalg.norm(arr))
    if norm == 0 or math.isnan(norm):
        return arr.tolist()
    return (arr / norm).tolist()


def song_embedding(row: Dict[str, float]) -> List[float]:
    return normalize(_scale_feature(feature, float(row[feature])) for feature in FEATURES)


def emotion_embedding(probabilities: Dict[str, float]) -> List[float]:
    weights = np.array([float(probabilities.get(emotion, 0.0)) for emotion in EMOTIONS], dtype=np.float32)
    if weights.sum() <= 0:
        weights = np.ones(len(EMOTIONS), dtype=np.float32) / len(EMOTIONS)
    else:
        weights = weights / weights.sum()

    centroids = []
    for emotion in EMOTIONS:
        scaled = [_scale_feature(feature, value) for feature, value in zip(FEATURES, EMOTION_CENTROIDS[emotion])]
        centroids.append(scaled)
    return normalize(np.matmul(weights, np.array(centroids, dtype=np.float32)))


def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    left = np.array(list(a), dtype=np.float32)
    right = np.array(list(b), dtype=np.float32)
    denom = float(np.linalg.norm(left) * np.linalg.norm(right))
    return 0.0 if denom == 0 else float(np.dot(left, right) / denom)


def dominant_emotion(probabilities: Dict[str, float]) -> str:
    normalized = {emotion: float(probabilities.get(emotion, 0.0)) for emotion in EMOTIONS}
    return max(normalized, key=normalized.get)


def target_features(probabilities: Dict[str, float]) -> Dict[str, float]:
    weights = np.array([float(probabilities.get(emotion, 0.0)) for emotion in EMOTIONS], dtype=np.float32)
    if weights.sum() <= 0:
        weights = np.ones(len(EMOTIONS), dtype=np.float32) / len(EMOTIONS)
    else:
        weights = weights / weights.sum()
    centroids = np.array(
        [[_scale_feature(feature, value) for feature, value in zip(FEATURES, EMOTION_CENTROIDS[emotion])] for emotion in EMOTIONS],
        dtype=np.float32,
    )
    values = np.matmul(weights, centroids)
    return {feature: float(value) for feature, value in zip(FEATURES, values)}


def mood_affinity(probabilities: Dict[str, float], song_features: Dict[str, float]) -> float:
    target = target_features(probabilities)
    weights = {
        "valence": 1.75,
        "energy": 1.45,
        "danceability": 1.10,
        "acousticness": 0.95,
        "tempo": 0.85,
        "loudness": 0.70,
        "popularity": 0.25,
        "speechiness": 0.30,
        "instrumentalness": 0.35,
        "liveness": 0.25,
    }
    distance = 0.0
    total = 0.0
    for feature, weight in weights.items():
        song_value = _scale_feature(feature, float(song_features.get(feature, 0.0)))
        distance += weight * abs(song_value - target[feature])
        total += weight
    raw_affinity = max(0.0, 1.0 - (distance / total))
    # Stretch raw affinity to show significant variation in the UI
    stretched = (raw_affinity - 0.58) / 0.30
    return max(0.12, min(0.98, stretched))


def emotion_song_rule_bonus(emotion: str, song_features: Dict[str, float]) -> float:
    valence = float(song_features["valence"])
    energy = float(song_features["energy"])
    danceability = float(song_features["danceability"])
    acousticness = float(song_features["acousticness"])
    tempo = _scale_feature("tempo", float(song_features["tempo"]))
    instrumentalness = float(song_features["instrumentalness"])
    loudness = _scale_feature("loudness", float(song_features["loudness"]))

    if emotion == "happy":
        return 0.40 * valence + 0.25 * danceability + 0.20 * energy
    if emotion == "sad":
        return 0.42 * (1.0 - valence) + 0.28 * acousticness + 0.16 * (1.0 - energy) + 0.10 * (1.0 - tempo)
    if emotion == "angry":
        return 0.42 * energy + 0.22 * loudness + 0.18 * (1.0 - acousticness) + 0.12 * tempo
    if emotion == "fear":
        return 0.28 * instrumentalness + 0.24 * (1.0 - valence) + 0.20 * (1.0 - danceability) + 0.16 * acousticness
    if emotion == "surprise":
        return 0.28 * energy + 0.24 * danceability + 0.18 * tempo + 0.16 * valence
    if emotion == "disgust":
        return 0.30 * (1.0 - valence) + 0.24 * energy + 0.16 * (1.0 - acousticness) + 0.12 * loudness
    if emotion == "love":
        return 0.35 * valence + 0.25 * acousticness + 0.20 * (1.0 - abs(energy - 0.5)) + 0.15 * danceability
    return 0.24 * (1.0 - abs(valence - 0.52)) + 0.22 * (1.0 - abs(energy - 0.50)) + 0.18 * danceability
