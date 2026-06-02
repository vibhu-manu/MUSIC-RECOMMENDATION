# Architecture Notes

## Stages

1. Webcam input captures a frame in the browser.
2. Facial emotion recognition predicts seven-class emotion probabilities.
3. Rolling smoothing averages probabilities across recent frames.
4. Emotion embedding maps probabilities to an audio-feature target vector.
5. Retrieval finds nearest songs by cosine similarity.
6. Ranking combines similarity, popularity, novelty, diversity, and personalization.
7. Output returns top 10 songs.
8. Feedback stores like/dislike/skip.
9. Personalization updates the user embedding and affects future ranking.

## Production Extensions

- Replace mock emotion provider with DeepFace, FER, or HuggingFace ViT.
- Train LightGBM LambdaRank on logged feedback.
- Batch-build a FAISS index whenever the song catalog changes.
- Add Redis for session smoothing state.
- Add object storage for optional captured-frame audit samples.
- Add Kafka or Pub/Sub for feedback events.
- Move from SQLite to PostgreSQL in production.
- Add auth and rate limiting before public deployment.

