import logging
import os
import time
from itertools import count
from math import ceil, inf

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from ..models import SpotifyToken

logger = logging.getLogger(__name__)


def get_spotify_oauth():
    """Create and return a SpotifyOAuth instance with app credentials"""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read",
        cache_path=None,  # Don't cache locally
    )


class SpotifyImporter:
    """Class to import data from Spotify API."""

    def __init__(self, user, sp=None, scopes=None, max_retries=3, retry_delay=2):
        """Initialize the SpotifyImporter.
        Args:
            user (User): The user for whom to import data.
            sp (spotipy.Spotify, optional): An authenticated Spotipy client.
                If None, a new client will be created using the user's token.
            scopes (list, optional): List of scopes for Spotify OAuth.
                Used only if sp is None and user is None.
            max_retries (int): Maximum number of retries for API calls.
            retry_delay (int): Delay between retries in seconds.
        """
        load_dotenv()
        self.user = user
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        if sp is not None:
            self.sp = sp
        elif user is not None:
            try:
                spotify_token = SpotifyToken.objects.get(user=user)

                # Refresh token if expired
                if spotify_token.is_expired():
                    sp_oauth = get_spotify_oauth()
                    token_info = sp_oauth.refresh_access_token(
                        spotify_token.refresh_token
                    )
                    spotify_token.access_token = token_info["access_token"]
                    spotify_token.set_expiration(token_info["expires_in"])
                    spotify_token.save()

                # Create Spotify client with user's token
                self.sp = spotipy.Spotify(auth=spotify_token.access_token)

            except SpotifyToken.DoesNotExist as exc:
                raise Exception("User hasn't connected their Spotify account") from exc
        else:
            # Fallback on legacy single-user mode in case no spotipy or user are passed
            if scopes is None:
                scopes = ["user-library-read"]
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

    importer = SpotifyImporter(user=None)
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
