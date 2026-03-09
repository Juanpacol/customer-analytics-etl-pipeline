import json
import os
import boto3
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine

# Configuraciones
BUCKET_NAME = "pipeline-juan-analytics-2026"  
TARGET_URL = "https://www.trustpilot.com/review/www.santander.co.uk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
# Usando puerto 6543 (Connection Pooler de Supabase) para evitar restricciones Serverless
DB_CONNECTION_STRING = os.environ.get("DB_URI", "postgresql+pg8000://postgres.hffjkhhouhweguptxzyo:JuanAnalytics2026@aws-0-us-west-2.pooler.supabase.com:6543/postgres")

def lambda_handler(event=None, context=None):
    """
    Función principal que actúa como 'Handler' para AWS Lambda.
    Automatiza el ciclo E-T-L en una sola pasada.
    """
    print("=== Iniciando Pipeline ETL Automático ===")
    
    # 1. EXTRAER (Extract)
    print("1. Extrayendo datos...")
    raw_data = extract_reviews(pages=2)
    if not raw_data:
        return {"statusCode": 500, "body": "Fallo la extracción de datos"}
        
    # 2. TRANSFORMAR (Transform)
    print("2. Transformando datos con Pandas...")
    df = transform_data(raw_data)
    
    # 3. CARGAR (Load a S3)
    print(f"3. Cargando {len(df)} registros a AWS S3...")
    success_s3 = load_to_s3(df)
    
    # 4. CARGAR (Load a PostgreSQL)
    print(f"4. Cargando datos a PostgreSQL (Supabase)...")
    success_db = load_to_postgres(df)
    
    if success_s3 and success_db:
        return {"statusCode": 200, "body": "ETL finalizado con éxito (S3 y BD actualizados)."}
    else:
        return {"statusCode": 500, "body": "Fallo parcial en la carga de S3 o BD."}

def extract_reviews(pages):
    all_reviews = []
    
    for page in range(1, pages + 1):
        url = f"{TARGET_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        review_cards = soup.find_all("article", class_=lambda value: value and "CDS_Card_card" in value)
        
        for card in review_cards:
            try:
                title_elem = card.find("h2")
                title = title_elem.get_text(strip=True) if title_elem else "Sin Título"

                paragraphs = card.find_all("p")
                body = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10])

                rating = None
                img_elem = card.find("img", alt=lambda value: value and "Rated" in value)
                if img_elem and "alt" in img_elem.attrs:
                    try:
                        rating = int(img_elem["alt"].split(" ")[1])
                    except ValueError:
                        rating = None

                all_reviews.append({
                    "title": title,
                    "body": body if body else "Sin Texto",
                    "rating": rating,
                    "company": "Santander",
                    "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception:
                continue
    return all_reviews

def transform_data(reviews_data):
    df = pd.DataFrame(reviews_data)
    df.dropna(subset=['rating'], inplace=True)
    df['sentiment'] = df['rating'].apply(lambda x: 'Positive' if x >= 4 else ('Neutral' if x == 3 else 'Negative'))
    df['body'] = df['body'].str.replace(r'\n|\r', ' ', regex=True)
    return df

def load_to_s3(df):
    try:
        # En la nube (AWS Lambda), solo podemos guardar archivos temporales en la ruta /tmp/
        # Simularemos este comportamiento aquí, o lo guardaremos en la ruta actual si falla
        filename = f"santander_reviews_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        temp_path = f"/tmp/{filename}" if os.name != 'nt' else filename
        
        # Exportar CSV temporal
        df.to_csv(temp_path, index=False, encoding='utf-8')
        
        # Subir a S3 usando Boto3 (Requiere llaves inyectadas en consola o Rol de IAM en Lambda)
        s3_client = boto3.client('s3')
        s3_key = f"raw_data/analytics/{filename}"
        s3_client.upload_file(temp_path, BUCKET_NAME, s3_key)
        
        print(f"[+] ¡Subida exitosa: s3://{BUCKET_NAME}/{s3_key}")
        
        # Limpieza (opcional local, recomendado en Lambda)
        if os.path.exists(temp_path):
             os.remove(temp_path)
             
        return True
    except Exception as e:
         print(f"[!] Error al cargar a S3: {e}")
         return False

def load_to_postgres(df):
    try:
        # ATENCIÓN: El motor conectará a la nube y mandará nuestro dataframe
        engine = create_engine(DB_CONNECTION_STRING)
        # to_sql crea automáticamente la tabla si no existe (modo append=agregar al final)
        df.to_sql('santander_reviews', engine, if_exists='append', index=False)
        print("[+] ¡Carga exitosa en Base de Datos PostgreSQL!")
        return True
    except Exception as e:
        print(f"[!] Error al cargar a PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    # Test local
    lambda_handler()
