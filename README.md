# aiohttp-n-sqlalchemy
Test application with aiohttp and sqlalchemy

How to run: 
1. Create test postgresql db: https://aiohttp-demos.readthedocs.io/en/latest/preparations.html#initial-setup
2. PYTHONPATH=${PYTHONPATH}:app:src DB_CONFIG=configs/db.yaml SHORTENER_CONFIG=configs/shortener.yaml python3 app/main.py
