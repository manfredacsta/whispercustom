FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requisitos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que usará la aplicación
EXPOSE $PORT

# Comando para ejecutar la aplicación
CMD gunicorn --bind 0.0.0.0:$PORT app:app
