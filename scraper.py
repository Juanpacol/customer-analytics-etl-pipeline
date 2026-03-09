import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

# Configuraciones
# Usaremos Trustpilot apuntando a un banco de ejemplo (Banco Santander UK)
TARGET_URL = "https://www.trustpilot.com/review/www.santander.co.uk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_trustpilot_reviews(pages=1):
    """
    Extrae reseñas de Trustpilot para la página objetivo.
    :param pages: Cantidad de páginas a raspar (20 reseñas por página aprox.)
    :return: Lista de diccionarios con la info de cada reseña.
    """
    all_reviews = []
    print(f"[*] Iniciando extracción en: {TARGET_URL}")

    for page in range(1, pages + 1):
        print(f" -> Raspando página {page}...")
        url = f"{TARGET_URL}?page={page}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"[!] Error al acceder a la página {page}. Código de estado: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Nuevos selectores de Trustpilot basados en exploración manual
        review_cards = soup.find_all("article", class_=lambda value: value and "CDS_Card_card" in value)
        
        if not review_cards:
             print("[!] No se encontraron tarjetas de reseña en esta página. (Posible bloqueo o cambio de HTML)")
             break

        for card in review_cards:
            try:
                # 1. Título (h2)
                title_elem = card.find("h2")
                title = title_elem.get_text(strip=True) if title_elem else "Sin Título"

                # 2. Cuerpo del texto (p)
                # Seleccionamos todos los párrafos y tomamos usualmente el último, o el que tiene más texto
                paragraphs = card.find_all("p")
                body = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10])
                if not body:
                    body = "Sin Texto"

                # 3. Clasificación (Estrellas)
                # Las estrellas en TP generalmente vienen en una imagen <img alt="Rated 1 out of 5 stars">
                rating = None
                img_elem = card.find("img", alt=lambda value: value and "Rated" in value)
                if img_elem and "alt" in img_elem.attrs:
                    alt_text = img_elem["alt"]
                    # Extraer el numero, ej: "Rated 1 out of 5..."
                    try:
                        rating = int(alt_text.split(" ")[1])
                    except ValueError:
                        rating = None

                all_reviews.append({
                    "title": title,
                    "body": body,
                    "rating": rating,
                    "company": "Santander",
                    "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                print(f"[!] Error al parsear una reseña: {e}")
                continue
                
        time.sleep(2) # Pausa amigable entre páginas
        
    return all_reviews

def transform_and_save(reviews_data):
    """
    Convierte la lista a Pandas DataFrame, limpia datos y exporta a CSV.
    """
    if not reviews_data:
         print("[-] No hay datos para guardar.")
         return

    df = pd.DataFrame(reviews_data)
    
    # Transformación Básica
    # 1. Eliminar filas sin calificación
    df.dropna(subset=['rating'], inplace=True)
    
    # 2. NLP básico: Categorizar sentimiento basado en las estrellas.
    df['sentiment'] = df['rating'].apply(lambda x: 'Positive' if x >= 4 else ('Neutral' if x == 3 else 'Negative'))
    
    # 3. Limpieza de texto sencilla (quitar saltos de linea extraños)
    df['body'] = df['body'].str.replace(r'\n|\r', ' ', regex=True)

    # Exportar Data "Limpia" a local
    filename = f"santander_reviews_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"[*] Guardado exitoso: {filename} con {len(df)} reseñas.")
    
    # Imprimimos una pequeña muestra
    print("\n--- Muestra de los datos procesados ---")
    print(df[['rating', 'sentiment', 'title']].head(3))

if __name__ == "__main__":
    # Prueba inicial raspando solo la página 1 y 2
    raw_data = extract_trustpilot_reviews(pages=2)
    transform_and_save(raw_data)
