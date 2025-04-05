import os
import requests
import re
import pandas as pd

# Patrón para extraer información de nombres de archivos
pattern = re.compile(r'(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d{1,5}(?:[.,]\d{3})*(?:[.,]\d{2})?)\.(\w+)')

# Función para obtener los elementos de una carpeta (archivos y subcarpetas)
def obtener_elementos(cid, folder_id, access_token):
    url = f'https://graph.microsoft.com/v1.0/drives/{cid}/items/{folder_id}/children'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error al acceder a la carpeta. Código: {response.status_code}, Mensaje: {response.text}")
    return response.json().get('value', [])

# Función recursiva para explorar carpetas y subcarpetas
def explorar_carpeta(cid, folder_id, access_token, ruta_actual="", datos=[], filtro_anio=None, filtro_trimestre=None):
    elementos = obtener_elementos(cid, folder_id, access_token)
    for elemento in elementos:
        nombre = elemento.get('name')
        tipo = 'Carpeta' if elemento.get('folder') else 'Archivo'
        id_elemento = elemento.get('id')
        nueva_ruta = f"{ruta_actual}/{nombre}" if ruta_actual else nombre

        # Si es una carpeta, verificar si coincide con el filtro de año o trimestre
        if tipo == 'Carpeta':
            if filtro_anio and nombre == filtro_anio:
                # Si coincide con el año, continuar explorando
                explorar_carpeta(cid, id_elemento, access_token, nueva_ruta, datos, filtro_anio=None, filtro_trimestre=filtro_trimestre)
            elif filtro_trimestre and nombre == filtro_trimestre:
                # Si coincide con el trimestre, continuar explorando
                explorar_carpeta(cid, id_elemento, access_token, nueva_ruta, datos, filtro_anio=None, filtro_trimestre=None)
            else:
                # Si no coincide con el filtro, explorar recursivamente
                explorar_carpeta(cid, id_elemento, access_token, nueva_ruta, datos, filtro_anio, filtro_trimestre)

        # Si es un archivo, intentar extraer información usando el patrón
        elif tipo == 'Archivo':
            match = pattern.match(nombre)
            if match:
                fecha, descripcion, valor, extension = match.groups()
                datos.append({
                    'Fecha': fecha,
                    'Descripción': descripcion,
                    'Valor': valor,
                    'Extensión': extension,
                    'Ruta': nueva_ruta
                })
            else:
                print(f"No se pudo extraer la información del archivo: {nombre}")

# Función principal para ejecutar el proceso
def main():
    # Configuración inicial
    client_id = 'd8f37651-8b65-4a18-a250-4899fcce9579'
    redirect_uri = 'https://login.microsoftonline.com/common/oauth2/nativeclient'
    scopes = 'Files.ReadWrite.All'

    # Paso 1: Generar la URL de autenticación manualmente
    auth_url = (
        f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?'
        f'client_id={client_id}&'
        f'response_type=code&'
        f'redirect_uri={redirect_uri}&'
        f'scope={scopes}'
    )

    print("Por favor, abre la siguiente URL en tu navegador para autenticarte:")
    print(auth_url)
    print("\nDespués de autenticarte, serás redirigido a una página en blanco.")
    print("Copia la URL completa de la página y pégala aquí.")

    # Paso 2: Obtener el código de autorización
    redirected_url = input("Pega la URL aquí: ")

    # Extraer el código de autorización de la URL
    try:
        code = redirected_url.split('code=')[1].split('&')[0]
    except IndexError:
        raise ValueError("No se pudo extraer el código de autorización de la URL.")

    # Paso 3: Intercambiar el código por un token de acceso
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri,
        'scope': scopes
    }
    token_response = requests.post(token_url, data=token_data)

    # Verificar si se obtuvo el token de acceso
    if token_response.status_code != 200:
        print("Error al obtener el token de acceso:")
        print(token_response.json())
        raise ValueError("No se pudo obtener el token de acceso")

    access_token = token_response.json().get('access_token')

    if not access_token:
        raise ValueError("No se pudo obtener el token de acceso")

    # Paso 4: Obtener el ID del recurso compartido
    shared_link = 'https://1drv.ms/f/s!AtvsAW50wkpjlAc08BnmGvfU4Zs7'

    # Abre el enlace compartido en tu navegador y copia la URL completa
    print("Por favor, abre el siguiente enlace en tu navegador y copia la URL completa:")
    print(shared_link)
    print("\nDespués de que se cargue la página, copia la URL completa de la barra de direcciones y pégala aquí.")
    full_url = input("Pega la URL completa aquí: ")

    # Extraer el cid de la URL completa
    try:
        cid = full_url.split('cid=')[1].split('&')[0]
    except IndexError:
        raise ValueError("No se pudo extraer el cid de la URL completa.")

    # Paso 5: Solicitar el año y el trimestre al usuario
    filtro_anio = input("Ingresa el año que deseas procesar (ej. 2025): ")
    filtro_trimestre = input("Ingresa el trimestre que deseas procesar (1T, 2T, 3T, 4T): ").upper()

    # Paso 6: Explorar la carpeta principal y sus subcarpetas
    try:
        # Lista para almacenar todos los datos
        datos = []

        # Explorar la carpeta principal y sus subcarpetas
        explorar_carpeta(cid, 'root', access_token, datos=datos, filtro_anio=filtro_anio, filtro_trimestre=filtro_trimestre)

        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(datos)

        # Guardar los datos en un archivo Excel
        output_path = '/app/archivos_facturas.xlsx'
        df.to_excel(output_path, index=False)
        print(f"El archivo Excel ha sido generado exitosamente en: {output_path}")

        # Verificar si el archivo existe y no está vacío
        if not os.path.exists(output_path):
            raise ValueError(f"El archivo {output_path} no existe.")
        with open(output_path, 'rb') as file:
            file_content = file.read()
            if not file_content:
                raise ValueError(f"El archivo {output_path} está vacío.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Ejecutar el programa
if __name__ == "__main__":
    main()