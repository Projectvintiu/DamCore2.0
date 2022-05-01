#!/bin/bash

pip install --upgrade pip
pip install -r /app/requirements.txt

/scripts/wait-for-it.sh $DAMCore_DB_HOST:3306

export PYTHONPATH=$PYTHONPATH:/app
python /app/dev/reset_database.py

gunicorn -b [::]:8000 app:app --reload
