# 5SiTrec – Tracker Academic Personal
# (Proiect Vibecoded pentru ora de info de la liceu)

## Instalare & Pornire

### Prima rulare
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Rulări ulterioare
```bash
venv\Scripts\activate
python manage.py runserver
```

Accesează: http://127.0.0.1:8000/

## Cont demo
- Username: `admin`
- Parolă: `admin123`

## Funcționalități
- Dashboard cu media generală, absențe, consistency score, insights
- Materii: adaugă și urmărește mediile per materie
- Note: înregistrare cu calcul automat al mediei
- Absențe: motivate/nemotivate cu alerte
- Study Check-in: urmărire zilnică ore studiu, productivitate, înțelegere, stres
- Reflecții săptămânale: ce a mers, dificultăți, obiective

## Pitch tehnical

**5SiTrec** este o aplicație web construită cu **Django**, un framework Python full-stack care gestionează atât logica de server cât și interfața vizuală.

Arhitectura urmează pattern-ul **MVT** — Model, View, Template. Modelele definesc structura bazei de date, view-urile conțin logica aplicației, iar templateurile generează HTML-ul trimis către browser. Toate requesturile trec prin `urls.py` care le direcționează către view-ul corespunzător.

Datele sunt persistate într-o bază **SQLite** — un fișier local, fără server separat, ideal pentru aplicații single-user. Autentificarea folosește sistemul built-in Django: parolele sunt stocate **hashed cu PBKDF2 + SHA256**, niciodată în clar.

Fiecare endpoint acceptă atât `GET` cât și `POST` pe același URL — modelul clasic Django fără API REST separat. Vizualizările sunt generate cu **Chart.js** pe client, datele fiind injectate direct din Python în template prin variabile de context serializate JSON.

Aplicația rulează **complet local**, fără dependențe externe sau servicii cloud — `pip install`, `migrate`, `runserver` și funcționează.
