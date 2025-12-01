import logging

from dateutil import parser

from spotify_filter.models import Album, AlbumTrack, Artist, Genre, Track

from .api import SpotifyImporter

logger = logging.getLogger(__name__)


def import_from_spotify(user, importer=None):
    """Import data from Spotify into the local database.
    Args:
        importer (SpotifyImporter, optional): An instance of SpotifyImporter.
            If None, a new instance will be created.
    Returns:
        dict: A dictionary containing statistics about the import process.
    """

    if importer is None:
        importer = SpotifyImporter(user)

    stats = {
        "albums_processed": 0,
        "albums_failed": 0,
        "artists_processed": 0,
        "artists_updated": 0,
        "artists_failed": 0,
        "tracks_processed": 0,
        "tracks_failed": 0,
    }
    import_albums(importer, stats)
    update_artists(importer, stats)
    logger.info(str(stats))
    return stats


def import_albums(importer, stats):
    """Import albums from Spotify into the local database."""
    albums = importer.retrieve_albums()
    for album_entry in albums:
        album_data = album_entry["album"]
        try:
            album_obj, album_created = Album.objects.get_or_create(
                user=importer.user,
                spotify_id=album_data["id"],
                defaults={
                    "title": album_data["name"],
                    "total_tracks": int(album_data["total_tracks"]),
                    "release_date": parser.parse(album_data["release_date"]),
                    "added_at": parser.parse(album_entry["added_at"]),
                    "popularity": int(album_data["popularity"]),
                    # takes the first image url,
                    # seems to be the one with the highest resolution
                    "album_cover": (
                        album_data["images"][0]["url"] if album_data["images"] else None
                    ),
                },
            )
            if not album_created:
                album_obj.added_at = parser.parse(album_entry["added_at"])
                album_obj.popularity = int(album_data["popularity"])
                album_obj.save()

            # create each artist if they don't exist and link to album
            for artist_data in album_data["artists"]:
                try:
                    artist_obj, _ = Artist.objects.get_or_create(
                        user=importer.user,
                        spotify_id=artist_data["id"],
                        defaults={
                            "name": artist_data["name"],
                        },
                    )
                    album_obj.artists.add(artist_obj)
                    stats["artists_processed"] += 1
                except KeyError as e:
                    logger.error(
                        "Failed to process artist %s for album %s: %s",
                        artist_data["id"],
                        album_data["id"],
                        e,
                    )
                    stats["artists_failed"] += 1
                    continue

            album_obj.save()

            for track_data in album_data["tracks"]["items"]:
                try:
                    track_obj, _ = Track.objects.get_or_create(
                        spotify_id=track_data["id"],
                        defaults={
                            "title": track_data["name"],
                            "duration_ms": int(track_data["duration_ms"]),
                        },
                    )
                    # create link between album and track with track and disc number
                    AlbumTrack.objects.get_or_create(
                        album=album_obj,
                        track=track_obj,
                        defaults={
                            "track_number": int(track_data["track_number"]),
                            "disc_number": int(track_data["disc_number"]),
                        },
                    )
                    stats["tracks_processed"] += 1
                except KeyError as e:
                    logger.error("Failed to process track %s: %s", track_data["id"], e)
                    stats["tracks_failed"] += 1
                    continue
            stats["albums_processed"] += 1
        except KeyError as e:
            logger.error("Failed to process album %s: %s", album_data["id"], e)
            stats["albums_failed"] += 1
            continue


def update_artists(importer, stats):
    """Update artist information such as genres and images."""
    artist_ids = list(
        Artist.objects.values_list("spotify_id", flat=True)
    )  # filter only the user specific artists?
    for sp_id, artist_data in zip(
        artist_ids, importer.retrieve_artists_by_id(artist_ids)
    ):
        try:
            artist_obj = Artist.objects.get(spotify_id=sp_id, user=importer.user)
            artist_obj.image = (
                artist_data["images"][0]["url"] if artist_data["images"] else None
            )
            artist_obj.save()
            for genre_name in artist_data["genres"]:
                genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
                artist_obj.genres.add(genre_obj)
            stats["artists_updated"] += 1
        except KeyError as e:
            logger.error("Failed to update artist %s: %s", sp_id, e)
            stats["artists_failed"] += 1
            continue
