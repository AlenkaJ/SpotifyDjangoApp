from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .filters import DashboardFilter
from .models import Album, Artist
from .tables import ArtistTable
from .tasks import import_spotify_data_task


def index(request):
    return render(request, "spotify_filter/index.html")


def importing(request):
    task = import_spotify_data_task.delay()
    return render(request, "spotify_filter/importing.html", {"task_id": task.id})


def task_status(request, task_id):
    result = AsyncResult(task_id)
    return JsonResponse(
        {
            "status": result.status,
            "result": result.result if result.status == "SUCCESS" else None,
        }
    )


class DashboardView(SingleTableMixin, FilterView):
    model = Artist
    table_class = ArtistTable
    template_name = "spotify_filter/dashboard.html"
    context_object_name = "artist_list"
    filterset_class = DashboardFilter

    def get_queryset(self):
        return Artist.objects.all()


class ArtistDetailView(generic.DetailView):
    model = Artist
    template_name = "spotify_filter/artist_detail.html"

    def get_queryset(self):
        return Artist.objects.all()


class AlbumDetailView(generic.DetailView):
    model = Album
    template_name = "spotify_filter/album_detail.html"

    def get_queryset(self):
        return Album.objects.all()
