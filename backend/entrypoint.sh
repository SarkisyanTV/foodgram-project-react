gunicorn --bind 0.0.0.0:8000 foodgram.wsgi

python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py collectstatic --noinput

cp -r static/. /static
