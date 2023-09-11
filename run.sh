#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

echo "Creation superuser" && python manage.py createsuperuser --noinput || echo "Anny issue on creation superuser"