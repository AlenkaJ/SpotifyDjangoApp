import logging
import time
from itertools import count
from math import ceil, inf

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger(__name__)


class SpotifyImporter:
    """Class to import data from Spotify API."""

    def __init__(self, sp=None, scopes=None, max_retries=3, retry_delay=2):
        load_dotenv()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        if sp is not None:
            self.sp = sp
        else:
            if scopes is None:
                scopes = ["user-library-read", "playlist-modify-private"]
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))
            except spotipy.exceptions.SpotifyException as e:
                logger.error("Authentication failed: %s", e)
                raise

    def retrieve_albums(self, max_len=inf, offset=0, limit=50):
        """
        Retrieve saved albums from the user's Spotify library.

        Args:
            max_len (int): Maximum number of albums to retrieve.
            offset (int): The index of the first album to retrieve.
            limit (int): Number of albums to retrieve per API call.
        Returns:
            list: A list of album objects.
        """
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
            try:
                queue_response = self._fetch_batch_with_retries(
                    self.sp.current_user_saved_albums,
                    limit=batch_limit,
                    offset=batch_offset,
                )
                albums += queue_response["items"]
            except (
                spotipy.exceptions.SpotifyException,
                requests.exceptions.Timeout,
            ) as e:
                logger.error("Failed to fetch albums in batch %s: %s", batch_num, e)
            if queue_response["next"] is None or len(albums) >= max_len:
                reading = False
        return albums

    def retrieve_artists_by_id(self, ids, limit=50):
        """
        Retrieve artist information by their Spotify IDs.

        Args:
            ids (list): List of Spotify artist IDs.
            limit (int): Number of artists to retrieve per API call.
        Returns:
            list: A list of artist objects.
        """
        artists = []
        nbatches = ceil(len(ids) / limit)
        logger.info("Reading artists ... ")
        for i in range(nbatches):
            logger.info(i)
            try:
                queue_response = self._fetch_batch_with_retries(
                    self.sp.artists, ids[i * limit : (i + 1) * limit]
                )
                artists += queue_response["artists"]
            except (
                spotipy.exceptions.SpotifyException,
                requests.exceptions.Timeout,
            ) as e:
                logger.error("Failed to fetch artists in batch %s: %s", i, e)
        return artists

    def _fetch_batch_with_retries(self, func, *args, **kwargs):
        """Fetch a batch of data with retries on failure."""
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except spotipy.exceptions.SpotifyException as e:
                logger.error("Spotify API error: %s", e)
                raise
            except requests.exceptions.Timeout as e:
                logger.warning(
                    (
                        "Timeout on attempt %s/%s: %s. Retrying in %s ...",
                        attempt,
                        self.max_retries,
                        e,
                        self.retry_delay,
                    )
                )
                if attempt == self.max_retries:
                    logger.error("Max retries reached. Giving up.")
                    raise
                time.sleep(self.retry_delay)
        return None  # return to make pylint happy


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
