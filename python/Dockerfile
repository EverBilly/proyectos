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
COPY archivos_facturas_enero.xlsx .

# (Opcional) Instalar dependencias si es necesario
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests pandas openpyxl matplotlib tabulate

# Dar permisos de ejecución al script
RUN chmod +x run.sh

# Comando por defecto cuando se inicie el contenedor
#CMD [ "python3", "extraer_montos.py" ]
#CMD [ "python3", "mostrar_montos.py" ]
#CMD sh -c "python3 extraer_montos.py && tail -f /dev/null"
CMD ["./run.sh"]