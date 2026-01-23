#!/bin/bash
set -e

echo "Collecting static files to Azure Storage..."
python manage.py collectstatic --noinput
python manage.py migrate
echo "Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p 8000 core.asgi:application
