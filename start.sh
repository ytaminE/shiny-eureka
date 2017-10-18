./venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=1 --access-logfile access.log --error-logfile error.log app:app
export APP_CONFIG_FILE=production.py
python run.py
