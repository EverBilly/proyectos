import pandas as pd

# Función para limpiar montos
def limpiar_monto(valor):
    if isinstance(valor, str):
        # Eliminar separadores de miles (puntos o comas) y convertir comas decimales a puntos
        valor = valor.replace('.', '').replace(',', '.')  # Elimina puntos y convierte comas a puntos
    return float(valor)

# Función principal para procesar los archivos
def procesar_archivos(archivo_movimientos, archivo_facturas, columna_monto_movimientos, columna_monto_facturas):
    # Cargar el archivo de movimientos
    try:
        df_movimientos = pd.read_csv(archivo_movimientos)
        df_movimientos[columna_monto_movimientos] = df_movimientos[columna_monto_movimientos].apply(limpiar_monto)
    except Exception as e:
        print(f"Error al cargar el archivo de movimientos: {e}")
        return

    # Cargar el archivo de facturas
    try:
        df_facturas = pd.read_excel(archivo_facturas, engine='openpyxl')
        df_facturas[columna_monto_facturas] = df_facturas[columna_monto_facturas].apply(limpiar_monto)
    except Exception as e:
        print(f"Error al cargar el archivo de facturas: {e}")
        return

    # Crear columnas adicionales en el archivo de movimientos
    df_movimientos['Existe en Facturas'] = 'No'
    df_movimientos['Ruta Archivo Facturas'] = None

    # Iterar sobre los movimientos y buscar coincidencias en las facturas
    for idx, row in df_movimientos.iterrows():
        monto_movimiento = abs(row[columna_monto_movimientos])  # Ignorar el signo del movimiento
        match = df_facturas[df_facturas[columna_monto_facturas] == monto_movimiento]

        if not match.empty:
            # Si se encuentra el monto, actualizar las columnas correspondientes
            df_movimientos.at[idx, 'Existe en Facturas'] = 'Sí'
            df_movimientos.at[idx, 'Ruta Archivo Facturas'] = match.iloc[0]['Ruta']

    # Guardar el archivo resultante
    output_path = '/app/resultado.xlsx'
    df_movimientos.to_excel(output_path, index=False, engine='openpyxl')
    print(f"El archivo resultante ha sido guardado exitosamente en: {output_path}")

# Ejecutar el procesamiento
if __name__ == "__main__":
    # Rutas de los archivos
    archivo_movimientos = '/app/movimientos_cuenta.csv'  # Archivo de movimientos (CSV)
    archivo_facturas = '/app/archivos_facturas.xlsx'     # Archivo de facturas (Excel)

    # Nombres de las columnas de montos en ambos archivos
    columna_monto_movimientos = 'IMPORTE'  # Columna de montos en el archivo de movimientos
    columna_monto_facturas = 'Valor'      # Columna de montos en el archivo de facturas

    # Procesar los archivos
    procesar_archivos(archivo_movimientos, archivo_facturas, columna_monto_movimientos, columna_monto_facturas)