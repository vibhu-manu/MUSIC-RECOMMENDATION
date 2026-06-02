from backend.app.config import get_settings
from backend.app.database import init_database
from backend.app.recommender.catalog import load_catalog, upsert_catalog


def main() -> None:
    settings = get_settings()
    init_database()
    songs = load_catalog(settings.catalog_path)
    upsert_catalog(songs)
    print(f"Loaded {len(songs)} songs from {settings.catalog_path}")


if __name__ == "__main__":
    main()
