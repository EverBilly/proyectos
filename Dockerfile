# Image base python 3.11
FROM python:3.11

# Establecer el directorio de trabajo dentro 
WORKDIR /app_principal

# Instala las dependencias para conectar Django con MySql
RUN pip install django mysqlclient

# Expone el puerto que Django usara
EXPOSE 8000