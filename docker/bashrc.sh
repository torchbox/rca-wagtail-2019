# Note: This file is loaded on all environments, even production.

alias dj="python manage.py"

if [ "$BUILD_ENV" = "dev" ]; then
    alias djrun="python manage.py runserver 0.0.0.0:8000"
    alias djtest="python manage.py test --settings=rca.settings.test"
fi