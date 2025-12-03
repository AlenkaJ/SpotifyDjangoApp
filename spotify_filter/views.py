import os
from datetime import timedelta

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic.edit import CreateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .filters import AlbumFilter, ArtistFilter
from .forms import UserRegisterForm
from .models import Album, Artist, SpotifyToken
from .spotify_import.api import get_spotify_oauth
from .tables import AlbumTable, ArtistTable
from .tasks import import_spotify_data_task


def index(request):
    """View for the index page."""
    return render(request, "spotify_filter/index.html")


@login_required
def spotify_connect(request):
    """Redirect user to Spotify for authorization"""
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@login_required
def spotify_callback(request):
    """Handle Spotify OAuth callback"""
    code = request.GET.get("code")

    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code, check_cache=False)

    # Save tokens
    SpotifyToken.objects.update_or_create(
        user=request.user,
        defaults={
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "expires_at": timezone.now() + timedelta(seconds=token_info["expires_in"]),
        },
    )

    # Start import
    task = import_spotify_data_task.delay(request.user.id)
    return render(request, "spotify_filter/importing.html", {"task_id": task.id})


@login_required
def importing(request):
    """View to start the Spotify data import process."""
    task = import_spotify_data_task.delay(request.user.id)
    return render(request, "spotify_filter/importing.html", {"task_id": task.id})


def task_status(request, task_id):
    """View to check the status of a Celery task."""
    result = AsyncResult(task_id)
    return JsonResponse(
        {
            "status": result.status,
            "result": result.result if result.status == "SUCCESS" else None,
        }
    )


class SignupView(SuccessMessageMixin, CreateView):
    template_name = "spotify_filter/signup.html"
    success_url = reverse_lazy("spotify_filter:login")
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"


class DashboardView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """
    Dashboard view to display artists or albums with filtering and table representation.
    """

    template_name = "spotify_filter/dashboard.html"

    def get_queryset(self):
        """Provide the appropriate queryset based on the view mode."""
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            Album.objects.filter(user=self.request.user)
        return Artist.objects.filter(user=self.request.user)

    def get_filterset_class(self):
        """Provide the appropriate filterset class based on the view mode."""
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            return AlbumFilter
        return ArtistFilter

    def get_table_class(self):
        """Provide the appropriate table class based on the view mode."""
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            return AlbumTable
        return ArtistTable

    def get_filterset_kwargs(self, filterset_class):
        """Provide the appropriate queryset to the filterset based on the view mode."""
        kwargs = super().get_filterset_kwargs(filterset_class)
        view_mode = self.request.GET.get("view", "artists")
        if view_mode == "albums":
            kwargs["queryset"] = Album.objects.filter(user=self.request.user)
        else:
            kwargs["queryset"] = Artist.objects.filter(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        """Add the active view to the context data."""
        context = super().get_context_data(**kwargs)
        context["active_view"] = self.request.GET.get("view", "artists")
        return context


class ArtistDetailView(LoginRequiredMixin, generic.DetailView):
    """View to display detailed information about a specific artist."""

    model = Artist
    template_name = "spotify_filter/artist_detail.html"

    def get_queryset(self):
        """Return the queryset for artists."""
        return Artist.objects.filter(user=self.request.user)


class AlbumDetailView(LoginRequiredMixin, generic.DetailView):
    """View to display detailed information about a specific album."""

    model = Album
    template_name = "spotify_filter/album_detail.html"

    def get_queryset(self):
        """Return the queryset for albums."""
        return Album.objects.filter(user=self.request.user)
