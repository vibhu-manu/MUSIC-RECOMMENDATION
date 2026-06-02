import csv
import random

languages = ["kannada", "english", "hindi", "telugu", "tamil"]
genres = ["pop", "rock", "classical", "hip hop", "acoustic", "electronic", "folk"]

with open("backend/data/sample_spotify_tracks.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "song_id", "track_name", "artist_name", "genre", "language",
        "valence", "energy", "tempo", "danceability", "acousticness",
        "speechiness", "instrumentalness", "liveness", "loudness", "popularity"
    ])
    
    for i in range(1, 151):
        lang = random.choice(languages)
        genre = random.choice(genres)
        
        # Add varied features
        valence = round(random.uniform(0.1, 0.9), 2)
        energy = round(random.uniform(0.1, 0.9), 2)
        tempo = random.randint(60, 180)
        danceability = round(random.uniform(0.2, 0.9), 2)
        acousticness = round(random.uniform(0.0, 0.9), 2)
        speechiness = round(random.uniform(0.0, 0.3), 2)
        instrumentalness = round(random.uniform(0.0, 0.8), 2)
        liveness = round(random.uniform(0.0, 0.4), 2)
        loudness = round(random.uniform(-15.0, -3.0), 1)
        popularity = random.randint(30, 95)
        
        track_name = f"Track {i} ({lang.capitalize()})"
        artist_name = f"Artist {i}"
        
        writer.writerow([
            f"s{i:03d}", track_name, artist_name, genre, lang,
            valence, energy, tempo, danceability, acousticness,
            speechiness, instrumentalness, liveness, loudness, popularity
        ])
