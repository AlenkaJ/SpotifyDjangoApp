from django.contrib import admin

from .models import Album, Artist, Track


class ArtistAdmin(admin.ModelAdmin):
    """Admin representation for Artist model."""

    list_display = ("name", "spotify_id", "user_id")
    list_filter = ["genres"]
    search_fields = ["name"]


class AlbumAdmin(admin.ModelAdmin):
    """Admin representation for Album model."""

    list_display = ("title", "added_at", "release_date", "popularity", "user_id")
    list_filter = ["release_date"]
    search_fields = ["title"]


class TrackAdmin(admin.ModelAdmin):
    """Admin representation for Track model."""

    list_display = ("title", "spotify_id")
    search_fields = ["title"]


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Track, TrackAdmin)
