#!/usr/bin/env sh

# Wait for database to be ready
echo "Waiting for database to be ready..."
until /app/bin/python manage.py check --database default > /dev/null 2>&1; do
  echo "MySQL is unavailable - sleeping"
  sleep 3
done
echo "MySQL is up - executing commands"
  
/app/bin/python manage.py migrate --noinput
/app/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 poetfolio.wsgi:application

