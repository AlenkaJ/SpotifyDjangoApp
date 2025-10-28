from celery import shared_task

from .spotify_import.import_logic import import_from_spotify


@shared_task()
def import_spotify_data_task():
    """Celery task to import data from Spotify."""
    try:
        import_from_spotify()
        return {"status": "success"}
    except Exception as e:
        raise e
