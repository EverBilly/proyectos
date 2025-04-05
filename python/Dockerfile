# Usar una imagen base de python
FROM python:latest

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# (Opcional) Copiar un archivo de requisitos si tienes dependencias
#COPY requirements.txt .
COPY extraer_montos.py .
COPY run.sh .
COPY mostrar_montos.py .

# (Opcional) Instalar dependencias si es necesario
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests pandas openpyxl matplotlib tabulate

# Dar permisos de ejecución al script
RUN chmod +x run.sh

# Comando por defecto cuando se inicie el contenedor
#CMD [ "python3", "extraer_montos.py" ]
#CMD [ "python3", "mostrar_montos.py" ]
#CMD sh -c "python3 extraer_montos.py && tail -f /dev/null"

#docker run -v ~/docker_output:/app -e OUTPUT_PATH=/app/archivos_facturas.xlsx python_container
#docker build -t python_container .
#docker run -it --rm python_container
#docker cp d7ccccf7eb72:/app/archivos_facturas.xlsx .

CMD ["./run.sh"]