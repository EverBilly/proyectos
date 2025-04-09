FROM python:latest

# Instalar dependencias
RUN pip install pandas openpyxl flask chardet

# Copiar archivos
COPY . /app
WORKDIR /app

# Copiar archivos específicos

# Exponer puerto
EXPOSE 6000

#docker build -t contabilidad-app .
#docker run --rm -p 5000:5000 contabilidad-app
# Ejecutar aplicación
#docker run -v /Users/evercifuentes/proyectos/contabilidad:/app/archivos \
#           -e RUTA_FACTURAS=/app/archivos/archivos_facturas.xlsx \
#           -e RUTA_MOVIMIENTOS=/app/archivos/movimientos_cuenta.csv \
#           -e RUTA_SALIDA=/app/archivos/resultado.xlsx \
#           conta

#docker run contabilidad sh -c "python app.py && tail -f /dev/null"
#docker cp c2895bfc4d8b:/app/facturas_sin.xlsx .

CMD ["sh", "-c", "pyhton app.py && tail -f /dev/null"]