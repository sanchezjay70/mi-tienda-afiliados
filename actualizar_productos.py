import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# === 1. TU CÓDIGO DE AFILIADO ===
MI_TAG_AFILIADO = "tu-codigo-21"  # Pon tu tag real de Amazon aquí

# === 2. SOLO TUS ENLACES (Python hará el resto) ===
ENLACES_AMAZON = [
    "https://link.amazon/B069mnmiX", 
    "https://link.amazon/B06UkY9Tn", 
    "https://link.amazon/B0j7e7GgZ",
    "https://link.amazon/B0cwHhChT", 
    "https://link.amazon/B0c5C9XLw", 
    "https://link.amazon/B02rKyKwe",
    "https://link.amazon/B0bD6BdAI", 
    "https://link.amazon/B09AAbGtn", 
    "https://link.amazon/B03sfDqSr",
    "https://link.amazon/B0aAEURgi", 
    "https://link.amazon/B00SjweNb", 
    "https://link.amazon/B04FiMXrH",
    "https://link.amazon/B02nq1zsx", 
    "https://link.amazon/B04Y4VWWD", 
    "https://link.amazon/B0ix1Skjc",
    "https://link.amazon/B00DXYAkp", 
    "https://link.amazon/B00QKWEDw", 
    "https://link.amazon/B01fpnlw4",
    "https://link.amazon/B0appfW92", 
    "https://link.amazon/B08Qoyyid", 
    "https://link.amazon/B05JqgofS",
    "https://link.amazon/B01TiNaKq", 
    "https://link.amazon/B0hzJawMW", 
    "https://link.amazon/B0cwYqSL3",
    "https://link.amazon/B0e0UywZ9", 
    "https://link.amazon/B04YNijKa", 
    "https://link.amazon/B03JC4NL5",
    "https://link.amazon/B0hwjP3KF", 
    "https://link.amazon/B0e4teK0D", 
    "https://link.amazon/B0gq8fhD4",
    "https://link.amazon/B04xICsAV", 
    "https://link.amazon/B0hur1vRe"
]

# Encabezado para que Amazon reconozca a Python como un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9'
}

def obtener_datos_amazon(url, index):
    try:
        # Añadir tag de afiliado si no lo tiene
        url_final = url
        if "?tag=" not in url and "&tag=" not in url:
            separador = "&" if "?" in url else "?"
            url_final = f"{url}{separador}tag={MI_TAG_AFILIADO}"

        # Consultar la página web de Amazon
        response = requests.get(url_final, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Extraer Título
            titulo_elem = soup.find(id='productTitle')
            nombre = titulo_elem.get_text().strip() if titulo_elem else f"Producto Oferta #{index + 1}"
            
            # 2. Extraer Imagen Principal
            img_elem = soup.find(id='landingImage') or soup.find(id='imgBlkFront')
            imagen = img_elem['src'] if img_elem and 'src' in img_elem.attrs else "https://m.media-amazon.com/images/I/71wF7YDIQkL._AC_SX679_.jpg"
            
            # 3. Extraer Precio
            precio_elem = soup.find('span', class_='a-offscreen')
            precio_texto = precio_elem.get_text().strip() if precio_elem else "29.99$"
            # Limpiar el precio para dejar solo el número
            precio_num = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
            try:
                precio = float(precio_num)
            except:
                precio = 29.99

            print(f"✅ [{index+1}/{len(ENLACES_AMAZON)}] Extraído: {nombre[:30]}... | {precio}€")
            
            return {
                "id": f"PROD-{index+1}",
                "nombre": nombre,
                "precio": precio,
                "imagen": imagen,
                "link_afiliado": url_final,
                "caracteristica": "Producto seleccionado con envío rápido y garantía Amazon."
            }
            
    except Exception as e:
        print(f"⚠️ Error al consultar enlace #{index+1}: {e}")

    # Si Amazon bloquea la consulta puntual, usa estos datos por defecto para no romper la web
    return {
        "id": f"PROD-{index+1}",
        "nombre": f"Producto Destacado Oferta #{index+1}",
        "precio": 29.99,
        "imagen": "https://m.media-amazon.com/images/I/71wF7YDIQkL._AC_SX679_.jpg",
        "link_afiliado": url,
        "caracteristica": "Garantía de calidad y mejor precio."
    }

def main():
    print(f"[{datetime.now()}] Iniciando extracción automática de Amazon...")
    catalogo = []
    
    for idx, url in enumerate(ENLACES_AMAZON):
        datos = obtener_datos_amazon(url, idx)
        catalogo.append(datos)
        
    with open('productos.json', 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=4)
        
    print("\n🎉 ¡Catálogo generado y actualizado automáticamente con éxito!")

if __name__ == "__main__":
    main()