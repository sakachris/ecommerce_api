#!/bin/bash

set -e

echo "⏳ Waiting for database to be ready..."

# Wait until Postgres is ready
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  sleep 5
done

echo "✅ Postgres is up - continuing..."

echo "🧱 Making migrations..."
python manage.py makemigrations --noinput

echo "🛠️ Applying database migrations..."
python manage.py migrate --noinput

# Create a default superuser
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
  echo "👤 Creating superuser..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
first_name = os.getenv("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
last_name = os.getenv("DJANGO_SUPERUSER_LAST_NAME", "User")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password
    )
EOF
fi

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django app..."
exec "$@"