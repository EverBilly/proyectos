FROM python:3.11-slim

# Actualiza e instala dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        pkg-config \
        libmariadb-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto del código
COPY . .

# Exponer puerto de la app
EXPOSE 8000

# Comando de inicio usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "booking_project.wsgi:application"]