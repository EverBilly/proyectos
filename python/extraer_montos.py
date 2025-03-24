import os
import requests
import re
import pandas as pd

# Configuración de la aplicación
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



# Paso 5: Listar archivos en la carpeta compartida
url = f'https://graph.microsoft.com/v1.0/drives/{cid}/root/children'
headers = {
    'Authorization': f'Bearer {access_token}'
}
response = requests.get(url, headers=headers)
items = response.json().get('value', [])

# Buscar la carpeta "Facturas"
folder_name = 'Facturas'
folder_id = None

for item in items:
    if item.get('name') == folder_name and item.get('folder'):
        folder_id = item.get('id')
        break

if not folder_id:
    raise ValueError(f"No se encontró la carpeta '{folder_name}'")

# Función para obtener el ID de una subcarpeta
def obtener_id_subcarpeta(cid, folder_id, folder_name, access_token):
    url = f'https://graph.microsoft.com/v1.0/drives/{cid}/items/{folder_id}/children'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    items = response.json().get('value', [])

    # Buscar la subcarpeta por su nombre
    for item in items:
        if item.get('name') == folder_name and item.get('folder'):
            return item.get('id')

    raise ValueError(f"No se encontró la subcarpeta '{folder_name}'")

# Navegar a través de las subcarpetas
try:
    folder_id_2025 = obtener_id_subcarpeta(cid, folder_id, '2025', access_token)
    folder_id_1trimestre = obtener_id_subcarpeta(cid, folder_id_2025, '1T', access_token)
    folder_id_enero = obtener_id_subcarpeta(cid, folder_id_1trimestre, 'MARZO', access_token)
except ValueError as e:
    print(e)
    exit()

# Listar archivos en la carpeta "ENERO"
url = f'https://graph.microsoft.com/v1.0/drives/{cid}/items/{folder_id_enero}/children'
response = requests.get(url, headers=headers)
files = response.json().get('value', [])

# Expresión regular mejorada para dividir el nombre del archivo
pattern = re.compile(r'(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d{1,5}(?:[.,]\d{3})*(?:[.,]\d{2})?)\.(\w+)')

# Obtener la ruta de salida de una variable de entorno
output_path = ('/app/archivos_facturas.xlsx')

# Lista de archivos procesados
data = []

for file in files:
    file_name = file.get('name')
    match = pattern.match(file_name)
    if match:
        fecha, nombre_empresa, monto, extension = match.groups()
        data.append([fecha, nombre_empresa, monto, extension])
    else:
        print(f"No se pudo extraer la información del archivo: {file_name}")

# Crear el DataFrame
df = pd.DataFrame(data, columns=['Fecha', 'Nombre Empresa', 'Monto', 'Extensión'])
print(df)

# Guardar el DataFrame en un archivo de Excel
df.to_excel(output_path, index=False)
print(f'Archivo de Excel guardado correctamente {output_path}')

# Verificar si el archivo existe y no está vacío
if not os.path.exists(output_path):
    raise ValueError(f"El archivo {output_path} no existe.")

with open(output_path, 'rb') as file:
    file_content = file.read()
    if not file_content:
        raise ValueError(f"El archivo {output_path} está vacío.")
