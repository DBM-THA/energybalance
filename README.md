# Installiere ein Python Virtual Environment

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Aktualisiere die Datenbank
python manage.py migrate 

# Starte den Server
python manage.py runserver 
