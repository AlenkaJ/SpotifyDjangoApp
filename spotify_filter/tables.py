import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import Album, Artist


class ArtistTable(tables.Table):
    """Table representation for Artist model."""

    albums = tables.Column(verbose_name="Albums")

    class Meta:
        """Meta class for ArtistTable."""

        model = Artist
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "name",
            "albums",
            "genres",
        )

    def render_name(self, value, record):
        """Render the artist name as a link to the artist detail page."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse("spotify_filter:artist_detail", args=[record.id]),
            value,
        )

    def render_albums(self, value):
        """Render the albums as links to their detail pages."""
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
        """Render the genres as a comma-separated list."""
        genres = value.all()
        return ", ".join([genre.name for genre in genres])


class AlbumTable(tables.Table):
    """Table representation for Album model."""

    artists = tables.Column(verbose_name="Artists")

    class Meta:
        """Meta class for AlbumTable."""

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
        """Render the album title as a link to the album detail page."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse("spotify_filter:album_detail", args=[record.id]),
            value,
        )

    def render_artists(self, value):
        """Render the artists as links to their detail pages."""
        artists = value.all()
        return format_html_join(
            ", ",
            '<a href="{}">{}</a>',
            (
                (reverse("spotify_filter:artist_detail", args=[artist.id]), artist.name)
                for artist in artists
            ),
        )
