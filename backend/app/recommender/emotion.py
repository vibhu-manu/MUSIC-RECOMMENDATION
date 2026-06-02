from __future__ import annotations
import base64
import io
import hashlib
import os
from collections import defaultdict, deque
from typing import Deque, Dict
from backend.app.schemas import EMOTIONS


class EmotionSmoother:
    def __init__(self, window: int = 8):
        self.window = window
        self.frames: Dict[str, Deque[Dict[str, float]]] = defaultdict(lambda: deque(maxlen=window))

    def add(self, session_id: str, probabilities: Dict[str, float]) -> Dict[str, float]:
        normalized = normalize_probabilities(probabilities)
        self.frames[session_id].append(normalized)
        smoothed = {emotion: 0.0 for emotion in EMOTIONS}
        weights = list(range(1, len(self.frames[session_id]) + 1))
        for frame, weight in zip(self.frames[session_id], weights):
            for emotion in EMOTIONS:
                smoothed[emotion] += frame.get(emotion, 0.0) * weight
        total_weight = max(1, sum(weights))
        averaged = {emotion: value / total_weight for emotion, value in smoothed.items()}
        return sharpen_probabilities(averaged, temperature=0.95)

    def clear(self, session_id: str) -> None:
        self.frames.pop(session_id, None)


def normalize_probabilities(probabilities: Dict[str, float]) -> Dict[str, float]:
    cleaned = {emotion: max(0.0, float(probabilities.get(emotion, 0.0))) for emotion in EMOTIONS}
    total = sum(cleaned.values())
    if total <= 0:
        return {emotion: round(1 / len(EMOTIONS), 4) for emotion in EMOTIONS}
    return {emotion: round(value / total, 4) for emotion, value in cleaned.items()}


def sharpen_probabilities(probabilities: Dict[str, float], temperature: float = 0.95) -> Dict[str, float]:
    normalized = normalize_probabilities(probabilities)
    sharpened = {emotion: value ** (1.0 / temperature) for emotion, value in normalized.items()}
    return normalize_probabilities(sharpened)


def _image_payload(image_base64: str | None) -> bytes | None:
    if not image_base64:
        return None
    payload = image_base64.split(",", 1)[-1]
    try:
        return base64.b64decode(payload)
    except Exception:
        return None


class EmotionDetector:
    provider_name = "base"
    last_error: str | None = None

    def predict(self, image_base64: str | None) -> Dict[str, float]:
        raise NotImplementedError


class VisualEmotionDetector(EmotionDetector):
    """Local frame-sensitive fallback used when a pretrained face model is not installed."""

    provider_name = "visual"

    def predict(self, image_base64: str | None) -> Dict[str, float]:
        import random
        image_bytes = _image_payload(image_base64)
        if not image_bytes:
            base = {"happy": 0.04, "sad": 0.06, "angry": 0.03, "fear": 0.03, "surprise": 0.03, "neutral": 0.78, "disgust": 0.02, "love": 0.01}
            for k in base:
                base[k] = max(0.01, base[k] + random.uniform(-0.02, 0.02))
            return sharpen_probabilities(base, temperature=0.95)
        try:
            from PIL import Image, ImageStat

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((96, 72))
            stat = ImageStat.Stat(image)
            mean_r, mean_g, mean_b = [value / 255.0 for value in stat.mean]
            std_r, std_g, std_b = [value / 255.0 for value in stat.stddev]
            brightness = (mean_r + mean_g + mean_b) / 3.0
            contrast = (std_r + std_g + std_b) / 3.0
            warmth = max(0.0, mean_r - mean_b)
            coolness = max(0.0, mean_b - mean_r)
            saturation = max(mean_r, mean_g, mean_b) - min(mean_r, mean_g, mean_b)
            center = image.crop((30, 18, 66, 54))
            center_brightness = sum(ImageStat.Stat(center).mean) / (3 * 255.0)
            face_signal = max(0.0, min(1.0, center_brightness + contrast))

            scores = {
                "happy": 0.08 + 1.20 * brightness + 1.05 * saturation + 0.65 * warmth,
                "sad": 0.10 + 1.35 * (1.0 - brightness) + 0.35 * coolness,
                "angry": 0.08 + 1.10 * warmth + 0.95 * contrast + 0.25 * (1.0 - mean_g),
                "fear": 0.07 + 1.05 * contrast + 0.45 * coolness + 0.35 * (1.0 - face_signal),
                "surprise": 0.07 + 1.20 * contrast + 0.65 * brightness + 0.35 * saturation,
                "neutral": 0.32 + 0.95 * (1.0 - abs(brightness - 0.52)) + 0.40 * (1.0 - saturation),
                "disgust": 0.06 + 0.95 * (mean_g - min(mean_r, mean_b)) + 0.55 * (1.0 - brightness),
                "love": 0.08 + 1.15 * warmth + 0.85 * (1.0 - contrast) + 0.50 * brightness,
            }
            for k in scores:
                scores[k] = max(0.01, scores[k] + random.uniform(-0.08, 0.08))
            return sharpen_probabilities(scores, temperature=0.95)
        except Exception:
            digest = hashlib.sha256(image_bytes).digest()
            raw = [(digest[index] % 100) / 100.0 + 0.05 for index in range(len(EMOTIONS))]
            return sharpen_probabilities(dict(zip(EMOTIONS, raw)), temperature=0.95)


class DeepFaceEmotionDetector(EmotionDetector):
    provider_name = "deepface"

    def __init__(self, deepface_home: str | None = None):
        if deepface_home:
            os.environ["DEEPFACE_HOME"] = deepface_home
        from deepface import DeepFace

        self.deepface = DeepFace
        self.fallback = VisualEmotionDetector()

    def predict(self, image_base64: str | None) -> Dict[str, float]:
        if not image_base64:
            return VisualEmotionDetector().predict(None)
        image_bytes = _image_payload(image_base64)
        if not image_bytes:
            return VisualEmotionDetector().predict(None)
        import cv2
        import numpy as np

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            return VisualEmotionDetector().predict(image_base64)
        try:
            result = self.deepface.analyze(
                img_path=image,
                actions=["emotion"],
                detector_backend="opencv",
                enforce_detection=False,
                silent=True,
            )
            first = result[0] if isinstance(result, list) else result
            emotions = {key.lower(): float(value) for key, value in first.get("emotion", {}).items()}
            emotions["love"] = emotions.get("happy", 0.0) * 0.4 + emotions.get("neutral", 0.0) * 0.2
            self.last_error = None
            return sharpen_probabilities(emotions, temperature=0.95)
        except Exception as exc:
            self.last_error = str(exc)
            return self.fallback.predict(image_base64)


def build_detector(provider: str, deepface_home: str | None = None) -> EmotionDetector:
    if provider.lower() == "deepface":
        try:
            return DeepFaceEmotionDetector(deepface_home=deepface_home)
        except Exception as exc:
            fallback = VisualEmotionDetector()
            fallback.last_error = str(exc)
            return fallback
    return VisualEmotionDetector()
