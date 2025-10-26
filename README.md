[![Testing CI](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/tests.yml/badge.svg)](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/tests.yml)
[![Code Quality CI](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/code_quality.yml)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

# Spotify Music Library Manager

This web app loads the saved albums from your Spotify library and allows you to browse or filter the albums at your leisure.

![Dashboard Screenshot](path/to/screenshot.png)

## Features

- 🎵 [Feature 1]
- 📊 [Feature 2]
- ⚡ [Feature 3]
- 🔄 [Feature 4]

## Tech Stack

**Backend:** Django, Celery, Redis, PostgreSQL
**APIs:** Spotify Web API (via Spotipy)
**Frontend:** Django templates, django-tables2, django-filter
**Dev Tools:** GitHub Actions (CI/CD), black, isort, flake8, pylint

## Screenshots

### Dashboard
[Screenshot of main dashboard]

### Artist Detail
[Screenshot of artist detail page]

## Setup

### Prerequisites
- Python 3.x
- PostgreSQL
- Redis
- Spotify Developer Account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AlenkaJ/SpotifyDjangoApp.git
cd SpotifyDjangoApp
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root:
```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8000/callback
DATABASE_URL=postgresql://user:password@localhost:5432/spotify_db
CELERY_BROKER_URL=redis://localhost:6379/0
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Start Redis (in separate terminal):
```bash
redis-server
```

6. Start Celery worker (in separate terminal):
```bash
celery -A [your_project_name] worker -l info
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Visit `http://localhost:8000` and start importing your Spotify data!

## Usage

[Brief description of how to use the app - import data, browse, filter, etc.]

## Project Structure
```
spotify_app/
├── spotify_filter/       # Main Django app
├── templates/           # HTML templates
├── static/             # CSS, JS, images
└── ...
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
The project uses GitHub Actions for automated testing and code quality checks (black, isort, flake8, pylint).

## Future Improvements

- [ ] [Thing you want to add]
- [ ] [Another thing]
- [ ] [etc.]

## Related Projects

This project evolved from an earlier data analysis exploration: [SpotifyShenanigans](https://github.com/AlenkaJ/SpotifyShenanigans)

## License

[Your choice - MIT is common for portfolio projects]

a server needs to be running for the site to work:
(browsing existing dashboard etc works)
```
python manage.py runserver
```

Celery needs to be running in the background for the spotify loading to work properly - it runs background task:
```
celery -A analytics_site worker -l info --pool=solo
```

(run each of those in separate cmd)
