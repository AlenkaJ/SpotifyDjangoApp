import logging
from itertools import count
from math import ceil, inf

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger(__name__)


class SpotifyImporter:
    def __init__(self, sp=None, scopes=None):
        load_dotenv()
        if sp is not None:
            self.sp = sp
        else:
            if scopes is None:
                scopes = ["user-library-read", "playlist-modify-private"]
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))

    def retrieve_albums(self, max_len=inf, offset=0, limit=50):
        assert limit > 0
        assert max_len > 0
        assert offset >= 0
        albums = []
        counter = count(start=0, step=1)
        reading = True
        logger.info("Reading albums ... ")
        while reading:
            batch_num = next(counter)
            logger.info(batch_num)
            batch_offset = offset + limit * batch_num
            batch_limit = min(limit, max_len + offset - batch_offset)
            queue_response = self.sp.current_user_saved_albums(
                limit=batch_limit, offset=batch_offset
            )
            albums += queue_response["items"]
            if queue_response["next"] is None or len(albums) >= max_len:
                reading = False
        return albums

    def retrieve_artists_by_id(self, ids, limit=50):
        artists = []
        nbatches = ceil(len(ids) / limit)
        logger.info("Reading artists ... ")
        for i in range(nbatches):
            logger.info(i)
            queue_response = self.sp.artists(ids[i * limit : (i + 1) * limit])
            artists += queue_response["artists"]
        return artists


if __name__ == "__main__":
    import json

    importer = SpotifyImporter()
    retrieved_albums = importer.retrieve_albums(max_len=2)
    with open("albums2.json", "w", encoding="utf-8") as f:
        json.dump(retrieved_albums, f, indent=4)

    artist_ids = []
    for album_entry in retrieved_albums:
        album_data = album_entry["album"]
        for artist_data in album_data["artists"]:
            artist_ids.append(artist_data["id"])

    retrieved_artists = importer.retrieve_artists_by_id(artist_ids, limit=50)
    with open("artists2.json", "w", encoding="utf-8") as f:
        json.dump(retrieved_artists, f, indent=4)
