pip install wheel
pip install -r requirements.txt

# python manage.py migrate
python3.9 manage.py collectstatic --no-input
# python manage.py loaddata currencies.json