from celery import shared_task
from django.contrib.auth import get_user_model

from .spotify_import.import_logic import import_from_spotify


@shared_task()
def import_spotify_data_task(user_id):
    """Celery task to import data from Spotify."""
    try:
        user = get_user_model().objects.get(id=user_id)
        import_from_spotify(user)
        return {"status": "success"}
    except Exception as e:
        raise e
