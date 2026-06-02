CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    user_embedding JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE songs (
    song_id TEXT PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_name TEXT NOT NULL,
    genre TEXT NOT NULL,
    popularity NUMERIC NOT NULL
);

CREATE TABLE song_features (
    song_id TEXT PRIMARY KEY REFERENCES songs(song_id),
    valence NUMERIC NOT NULL,
    energy NUMERIC NOT NULL,
    tempo NUMERIC NOT NULL,
    danceability NUMERIC NOT NULL,
    acousticness NUMERIC NOT NULL,
    speechiness NUMERIC NOT NULL,
    instrumentalness NUMERIC NOT NULL,
    liveness NUMERIC NOT NULL,
    loudness NUMERIC NOT NULL,
    embedding JSONB NOT NULL
);

CREATE TABLE emotion_history (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    user_id TEXT NOT NULL REFERENCES users(user_id),
    probabilities JSONB NOT NULL,
    smoothed_probabilities JSONB NOT NULL,
    top_emotion TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE listening_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    song_id TEXT NOT NULL REFERENCES songs(song_id),
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    event_type TEXT NOT NULL CHECK (event_type IN ('like', 'dislike', 'skip', 'play')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feedback (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    song_id TEXT NOT NULL REFERENCES songs(song_id),
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    recommendation_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('like', 'dislike', 'skip')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recommendations (
    recommendation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    emotion_embedding JSONB NOT NULL,
    song_ids JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_feedback_user_song ON feedback(user_id, song_id);
CREATE INDEX idx_emotion_history_session ON emotion_history(session_id, created_at DESC);
CREATE INDEX idx_listening_history_user ON listening_history(user_id, created_at DESC);
