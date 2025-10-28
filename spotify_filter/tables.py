import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import Album, Artist


class ArtistTable(tables.Table):
    albums = tables.Column(verbose_name="Albums")

    class Meta:
        model = Artist
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "name",
            "albums",
            "genres",
        )

    def render_name(self, value, record):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("spotify_filter:artist_detail", args=[record.id]),
            value,
        )

    def render_albums(self, value):
        albums = value.all()
        return format_html_join(
            "",
            '<p><a href="{}">{}</a></p>',
            (
                (reverse("spotify_filter:album_detail", args=[album.id]), album.title)
                for album in albums
            ),
        )

    def render_genres(self, value):
        genres = value.all()
        return ", ".join([genre.name for genre in genres])


class AlbumTable(tables.Table):
    artists = tables.Column(verbose_name="Artists")

    class Meta:
        model = Album
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "title",
            "artists",
            "total_tracks",
            "release_date",
            "popularity",
            "added_at",
        )

    def render_title(self, value, record):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("spotify_filter:album_detail", args=[record.id]),
            value,
        )

    def render_artists(self, value):
        artists = value.all()
        return format_html_join(
            ", ",
            '<a href="{}">{}</a>',
            (
                (reverse("spotify_filter:artist_detail", args=[artist.id]), artist.name)
                for artist in artists
            ),
        )
