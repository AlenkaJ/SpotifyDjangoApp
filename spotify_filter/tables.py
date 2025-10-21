from django.utils.html import format_html_join, format_html
from django.urls import reverse
import django_tables2 as tables
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, OrderingFilter
from django.db.models import Q

from .models import Artist, Album


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
        name = value
        return format_html(
            '<a href="{}">{}</a>',
            reverse("spotify_filter:artist_detail", args=[record.id]),
            name,
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


class DashboardFilter(FilterSet):
    artist_name = CharFilter(
        field_name="name", lookup_expr="icontains", label="Artist", distinct=True
    )
    album_name = CharFilter(
        field_name="albums__title",
        lookup_expr="icontains",
        label="Album",
        distinct=True,
    )
    genre_name = CharFilter(method="filter_by_genre", label="Genres", distinct=True)

    class Meta:
        model = Artist
        fields = ["artist_name", "album_name", "genre_name"]

    def filter_by_genre(self, queryset, name, value):
        """Allow filtering of multiple comma- or space-separated genre keywords"""
        # separate the keywords to a list
        keywords = [v.strip() for v in value.replace(",", " ").split() if v.strip()]
        # if no keywords, return whole queryset
        if not keywords:
            return queryset

        # go through the keywords and filter them out one by one
        for kw in keywords:
            queryset = queryset.filter(genres__name__icontains=kw)

        return queryset.distinct()
