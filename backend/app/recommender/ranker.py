from __future__ import annotations
from typing import Dict, Iterable, List, Tuple
import random
from backend.app.recommender.catalog import Song
from backend.app.recommender.embeddings import cosine, dominant_emotion, emotion_song_rule_bonus, mood_affinity


def _diversity_penalty(song: Song, selected: Iterable[Song]) -> float:
    selected = list(selected)
    if not selected:
        return 0.0
    same_genre = sum(1 for item in selected if item.genre == song.genre)
    artist_repeat = sum(1 for item in selected if item.artist_name == song.artist_name)
    return min(0.35, same_genre * 0.08 + artist_repeat * 0.12)


def rank_candidates(
    candidates: List[Tuple[Song, float]],
    user_embedding: List[float],
    limit: int,
    feedback_counts: Dict[str, Dict[str, int]],
    probabilities: Dict[str, float],
    language: str = "english",
) -> List[Tuple[Song, float, List[str]]]:
    selected: List[Song] = []
    ranked: List[Tuple[Song, float, List[str]]] = []
    remaining = [c for c in candidates if c[0].language.lower() == language.lower()]
    mood = dominant_emotion(probabilities)

    while remaining and len(ranked) < limit:
        best = None
        best_score = -10.0
        best_reasons: List[str] = []
        for song, similarity in remaining:
            popularity = song.popularity / 100.0
            novelty = 1.0 - popularity
            personalization = cosine(user_embedding, song.embedding) if any(user_embedding) else 0.0
            feedback = feedback_counts.get(song.song_id, {})
            feedback_bonus = feedback.get("like", 0) * 0.03 - feedback.get("dislike", 0) * 0.06 - feedback.get("skip", 0) * 0.03
            diversity_penalty = _diversity_penalty(song, selected)
            affinity = mood_affinity(probabilities, song.features)
            rule_bonus = sum(prob * emotion_song_rule_bonus(emo, song.features) for emo, prob in probabilities.items())
            random_factor = random.uniform(-0.1, 0.1)
            score = (
                0.40 * affinity
                + 0.24 * rule_bonus
                + 0.14 * similarity
                + 0.08 * popularity
                + 0.06 * novelty
                + 0.08 * personalization
                + feedback_bonus
                - diversity_penalty
                + random_factor
            )
            reasons = [
                f"{mood} fit {affinity:.2f}",
                f"popularity {song.popularity:.0f}/100",
                "personalized" if personalization > 0.1 else "fresh pick",
            ]
            if score > best_score:
                best = (song, similarity)
                best_score = score
                best_reasons = reasons
        if best is None:
            break
        selected.append(best[0])
        ranked.append((best[0], round(best_score, 4), best_reasons))
        remaining = [candidate for candidate in remaining if candidate[0].song_id != best[0].song_id]
    return ranked
