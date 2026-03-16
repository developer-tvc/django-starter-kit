#!/bin/bash


while ! pg_isready -h host.docker.internal -p 5432 -U postgres
do
  sleep 2
done

echo "Database started"

if [ "$ENV" = "local" ]; then
    echo "Running makemigrations..."
    python manage.py migrate --settings=config.settings.$ENV
fi

echo "Running migrations..."
python manage.py migrate --settings=config.settings.$ENV
echo "Starting Django..."

python manage.py runserver 0.0.0.0:8000 --settings=config.settings.$ENV