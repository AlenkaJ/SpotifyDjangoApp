import json
import logging
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from spotify_filter.filters import AlbumFilter, ArtistFilter
from spotify_filter.models import Album, AlbumTrack, Artist, Genre, Track
from spotify_filter.spotify_import.import_logic import import_from_spotify
from spotify_filter.tasks import import_spotify_data_task

logging.disable(logging.CRITICAL)

# pylint: disable=duplicate-code


class AlbumModelTests(TestCase):
    """Tests for the Album model."""

    def test_album_creation(self):
        """Test that an Album instance can be created successfully."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
            total_tracks=10,
            release_date="2023-01-01",
            popularity=50,
            album_cover="http://example.com/cover.jpg",
        )
        self.assertEqual(album.spotify_id, "12345")
        self.assertEqual(album.title, "Test Album")
        self.assertEqual(album.total_tracks, 10)
        self.assertEqual(album.release_date, "2023-01-01")
        self.assertEqual(album.popularity, 50)
        self.assertEqual(album.album_cover, "http://example.com/cover.jpg")

    def test_spotify_link_property(self):
        """Test the spotify_link property of the Album model."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
        )
        self.assertEqual(album.spotify_link, "https://open.spotify.com/album/12345")

    def test_album_str_method(self):
        """Test the __str__ method of the Album model."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
        )
        self.assertEqual(str(album), "Test Album")

    def test_artists_verbose_name(self):
        """Test the verbose_name of the artists field in Album model."""
        album = Album()
        self.assertEqual(album._meta.get_field("artists").verbose_name, "Album Artists")

    def test_album_with_artists(self):
        """Test that artists can be associated with an Album."""
        user = get_user_model().objects.create_user(username="testuser")
        album = Album.objects.create(
            user=user,
            spotify_id="12345",
            title="Test Album",
        )
        artist1 = Artist.objects.create(
            user=user,
            spotify_id="a1",
            name="Artist One",
        )
        artist2 = Artist.objects.create(
            user=user,
            spotify_id="a2",
            name="Artist Two",
        )
        album.artists.add(artist1, artist2)
        self.assertEqual(album.artists.count(), 2)
        self.assertIn(artist1, album.artists.all())
        self.assertIn(artist2, album.artists.all())


class ArtistModelTests(TestCase):
    """Tests for the Artist model."""

    def test_artist_creation(self):
        """Test that an Artist instance can be created successfully."""
        artist = Artist.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="a1",
            name="Artist One",
        )
        self.assertEqual(artist.spotify_id, "a1")
        self.assertEqual(artist.name, "Artist One")

    def test_spotify_link_property(self):
        """Test the spotify_link property of the Artist model."""
        artist = Artist.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="a1",
            name="Artist One",
        )
        self.assertEqual(artist.spotify_link, "https://open.spotify.com/artist/a1")

    def test_artist_str_method(self):
        """Test the __str__ method of the Artist model."""
        artist = Artist.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="a1",
            name="Artist One",
        )
        self.assertEqual(str(artist), "Artist One")

    def test_name_verbose_name(self):
        """Test the verbose_name of the name field in Artist model."""
        artist = Artist(
            user=get_user_model().objects.create_user(username="testuser"),
        )
        self.assertEqual(artist._meta.get_field("name").verbose_name, "Artist Name")

    def test_genres_verbose_name(self):
        """Test the verbose_name of the genres field in Artist model."""
        artist = Artist(
            user=get_user_model().objects.create_user(username="testuser"),
        )
        self.assertEqual(artist._meta.get_field("genres").verbose_name, "Genres")

    def test_artist_with_genres(self):
        """Test that genres can be associated with an Artist."""
        artist = Artist.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="a1",
            name="Artist One",
        )
        genre1 = Genre.objects.create(name="Rock")
        genre2 = Genre.objects.create(name="Pop")
        artist.genres.add(genre1, genre2)
        self.assertEqual(artist.genres.count(), 2)
        self.assertIn(genre1, artist.genres.all())
        self.assertIn(genre2, artist.genres.all())


class GenreModelTests(TestCase):
    """Tests for the Genre model."""

    def test_genre_creation(self):
        """Test that a Genre instance can be created successfully."""
        genre = Genre.objects.create(name="Rock")
        self.assertEqual(genre.name, "Rock")

    def test_genre_str_method(self):
        """Test the __str__ method of the Genre model."""
        genre = Genre.objects.create(name="Rock")
        self.assertEqual(str(genre), "Rock")


class TrackModelTests(TestCase):
    """Tests for the Track model."""

    def test_track_creation(self):
        """Test that a Track instance can be created successfully."""
        track = Track.objects.create(
            spotify_id="t1",
            title="Test Track",
            duration_ms=300000,
        )
        self.assertEqual(track.spotify_id, "t1")
        self.assertEqual(track.title, "Test Track")
        self.assertEqual(track.duration_ms, 300000)

    def test_spotify_link_property(self):
        """Test the spotify_link property of the Track model."""
        track = Track.objects.create(spotify_id="t1", title="Test Track")
        self.assertEqual(track.spotify_link, "https://open.spotify.com/track/t1")

    def test_track_str_method(self):
        """Test the __str__ method of the Track model."""
        track = Track.objects.create(spotify_id="t1", title="Test Track")
        self.assertEqual(str(track), "Test Track")

    def test_track_with_albums(self):
        """Test that albums can be associated with a Track."""
        user = get_user_model().objects.create_user(username="testuser")
        track = Track.objects.create(spotify_id="t1", title="Test Track")
        album1 = Album.objects.create(
            user=user,
            spotify_id="12345",
            title="Album One",
        )
        album2 = Album.objects.create(
            user=user,
            spotify_id="67890",
            title="Album Two",
        )
        AlbumTrack.objects.create(album=album1, track=track, track_number=1)
        AlbumTrack.objects.create(album=album2, track=track, track_number=2)
        self.assertEqual(track.albums.count(), 2)
        self.assertIn(album1, track.albums.all())
        self.assertIn(album2, track.albums.all())


class AlbumTrackModelTests(TestCase):
    """Tests for the AlbumTrack model."""

    def test_album_track_creation(self):
        """Test that an AlbumTrack instance can be created successfully."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
        )
        track = Track.objects.create(spotify_id="t1", title="Test Track")
        album_track = AlbumTrack.objects.create(
            album=album, track=track, track_number=1, disc_number=1
        )
        self.assertEqual(album_track.album, album)
        self.assertEqual(album_track.track, track)
        self.assertEqual(album_track.track_number, 1)
        self.assertEqual(album_track.disc_number, 1)

    def test_album_track_unique_together(self):
        """Test that the unique_together constraint on AlbumTrack works."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
        )
        track = Track.objects.create(spotify_id="t1", title="Test Track")
        AlbumTrack.objects.create(
            album=album, track=track, track_number=1, disc_number=1
        )
        with self.assertRaises(Exception):
            AlbumTrack.objects.create(
                album=album, track=track, track_number=2, disc_number=1
            )

    def test_album_track_ordering(self):
        """Test the ordering of AlbumTrack instances."""
        album = Album.objects.create(
            user=get_user_model().objects.create_user(username="testuser"),
            spotify_id="12345",
            title="Test Album",
        )
        track1 = Track.objects.create(spotify_id="t1", title="Track One")
        track2 = Track.objects.create(spotify_id="t2", title="Track Two")
        track3 = Track.objects.create(spotify_id="t3", title="Track Three")

        at1 = AlbumTrack.objects.create(
            album=album, track=track1, track_number=2, disc_number=1
        )
        at2 = AlbumTrack.objects.create(
            album=album, track=track2, track_number=1, disc_number=1
        )
        at3 = AlbumTrack.objects.create(
            album=album, track=track3, track_number=1, disc_number=2
        )

        album_tracks = AlbumTrack.objects.filter(album=album)
        self.assertEqual(
            list(album_tracks), [at2, at1, at3]
        )  # Ordered by disc_number then track_number


class IndexViewTests(TestCase):
    """Tests for the index view."""

    def test_index_view_status_code(self):
        """Test that the index view returns a 200 status code."""
        response = self.client.get(reverse("spotify_filter:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_template(self):
        """Test that the index view uses the correct template."""
        response = self.client.get(reverse("spotify_filter:index"))
        self.assertTemplateUsed(response, "spotify_filter/index.html")


class ImportingViewTests(TestCase):
    """Tests for the importing view."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_importing_view_status_code(self):
        """Test that the importing view returns a 200 status code."""
        response = self.client.get(reverse("spotify_filter:importing"))
        self.assertEqual(response.status_code, 200)

    def test_importing_view_template(self):
        """Test that the importing view uses the correct template."""
        response = self.client.get(reverse("spotify_filter:importing"))
        self.assertTemplateUsed(response, "spotify_filter/importing.html")


class ArtistDetailViewTests(TestCase):
    """Tests for the ArtistDetailView."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_artist_detail_view_status_code(self):
        """Test that the ArtistDetailView returns a 200 status code."""
        artist = Artist.objects.create(
            user=self.user,
            spotify_id="a1",
            name="Artist One",
        )
        response = self.client.get(
            reverse("spotify_filter:artist_detail", args=(artist.id,))
        )
        self.assertEqual(response.status_code, 200)

    def test_artist_detail_view_template(self):
        """Test that the ArtistDetailView uses the correct template."""
        artist = Artist.objects.create(
            user=self.user,
            spotify_id="a1",
            name="Artist One",
        )
        response = self.client.get(
            reverse("spotify_filter:artist_detail", args=(artist.id,))
        )
        self.assertTemplateUsed(response, "spotify_filter/artist_detail.html")


class AlbumDetailViewTests(TestCase):
    """Tests for the AlbumDetailView."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_album_detail_view_status_code(self):
        """Test that the AlbumDetailView returns a 200 status code."""
        album = Album.objects.create(
            user=self.user,
            spotify_id="12345",
            title="Test Album",
        )
        response = self.client.get(
            reverse("spotify_filter:album_detail", args=(album.id,))
        )
        self.assertEqual(response.status_code, 200)

    def test_album_detail_view_template(self):
        """Test that the AlbumDetailView uses the correct template."""
        album = Album.objects.create(
            user=self.user,
            spotify_id="12345",
            title="Test Album",
        )
        response = self.client.get(
            reverse("spotify_filter:album_detail", args=(album.id,))
        )
        self.assertTemplateUsed(response, "spotify_filter/album_detail.html")


class DashboardViewTests(TestCase):
    """Tests for the DashboardView."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_dashboard_view_status_code(self):
        """Test that the DashboardView returns a 200 status code."""
        response = self.client.get(reverse("spotify_filter:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_template(self):
        """Test that the DashboardView uses the correct template."""
        response = self.client.get(reverse("spotify_filter:dashboard"))
        self.assertTemplateUsed(response, "spotify_filter/dashboard.html")

    def test_dashboard_view_context(self):
        """Test that the DashboardView provides the correct context data."""
        artist1 = Artist.objects.create(
            user=self.user,
            spotify_id="a1",
            name="Artist One",
        )
        artist2 = Artist.objects.create(
            user=self.user,
            spotify_id="a2",
            name="Artist Two",
        )
        response = self.client.get(reverse("spotify_filter:dashboard"))
        self.assertIn(artist1, response.context["artist_list"])
        self.assertIn(artist2, response.context["artist_list"])


class ImportSpotifyTests(TestCase):
    """Tests for the Spotify data import functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open("spotify_filter/tests/data/albums2.json", "r", encoding="utf-8") as f:
            cls.two_albums = json.load(f)
        with open(
            "spotify_filter/tests/data/artists2.json", "r", encoding="utf-8"
        ) as f:
            cls.two_artists = json.load(f)

    def test_import_from_spotify_success(self):
        """Test that the import_from_spotify correctly imports data."""
        user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        mock_importer = MagicMock()
        mock_importer.retrieve_albums.return_value = self.two_albums
        mock_importer.retrieve_artists_by_id.return_value = self.two_artists
        mock_importer.user = user

        stats = import_from_spotify(user.id, importer=mock_importer)

        assert stats == {
            "albums_processed": 2,
            "albums_failed": 0,
            "artists_processed": 2,
            "artists_updated": 2,
            "artists_failed": 0,
            "tracks_processed": 25,
            "tracks_failed": 0,
        }
        assert Album.objects.count() == 2
        assert Artist.objects.count() == 2
        assert Track.objects.count() == 25
        assert AlbumTrack.objects.count() == 25

    @patch("spotify_filter.tasks.import_from_spotify")
    def test_celery_task_runs(self, mock_import):
        """Test that the import_spotify_data_task calls the import function."""
        user = get_user_model().objects.create_user(username="testuser")
        import_spotify_data_task(user.id)
        mock_import.assert_called_once()

    def test_import_from_spotify_data_error_in_album(self):
        """Test handling of KeyError exception when album data is weird"""
        mock_importer = MagicMock()
        mock_importer.retrieve_albums.return_value = [
            {
                "added_at": "",
                "album": {
                    "id": "123",
                    "title": "test_album",
                    "artists": [{"name": "test_artist", "id": "321"}],
                },
            }
        ]
        mock_importer.retrieve_artists_by_id.return_value = []

        user = get_user_model().objects.create_user(username="testuser")
        stats = import_from_spotify(user.id, importer=mock_importer)
        assert stats == {
            "albums_processed": 0,
            "albums_failed": 1,
            "artists_processed": 0,
            "artists_updated": 0,
            "artists_failed": 0,
            "tracks_processed": 0,
            "tracks_failed": 0,
        }

    def test_import_from_spotify_data_error_in_artist(self):
        """Test handling of KeyError exception when artist data is weird"""
        user = get_user_model().objects.create_user(username="testuser")
        mock_importer = MagicMock()
        mock_importer.retrieve_albums.return_value = self.two_albums
        correct_artists = self.two_artists
        mock_importer.retrieve_artists_by_id.return_value = [
            {"id": ar["id"]} for ar in correct_artists
        ]
        mock_importer.user = user

        stats = import_from_spotify(user.id, importer=mock_importer)
        assert stats == {
            "albums_processed": 2,
            "albums_failed": 0,
            "artists_processed": 2,
            "artists_updated": 0,
            "artists_failed": 2,
            "tracks_processed": 25,
            "tracks_failed": 0,
        }


class FilterTests(TestCase):
    """Tests for the filtering functionality in the dashboard."""

    def test_artist_genre_filter_and_logic(self):
        """Test dashboard filtering"""
        user = get_user_model().objects.create_user(username="testuser")
        indie = Genre.objects.create(name="indie Rock")
        experimental = Genre.objects.create(name="experimental")
        jazz = Genre.objects.create(name="jazz")

        artist1 = Artist.objects.create(
            user=user,
            spotify_id="01",
            name="Artist 1",
        )
        artist1.genres.add(indie, experimental)

        artist2 = Artist.objects.create(
            user=user,
            spotify_id="02",
            name="Artist 2",
        )
        artist2.genres.add(indie)

        artist3 = Artist.objects.create(
            user=user,
            spotify_id="03",
            name="Artist 3",
        )
        artist3.genres.add(jazz)

        # Should return only Artist 1, because only they have *both* genres
        filterset = ArtistFilter(data={"genre_name": "indie, experimental"})
        results = filterset.qs

        assert list(results) == [artist1]

    def test_album_filter_by_title(self):
        """Test album filtering by title"""
        user = get_user_model().objects.create_user(username="testuser")
        album1 = Album.objects.create(
            user=user,
            spotify_id="a1",
            title="The Dark Side of the Moon",
        )
        album2 = Album.objects.create(
            user=user,
            spotify_id="a2",
            title="The Wall",
        )
        album3 = Album.objects.create(
            user=user,
            spotify_id="a3",
            title="Abbey Road",
        )

        filterset = AlbumFilter(data={"album_name": "The"})
        results = filterset.qs

        assert album1 in results
        assert album2 in results
        assert album3 not in results
