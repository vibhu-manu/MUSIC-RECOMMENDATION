import csv
import random

# Curated list of actual popular songs per language with appropriate genres and mood defaults
songs_pool = {
    "kannada": [
        {"name": "Anisuthide", "artist": "Sonu Nigam", "genre": "acoustic", "valence": 0.6, "energy": 0.4, "tempo": 85},
        {"name": "Bombe Helutaithe", "artist": "Vijay Prakash", "genre": "folk", "valence": 0.5, "energy": 0.5, "tempo": 90},
        {"name": "Belageddu", "artist": "Vijay Prakash", "genre": "pop", "valence": 0.8, "energy": 0.7, "tempo": 115},
        {"name": "Singara Siriye", "artist": "Vijay Prakash", "genre": "folk", "valence": 0.85, "energy": 0.8, "tempo": 125},
        {"name": "Tagaru Banthu Tagaru", "artist": "Anthony Daasan", "genre": "rock", "valence": 0.7, "energy": 0.9, "tempo": 140},
        {"name": "Ninnindale", "artist": "Sonu Nigam", "genre": "pop", "valence": 0.75, "energy": 0.6, "tempo": 105},
        {"name": "Ondu Malebillu", "artist": "Armaan Malik", "genre": "acoustic", "valence": 0.65, "energy": 0.45, "tempo": 95},
        {"name": "Saluthillave", "artist": "Vijay Prakash", "genre": "pop", "valence": 0.55, "energy": 0.5, "tempo": 100},
        {"name": "Kavithe Kavithe", "artist": "Vijay Prakash", "genre": "pop", "valence": 0.6, "energy": 0.55, "tempo": 92},
        {"name": "Neene Bari Neene", "artist": "Sonu Nigam", "genre": "acoustic", "valence": 0.4, "energy": 0.35, "tempo": 80},
        {"name": "Raajakumara Title Track", "artist": "Vijay Prakash", "genre": "pop", "valence": 0.7, "energy": 0.75, "tempo": 120},
        {"name": "Natasaarvabhouma Title", "artist": "Puneeth Rajkumar", "genre": "rock", "valence": 0.8, "energy": 0.85, "tempo": 130},
        {"name": "Kush Kush", "artist": "Shreya Ghoshal", "genre": "pop", "valence": 0.82, "energy": 0.68, "tempo": 112},
        {"name": "Open the Bottle", "artist": "Vijay Prakash", "genre": "pop", "valence": 0.88, "energy": 0.82, "tempo": 128},
        {"name": "Chuttu Chuttu", "artist": "Ravindra Soragavi", "genre": "folk", "valence": 0.9, "energy": 0.88, "tempo": 135},
        {"name": "Yenammi Yenammi", "artist": "Vijay Prakash", "genre": "folk", "valence": 0.75, "energy": 0.7, "tempo": 110},
        {"name": "Jeeva Veene", "artist": "P. B. Sreenivas", "genre": "classical", "valence": 0.45, "energy": 0.25, "tempo": 75},
        {"name": "Kanasugara", "artist": "S. P. Balasubrahmanyam", "genre": "pop", "valence": 0.65, "energy": 0.6, "tempo": 102},
        {"name": "Appu Baa", "artist": "Kailash Kher", "genre": "rock", "valence": 0.75, "energy": 0.85, "tempo": 138},
        {"name": "Madhurame", "artist": "Rajesh Krishnan", "genre": "classical", "valence": 0.5, "energy": 0.3, "tempo": 82}
    ],
    "english": [
        {"name": "Shape of You", "artist": "Ed Sheeran", "genre": "pop", "valence": 0.91, "energy": 0.65, "tempo": 96},
        {"name": "Blinding Lights", "artist": "The Weeknd", "genre": "pop", "valence": 0.84, "energy": 0.80, "tempo": 171},
        {"name": "Someone Like You", "artist": "Adele", "genre": "acoustic", "valence": 0.28, "energy": 0.33, "tempo": 135},
        {"name": "Bad Guy", "artist": "Billie Eilish", "genre": "electronic", "valence": 0.56, "energy": 0.43, "tempo": 135},
        {"name": "Stay", "artist": "The Kid LAROI & Justin Bieber", "genre": "pop", "valence": 0.87, "energy": 0.76, "tempo": 170},
        {"name": "As It Was", "artist": "Harry Styles", "genre": "pop", "valence": 0.66, "energy": 0.73, "tempo": 174},
        {"name": "Cruel Summer", "artist": "Taylor Swift", "genre": "pop", "valence": 0.58, "energy": 0.70, "tempo": 170},
        {"name": "Flowers", "artist": "Miley Cyrus", "genre": "pop", "valence": 0.65, "energy": 0.68, "tempo": 118},
        {"name": "Believer", "artist": "Imagine Dragons", "genre": "rock", "valence": 0.66, "energy": 0.78, "tempo": 125},
        {"name": "Hotel California", "artist": "Eagles", "genre": "rock", "valence": 0.62, "energy": 0.65, "tempo": 147},
        {"name": "Imagine", "artist": "John Lennon", "genre": "acoustic", "valence": 0.40, "energy": 0.26, "tempo": 76},
        {"name": "Bohemian Rhapsody", "artist": "Queen", "genre": "rock", "valence": 0.55, "energy": 0.40, "tempo": 144},
        {"name": "Hey Jude", "artist": "The Beatles", "genre": "pop", "valence": 0.67, "energy": 0.53, "tempo": 143},
        {"name": "Rolling in the Deep", "artist": "Adele", "genre": "pop", "valence": 0.52, "energy": 0.76, "tempo": 105},
        {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "genre": "funk", "valence": 0.93, "energy": 0.61, "tempo": 115},
        {"name": "Counting Stars", "artist": "OneRepublic", "genre": "pop", "valence": 0.48, "energy": 0.71, "tempo": 122},
        {"name": "Don't Start Now", "artist": "Dua Lipa", "genre": "pop", "valence": 0.68, "energy": 0.79, "tempo": 124},
        {"name": "Levitating", "artist": "Dua Lipa", "genre": "pop", "valence": 0.91, "energy": 0.83, "tempo": 103},
        {"name": "Thinking Out Loud", "artist": "Ed Sheeran", "genre": "pop", "valence": 0.59, "energy": 0.45, "tempo": 79},
        {"name": "Perfect", "artist": "Ed Sheeran", "genre": "pop", "valence": 0.59, "energy": 0.45, "tempo": 95}
    ],
    "hindi": [
        {"name": "Tum Hi Ho", "artist": "Arijit Singh", "genre": "acoustic", "valence": 0.35, "energy": 0.4, "tempo": 90},
        {"name": "Kesariya", "artist": "Arijit Singh", "genre": "pop", "valence": 0.7, "energy": 0.65, "tempo": 98},
        {"name": "Chaiyya Chaiyya", "artist": "Sukhwinder Singh", "genre": "folk", "valence": 0.85, "energy": 0.9, "tempo": 130},
        {"name": "Apna Bana Le", "artist": "Arijit Singh", "genre": "pop", "valence": 0.6, "energy": 0.5, "tempo": 92},
        {"name": "Channa Mereya", "artist": "Arijit Singh", "genre": "pop", "valence": 0.4, "energy": 0.45, "tempo": 95},
        {"name": "Kabira", "artist": "Tochi Raina", "genre": "acoustic", "valence": 0.65, "energy": 0.5, "tempo": 88},
        {"name": "Kal Ho Naa Ho", "artist": "Sonu Nigam", "genre": "pop", "valence": 0.5, "energy": 0.55, "tempo": 82},
        {"name": "Zaalima", "artist": "Arijit Singh", "genre": "pop", "valence": 0.75, "energy": 0.7, "tempo": 102},
        {"name": "Dil Diyan Gallan", "artist": "Atif Aslam", "genre": "acoustic", "valence": 0.6, "energy": 0.42, "tempo": 94},
        {"name": "Ghar More Pardesiya", "artist": "Shreya Ghoshal", "genre": "classical", "valence": 0.55, "energy": 0.6, "tempo": 110},
        {"name": "Ae Dil Hai Mushkil", "artist": "Arijit Singh", "genre": "pop", "valence": 0.3, "energy": 0.58, "tempo": 115},
        {"name": "Raataan Lambiyan", "artist": "Jubin Nautiyal", "genre": "pop", "valence": 0.72, "energy": 0.62, "tempo": 95},
        {"name": "Bekhayali", "artist": "Sachet Tandon", "genre": "rock", "valence": 0.28, "energy": 0.85, "tempo": 135},
        {"name": "Pasoori", "artist": "Ali Sethi", "genre": "pop", "valence": 0.82, "energy": 0.72, "tempo": 122},
        {"name": "Tera Yaar Hoon Main", "artist": "Arijit Singh", "genre": "acoustic", "valence": 0.5, "energy": 0.48, "tempo": 85},
        {"name": "Jhumme Ki Raat", "artist": "Mika Singh", "genre": "pop", "valence": 0.9, "energy": 0.88, "tempo": 128},
        {"name": "Lungi Dance", "artist": "Yo Yo Honey Singh", "genre": "pop", "valence": 0.92, "energy": 0.92, "tempo": 130},
        {"name": "Kar Gayi Chull", "artist": "Badshah", "genre": "pop", "valence": 0.88, "energy": 0.85, "tempo": 120},
        {"name": "Balam Pichkari", "artist": "Vishal Dadlani", "genre": "pop", "valence": 0.86, "energy": 0.89, "tempo": 125},
        {"name": "Senorita", "artist": "Farhan Akhtar", "genre": "pop", "valence": 0.8, "energy": 0.75, "tempo": 118}
    ],
    "telugu": [
        {"name": "Butta Bomma", "artist": "Armaan Malik", "genre": "pop", "valence": 0.88, "energy": 0.72, "tempo": 110},
        {"name": "Naatu Naatu", "artist": "Rahul Sipligunj", "genre": "pop", "valence": 0.9, "energy": 0.95, "tempo": 150},
        {"name": "Samajavaragamana", "artist": "Sid Sriram", "genre": "pop", "valence": 0.75, "energy": 0.55, "tempo": 95},
        {"name": "Kalaavathi", "artist": "Sid Sriram", "genre": "pop", "valence": 0.7, "energy": 0.6, "tempo": 92},
        {"name": "Ramuloo Ramulaa", "artist": "Anurag Kulkarni", "genre": "folk", "valence": 0.85, "energy": 0.82, "tempo": 125},
        {"name": "Oo Antava Oo Oo Antava", "artist": "Indravathi Chauhan", "genre": "pop", "valence": 0.8, "energy": 0.78, "tempo": 118},
        {"name": "Srivalli", "artist": "Sid Sriram", "genre": "pop", "valence": 0.65, "energy": 0.58, "tempo": 90},
        {"name": "Inkem Inkem", "artist": "Sid Sriram", "genre": "pop", "valence": 0.68, "energy": 0.5, "tempo": 88},
        {"name": "Adiga Adiga", "artist": "Sid Sriram", "genre": "acoustic", "valence": 0.5, "energy": 0.42, "tempo": 84},
        {"name": "Nee Kannu Neeli Samudram", "artist": "Javed Ali", "genre": "pop", "valence": 0.72, "energy": 0.64, "tempo": 102},
        {"name": "Telusa Telusa", "artist": "Jubin Nautiyal", "genre": "pop", "valence": 0.6, "energy": 0.52, "tempo": 96},
        {"name": "Undiporaadhey", "artist": "Sid Sriram", "genre": "acoustic", "valence": 0.55, "energy": 0.45, "tempo": 80},
        {"name": "Chitti", "artist": "Ram Miriyala", "genre": "folk", "valence": 0.86, "energy": 0.78, "tempo": 115},
        {"name": "Saranga Dariya", "artist": "Mangli", "genre": "folk", "valence": 0.89, "energy": 0.87, "tempo": 132},
        {"name": "Oye Oye", "artist": "Siddharth", "genre": "pop", "valence": 0.78, "energy": 0.7, "tempo": 105},
        {"name": "Priya Mithunam", "artist": "Vijay Yesudas", "genre": "classical", "valence": 0.4, "energy": 0.3, "tempo": 78}
    ],
    "tamil": [
        {"name": "Why This Kolaveri Di", "artist": "Dhanush", "genre": "pop", "valence": 0.75, "energy": 0.65, "tempo": 100},
        {"name": "Arabic Kuthu", "artist": "Anirudh Ravichander", "genre": "pop", "valence": 0.88, "energy": 0.9, "tempo": 128},
        {"name": "Rowdy Baby", "artist": "Dhanush", "genre": "pop", "valence": 0.92, "energy": 0.88, "tempo": 130},
        {"name": "Tum Tum", "artist": "Sri Vardhini", "genre": "pop", "valence": 0.82, "energy": 0.75, "tempo": 115},
        {"name": "Kabavali", "artist": "Arunraja Kamaraj", "genre": "rock", "valence": 0.78, "energy": 0.86, "tempo": 122},
        {"name": "Marakkuma Nenjam", "artist": "A. R. Rahman", "genre": "acoustic", "valence": 0.45, "energy": 0.4, "tempo": 80},
        {"name": "Ranjithame", "artist": "Vijay", "genre": "folk", "valence": 0.9, "energy": 0.85, "tempo": 135},
        {"name": "Kaavaala", "artist": "Anirudh Ravichander", "genre": "pop", "valence": 0.85, "energy": 0.82, "tempo": 125},
        {"name": "Enjoy Enjaami", "artist": "Dhee", "genre": "folk", "valence": 0.8, "energy": 0.78, "tempo": 120},
        {"name": "Singappenney", "artist": "A. R. Rahman", "genre": "rock", "valence": 0.65, "energy": 0.72, "tempo": 110},
        {"name": "Verithanam", "artist": "Vijay", "genre": "pop", "valence": 0.86, "energy": 0.84, "tempo": 132},
        {"name": "Chilla Chilla", "artist": "Anirudh Ravichander", "genre": "pop", "valence": 0.8, "energy": 0.88, "tempo": 126},
        {"name": "Hukum", "artist": "Anirudh Ravichander", "genre": "rock", "valence": 0.74, "energy": 0.92, "tempo": 142},
        {"name": "Kanja Poovu Kannala", "artist": "Sid Sriram", "genre": "acoustic", "valence": 0.5, "energy": 0.45, "tempo": 85},
        {"name": "Kadhaippoma", "artist": "Sid Sriram", "genre": "pop", "valence": 0.62, "energy": 0.5, "tempo": 92},
        {"name": "Naan Pizhai", "artist": "Anirudh Ravichander", "genre": "acoustic", "valence": 0.68, "energy": 0.52, "tempo": 95},
        {"name": "Bodhai Kaname", "artist": "Anirudh Ravichander", "genre": "pop", "valence": 0.7, "energy": 0.62, "tempo": 105}
    ]
}

with open("backend/data/sample_spotify_tracks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "song_id", "track_name", "artist_name", "genre", "language",
        "valence", "energy", "tempo", "danceability", "acousticness",
        "speechiness", "instrumentalness", "liveness", "loudness", "popularity"
    ])
    
    song_counter = 1
    for lang, list_of_songs in songs_pool.items():
        for song in list_of_songs:
            # Generate realistic features around the song's predefined baseline
            valence = min(1.0, max(0.05, round(song["valence"] + random.uniform(-0.1, 0.1), 2)))
            energy = min(1.0, max(0.05, round(song["energy"] + random.uniform(-0.1, 0.1), 2)))
            tempo = max(50, min(200, song["tempo"] + random.randint(-8, 8)))
            
            # Fill other features realistically based on genre
            if song["genre"] == "acoustic":
                danceability = round(random.uniform(0.3, 0.65), 2)
                acousticness = round(random.uniform(0.65, 0.95), 2)
                instrumentalness = round(random.uniform(0.0, 0.3), 2)
                loudness = round(random.uniform(-14.0, -8.0), 1)
            elif song["genre"] == "classical":
                danceability = round(random.uniform(0.2, 0.5), 2)
                acousticness = round(random.uniform(0.8, 0.98), 2)
                instrumentalness = round(random.uniform(0.3, 0.95), 2)
                loudness = round(random.uniform(-18.0, -12.0), 1)
            elif song["genre"] == "rock":
                danceability = round(random.uniform(0.4, 0.7), 2)
                acousticness = round(random.uniform(0.01, 0.2), 2)
                instrumentalness = round(random.uniform(0.0, 0.4), 2)
                loudness = round(random.uniform(-6.5, -3.5), 1)
            else: # pop, folk, electronic, funk
                danceability = round(random.uniform(0.6, 0.88), 2)
                acousticness = round(random.uniform(0.1, 0.5), 2)
                instrumentalness = round(random.uniform(0.0, 0.15), 2)
                loudness = round(random.uniform(-8.0, -4.0), 1)

            speechiness = round(random.uniform(0.03, 0.15), 2)
            liveness = round(random.uniform(0.08, 0.32), 2)
            popularity = random.randint(45, 95)
            
            writer.writerow([
                f"s{song_counter:03d}",
                song["name"],
                song["artist"],
                song["genre"],
                lang,
                valence,
                energy,
                tempo,
                danceability,
                acousticness,
                speechiness,
                instrumentalness,
                liveness,
                loudness,
                popularity
            ])
            song_counter += 1

print(f"Generated {song_counter - 1} realistic multilingual tracks.")
