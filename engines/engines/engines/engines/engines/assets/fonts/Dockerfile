FROM python:3.10-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium \
    chromium-driver \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer Playwright
RUN playwright install chromium

# Copier tout le projet
COPY . .

# Port Streamlit
EXPOSE 7860

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
