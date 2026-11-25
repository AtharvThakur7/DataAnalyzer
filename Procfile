web: gunicorn DataAnalyzer.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread --worker-tmp-dir /dev/shm --max-requests 1000 --max-requests-jitter 50 --timeout 120 --access-logfile - --error-logfile -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
