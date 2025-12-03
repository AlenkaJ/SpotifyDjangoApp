from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "spotify_filter"
urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name=f"{app_name}/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name=f"{app_name}/logout.html"),
        name="logout",
    ),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path("spotify/connect/", views.spotify_connect, name="spotify_connect"),
    path("spotify/callback/", views.spotify_callback, name="spotify_callback"),
    path("importing/", views.importing, name="importing"),
    path("tasks/status/<str:task_id>/", views.task_status, name="task_status"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("artist/<str:pk>/", views.ArtistDetailView.as_view(), name="artist_detail"),
    path("album/<str:pk>/", views.AlbumDetailView.as_view(), name="album_detail"),
]
