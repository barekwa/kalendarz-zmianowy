# Użyj obrazu bazowego Python
FROM python:3.9

# Ustal katalog roboczy
WORKDIR /app

# Skopiuj plik requirements.txt
COPY requirements.txt .

# Zainstaluj zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę plików aplikacji
COPY . .

# Port, na którym działa serwer back-endowy (możesz zmienić, jeśli inny port jest używany)
EXPOSE 8080

# Komenda do uruchomienia serwera
CMD ["python", "app.py"]
