from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .filters import AlbumFilter, ArtistFilter
from .models import Album, Artist
from .tables import AlbumTable, ArtistTable
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
    template_name = "spotify_filter/dashboard.html"

    def get_queryset(self):
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            Album.objects.all()
        return Artist.objects.all()

    def get_filterset_class(self):
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            return AlbumFilter
        return ArtistFilter

    def get_table_class(self):
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            return AlbumTable
        return ArtistTable

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            kwargs["queryset"] = Album.objects.all()
        else:
            kwargs["queryset"] = Artist.objects.all()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_view"] = self.request.GET.get("view", "artists")
        return context


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
