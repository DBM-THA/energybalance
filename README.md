# Installiere ein Python Virtual Environment

python -m venv .venv
# Aktiviere das Virtual Environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt

# Aktualisiere die Datenbank
python manage.py migrate 

# Starte den Server
python manage.py runserver 
