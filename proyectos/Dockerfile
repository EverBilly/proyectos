# Image base python 3.11
FROM python:3.11

# Establecer el directorio de trabajo dentro 
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias para conectar Django con MySql
RUN pip install django mysqlclient

# Expone el puerto que Django usara
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]