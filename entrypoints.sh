#!/bin/bash
set -euo pipefail

echo "⏳ Waiting for database..."
until python manage.py dbshell -c "SELECT 1;" >/dev/null 2>&1; do
    echo "Database not ready yet, retrying in 2s..."
    sleep 2
done
echo "✅ Database is ready!"

echo "▶️  Checking and running migrations if needed"
if python manage.py showmigrations --plan | grep '\[ \]'; then
    python manage.py migrate --noinput
else
    echo "✅ No migrations to apply"
fi

echo "🔁 Syncing Celery Beat schedules (DB)"
python manage.py sync_beat || echo "⚠️  'sync_beat' not available or failed; continuing."

echo "👤 Checking superuser (optional)"
python manage.py shell <<'PY'
from decouple import config
from django.contrib.auth import get_user_model
User = get_user_model()
phone = config('DJANGO_SUPERUSER_PHONE_NUMBER', default=None)
pwd   = config('DJANGO_SUPERUSER_PASSWORD', default=None)
if phone and pwd and not User.objects.filter(phone_number=phone).exists():
    print(f"Creating superuser {phone}...")
    User.objects.create_superuser(phone_number=phone, password=pwd)
    print("Superuser created.")
else:
    print("Superuser exists or env not provided; skipping.")
PY

echo "🧹 Collecting static files"
python manage.py collectstatic --noinput || echo "⚠️ Failed to collect static, continuing..."

echo "🚀 Starting Gunicorn"
exec gunicorn src.config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --log-level info
