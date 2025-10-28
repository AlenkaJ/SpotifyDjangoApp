from django_filters import CharFilter, FilterSet

from .models import Album, Artist


class ArtistFilter(FilterSet):
    """FilterSet for Artist model."""

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
        """Meta class for ArtistFilter."""

        model = Artist
        fields = ["artist_name", "album_name", "genre_name"]

    def filter_by_genre(self, queryset, _name, value):
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


class AlbumFilter(FilterSet):
    """FilterSet for Album model."""

    album_name = CharFilter(
        field_name="title", lookup_expr="icontains", label="Album", distinct=True
    )
    artist_name = CharFilter(
        field_name="artists__name",
        lookup_expr="icontains",
        label="Artist",
        distinct=True,
    )

    class Meta:
        """Meta class for AlbumFilter."""

        model = Album
        fields = ["album_name", "artist_name"]
