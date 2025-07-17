FROM python:3.11-slim

# Actualiza paquetes y agrega dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        pkg-config \
        libc-dev \
        libjpeg-dev \
        zlib1g-dev \
        libmariadb-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Directorio de trabajo
WORKDIR /app

# Copia requirements
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . /app/

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "booking_project.wsgi:application"]