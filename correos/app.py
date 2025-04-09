import imaplib
import email
from email.header import decode_header

# Configuración del servidor IMAP
IMAP_SERVER = 'imap.raiola.network'
EMAIL_ACCOUNT = 'TU_CORREO@TU_DOMINIO.COM'
PASSWORD = 'TU_CONTRASEÑA'

# Lista de empresas y sus correos asociados
EMPRESAS = {
    "Empresa 1": ["empresa1@sudominio.com", "daniempresa1@sudominio.com"],
    "Empresa 2": ["empresa2@sudominio.com", "joseempresa2@sudominio.com"],
    # Agrega más empresas aquí
}

# Tamaño del lote
BATCH_SIZE = 50

def connect_to_imap():
    """Conecta al servidor IMAP."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    return mail

def fetch_emails_in_batches(mail):
    """Busca correos y los organiza por empresa en lotes."""
    mail.select('inbox')  # Selecciona la bandeja de entrada
    status, messages = mail.search(None, 'ALL')  # Busca todos los correos
    email_ids = messages[0].split()

    # Procesar en lotes
    for i in range(0, len(email_ids), BATCH_SIZE):
        batch = email_ids[i:i + BATCH_SIZE]
        print(f"Procesando lote {i // BATCH_SIZE + 1} (correos {i + 1}-{i + len(batch)})")
        process_batch(mail, batch)

def process_batch(mail, batch):
    """Procesa un lote de correos."""
    for email_id in batch:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_address = msg.get('From', '').lower()  # Obtiene el remitente

                # Determina a qué empresa pertenece el correo
                for empresa, correos in EMPRESAS.items():
                    if any(correo.lower() in from_address for correo in correos):
                        print(f"Correo de {empresa}: {from_address}")
                        move_email_to_folder(mail, email_id, empresa)
                        break

def move_email_to_folder(mail, email_id, folder_name):
    """Mueve un correo a una carpeta específica."""
    try:
        mail.create(folder_name)  # Crea la carpeta si no existe
        mail.copy(email_id, folder_name)  # Copia el correo a la carpeta
        mail.store(email_id, '+FLAGS', '\\Deleted')  # Marca el correo para eliminarlo de la bandeja de entrada
        mail.expunge()  # Elimina el correo de la bandeja de entrada
        print(f"Correo movido a la carpeta: {folder_name}")
    except Exception as e:
        print(f"Error al mover correo: {e}")

def main():
    mail = connect_to_imap()
    fetch_emails_in_batches(mail)
    mail.logout()

if __name__ == '__main__':
    main()