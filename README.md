[![Testing CI](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/tests.yml/badge.svg)](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/tests.yml)
[![Code Quality CI](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AlenkaJ/SpotifyDjangoApp/actions/workflows/code_quality.yml)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

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
