# Mini Inventory

Egyszerű Flask + SQLite készletkezelő webalkalmazás. A projekt egy CI/CD beadandó alkalmazásoldali alapja.

## Funkciók

- Termék felvétele (cikkszám, név, egységár, kezdő készlet)
- Termékek listázása
- Készlet növelése és csökkentése
- Negatív készlet tiltása
- Egyedi cikkszám ellenőrzése
- Figyelmeztetés 5 darab alatti készletnél
- Termék törlése
- `/health` végpont későbbi deployment-ellenőrzéshez

## Követelmények

- Python 3.10 vagy újabb
- pip

## Indítás Windows PowerShellben

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

Ezután nyisd meg: http://127.0.0.1:5000

Ha a PowerShell nem engedi a virtuális környezet aktiválását, futtasd közvetlenül a környezet Pythonját:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

## Adatbázis

Az SQLite adatbázis automatikusan létrejön az `instance/inventory.sqlite` útvonalon. Az `instance/` könyvtár nincs verziókezelés alatt.

## Health check

A `http://127.0.0.1:5000/health` végpont sikeres adatbázis-kapcsolat esetén HTTP 200 választ és `{"status":"ok"}` tartalmat ad.

## Következő fejlesztési mérföldkövek

1. Automatizált tesztek Pytesttel
2. Docker image és tartós adatbázis-volume
3. GitHub Actions CI/CD workflow
4. Image publikálása GitHub Container Registrybe
5. Deployment felhős sandboxba
