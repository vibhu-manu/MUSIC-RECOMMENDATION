import csv
import random

languages = ["kannada", "english", "hindi", "telugu", "tamil"]

data_pool = {
    "kannada": {
        "titles": [
            "Anisuthide", "Bombe Helutaithe", "Belageddu", "Singara Siriye", "Tagaru Banthu", 
            "Ninnindale", "Ondu Malebillu", "Saluthillave", "Kavithe Kavithe", "Neene Bari Neene", 
            "Raajakumara Title Track", "Natasaarvabhouma", "Kush Kush", "Open the Bottle", "Chuttu Chuttu", 
            "Yenammi Yenammi", "Jeeva Veene", "Kanasugara", "Appu Baa", "Madhurame",
            "Tunturu", "Nooru Janmaku", "Usire Usire", "Onde Ondu Maathu", "Karunade",
            "Sambo Siva Sambo", "Paravashanadenu", "Khaali Peeli", "Matte Matte", "Preethse"
        ],
        "artists": ["Sonu Nigam", "Vijay Prakash", "Shreya Ghoshal", "Sanjith Hegde", "Raghu Dixit", "Chandan Shetty", "Rajesh Krishnan", "Anuradha Bhat", "S. P. B.", "K. S. Chithra"],
        "genres": ["pop", "acoustic", "folk", "classical", "rock"]
    },
    "english": {
        "titles": [
            "Shape of You", "Blinding Lights", "Someone Like You", "Bad Guy", "Stay", 
            "As It Was", "Cruel Summer", "Flowers", "Believer", "Hotel California", 
            "Imagine", "Bohemian Rhapsody", "Hey Jude", "Rolling in the Deep", "Uptown Funk", 
            "Counting Stars", "Don't Start Now", "Levitating", "Thinking Out Loud", "Perfect",
            "All of Me", "Shallow", "Love Story", "Radioactive", "Wake Me Up",
            "Smells Like Teen Spirit", "Closer", "Senorita", "Stressed Out", "Bad Habits"
        ],
        "artists": ["Ed Sheeran", "The Weeknd", "Adele", "Billie Eilish", "Taylor Swift", "Harry Styles", "Dua Lipa", "Imagine Dragons", "Coldplay", "Bruno Mars"],
        "genres": ["pop", "rock", "electronic", "acoustic", "funk"]
    },
    "hindi": {
        "titles": [
            "Tum Hi Ho", "Kesariya", "Chaiyya Chaiyya", "Apna Bana Le", "Channa Mereya", 
            "Kal Ho Naa Ho", "Kabira", "Zaalima", "Dil Diyan Gallan", "Ghar More Pardesiya", 
            "Ae Dil Hai Mushkil", "Raataan Lambiyan", "Bekhayali", "Pasoori", "Tera Yaar Hoon Main", 
            "Jhumme Ki Raat", "Lungi Dance", "Kar Gayi Chull", "Balam Pichkari", "Senorita",
            "Agar Tum Saath Ho", "Pee Loon", "Kun Faya Kun", "Zindagi Do Pal Ki", "Tum Se Hi",
            "Hawayein", "Chura Ke Dil Mera", "Dil To Pagal Hai", "Ghungroo", "Nashe Si Chadh Gayi"
        ],
        "artists": ["Arijit Singh", "Sonu Nigam", "Shreya Ghoshal", "Atif Aslam", "Sukhwinder Singh", "Jubin Nautiyal", "Neha Kakkar", "Badshah", "Kailash Kher", "Lata Mangeshkar"],
        "genres": ["pop", "acoustic", "folk", "classical", "rock"]
    },
    "telugu": {
        "titles": [
            "Butta Bomma", "Naatu Naatu", "Samajavaragamana", "Kalaavathi", "Ramuloo Ramulaa", 
            "Oo Antava Oo Oo Antava", "Srivalli", "Inkem Inkem Inkem Kaavaale", "Adiga Adiga", "Nee Kannu Neeli Samudram", 
            "Telusa Telusa", "Undiporaadhey", "Chitti", "Saranga Dariya", "Oye Oye", 
            "Priya Mithunam", "Evare", "Nuvvostanante Neddontana", "Mellaga Karagani", "Oosupodu",
            "Dheevara", "Saahore Baahubali", "Pucho Prema Hele", "My Love", "Seethamma Vakitlo",
            "Ciciliya Ciciliya", "Apple Beauty", "Laalijo", "Arere Yemaindi", "Vintunnavaa"
        ],
        "artists": ["Sid Sriram", "Armaan Malik", "Rahul Sipligunj", "Anurag Kulkarni", "Mangli", "Karthik", "S. P. B.", "Chithra", "Shreya Ghoshal", "Sunitha"],
        "genres": ["pop", "acoustic", "folk", "classical", "rock"]
    },
    "tamil": {
        "titles": [
            "Why This Kolaveri Di", "Arabic Kuthu", "Rowdy Baby", "Tum Tum", "Kabavali", 
            "Marakkuma Nenjam", "Ranjithame", "Kaavaala", "Enjoy Enjaami", "Singappenney", 
            "Verithanam", "Chilla Chilla", "Hukum", "Kanja Poovu Kannala", "Kadhaippoma", 
            "Naan Pizhai", "Bodhai Kaname", "Vaseegara", "Munbe Vaa", "Nenjukkul Peidhidum",
            "Kannazhaga", "Unakku Thaan", "Ennodu Nee Irundhal", "Aalaporaan Thamizhan", "High on Love",
            "New York Nagaram", "Adiye", "Karka Karka", "Oru Maalai", "Pookkalae Sattru Oyivedungal"
        ],
        "artists": ["Anirudh Ravichander", "A. R. Rahman", "Sid Sriram", "Dhanush", "Dhee", "Vijay", "Harris Jayaraj", "Yuvan Shankar Raja", "Shreya Ghoshal", "S. P. B."],
        "genres": ["pop", "acoustic", "folk", "classical", "rock"]
    }
}

with open("backend/data/sample_spotify_tracks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "song_id", "track_name", "artist_name", "genre", "language",
        "valence", "energy", "tempo", "danceability", "acousticness",
        "speechiness", "instrumentalness", "liveness", "loudness", "popularity"
    ])
    
    song_counter = 1
    suffixes = [" (Acoustic)", " (Reprise)", " (Lofi Mix)", " (Live)", " (Club Remix)", " (Chill Out Mix)"]
    
    for lang, details in data_pool.items():
        titles = details["titles"]
        artists = details["artists"]
        genres = details["genres"]
        
        # We generate exactly 50 songs for each language
        for idx in range(50):
            if idx < len(titles):
                track_name = titles[idx]
            else:
                base_title = titles[idx % len(titles)]
                suffix = suffixes[(idx - len(titles)) % len(suffixes)]
                track_name = base_title + suffix
                
            artist_name = random.choice(artists)
            genre = random.choice(genres)
            
            # Setup realistic features based on genre
            if genre == "acoustic":
                valence = round(random.uniform(0.15, 0.55), 2)
                energy = round(random.uniform(0.1, 0.45), 2)
                tempo = random.randint(65, 95)
                danceability = round(random.uniform(0.3, 0.6), 2)
                acousticness = round(random.uniform(0.7, 0.95), 2)
                instrumentalness = round(random.uniform(0.0, 0.2), 2)
                loudness = round(random.uniform(-14.0, -8.0), 1)
            elif genre == "classical":
                valence = round(random.uniform(0.15, 0.65), 2)
                energy = round(random.uniform(0.05, 0.35), 2)
                tempo = random.randint(50, 85)
                danceability = round(random.uniform(0.15, 0.45), 2)
                acousticness = round(random.uniform(0.8, 0.98), 2)
                instrumentalness = round(random.uniform(0.3, 0.9), 2)
                loudness = round(random.uniform(-18.0, -11.0), 1)
            elif genre == "rock":
                valence = round(random.uniform(0.3, 0.75), 2)
                energy = round(random.uniform(0.7, 0.95), 2)
                tempo = random.randint(110, 160)
                danceability = round(random.uniform(0.4, 0.68), 2)
                acousticness = round(random.uniform(0.01, 0.15), 2)
                instrumentalness = round(random.uniform(0.0, 0.4), 2)
                loudness = round(random.uniform(-6.5, -3.5), 1)
            elif genre == "folk":
                valence = round(random.uniform(0.4, 0.85), 2)
                energy = round(random.uniform(0.45, 0.75), 2)
                tempo = random.randint(85, 125)
                danceability = round(random.uniform(0.55, 0.78), 2)
                acousticness = round(random.uniform(0.4, 0.7), 2)
                instrumentalness = round(random.uniform(0.0, 0.1), 2)
                loudness = round(random.uniform(-9.0, -5.5), 1)
            else: # pop, electronic, funk
                valence = round(random.uniform(0.5, 0.95), 2)
                energy = round(random.uniform(0.6, 0.9), 2)
                tempo = random.randint(95, 140)
                danceability = round(random.uniform(0.65, 0.88), 2)
                acousticness = round(random.uniform(0.05, 0.45), 2)
                instrumentalness = round(random.uniform(0.0, 0.15), 2)
                loudness = round(random.uniform(-8.0, -4.0), 1)
                
            speechiness = round(random.uniform(0.03, 0.15), 2)
            liveness = round(random.uniform(0.08, 0.3), 2)
            popularity = random.randint(50, 95)
            
            writer.writerow([
                f"s{song_counter:03d}",
                track_name,
                artist_name,
                genre,
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

print(f"Generated {song_counter - 1} tracks (50 songs per language).")
