import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

# ======== CONFIGURACIÓN ========
# Usamos el bucket que acabas de crear
BUCKET_NAME = "pipeline-juan-analytics-2026"  

def upload_to_s3(file_path, bucket=BUCKET_NAME):
    """
    Sube un archivo local a un Bucket de Amazon S3.
    """
    if not os.path.exists(file_path):
        print(f"[!] El archivo {file_path} no existe localmente.")
        return False
        
    file_name = os.path.basename(file_path)
    
    # Boto3 leerá automáticamente tus credenciales desde la terminal
    s3_client = boto3.client('s3')

    try:
        print(f"[*] Subiendo {file_name} a S3 ({bucket})...")
        s3_client.upload_file(file_path, bucket, f"raw_data/{file_name}")
        print(f"[+] ¡Subida exitosa a la nube! s3://{bucket}/raw_data/{file_name}")
        return True
        
    except FileNotFoundError:
        print("[!] Archivo no encontrado.")
        return False
    except NoCredentialsError:
        print("[!] ERROR: No se encontraron credenciales de AWS válidas.")
        print(" -> Asegúrate de ejecutar 'aws configure' en tu terminal.")
        return False
    except ClientError as e:
        print(f"[!] Error de AWS ('ClientError'): {e}")
        return False
    except Exception as e:
         print(f"[!] Error desconocido: {e}")
         return False

if __name__ == "__main__":
    # Prueba de subida rápida con el archivo que acabamos de crear
    # Reemplaza el nombre del archivo si guardaste con fecha distinta
    import glob
    csv_files = glob.glob("santander_reviews_*.csv")
    if csv_files:
        latest_file = sorted(csv_files)[-1]
        upload_to_s3(latest_file)
    else:
        print("No hay archivos CSV locales para subir. Ejecuta scraper.py primero.")
