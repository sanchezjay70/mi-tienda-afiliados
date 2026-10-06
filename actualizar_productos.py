import json
from datetime import datetime

# ==============================================================================
# 1. TU CÓDIGO DE AFILIADO DE AMAZON
# ==============================================================================
# Reemplaza 'tu-codigo-21' con tu ID/Tag de Afiliado real de Amazon
MI_TAG_AFILIADO = "tu-codigo-21"


# ==============================================================================
# 2. LISTA DE TUS ENLACES DE AFILIADO
# ==============================================================================
ENLACES_AMAZON = [
    "https://link.amazon/B069mnmiX", "https://link.amazon/B06UkY9Tn", "https://link.amazon/B0j7e7GgZ",
    "https://link.amazon/B0cwHhChT", "https://link.amazon/B0c5C9XLw", "https://link.amazon/B02rKyKwe",
    "https://link.amazon/B0bD6BdAI", "https://link.amazon/B09AAbGtn", "https://link.amazon/B03sfDqSr",
    "https://link.amazon/B0aAEURgi", "https://link.amazon/B00SjweNb", "https://link.amazon/B04FiMXrH",
    "https://link.amazon/B02nq1zsx", "https://link.amazon/B04Y4VWWD", "https://link.amazon/B0ix1Skjc",
    "https://link.amazon/B00DXYAkp", "https://link.amazon/B00QKWEDw", "https://link.amazon/B01fpnlw4",
    "https://link.amazon/B0appfW92", "https://link.amazon/B08Qoyyid", "https://link.amazon/B05JqgofS",
    "https://link.amazon/B01TiNaKq", "https://link.amazon/B0hzJawMW", "https://link.amazon/B0cwYqSL3",
    "https://link.amazon/B0e0UywZ9", "https://link.amazon/B04YNijKa", "https://link.amazon/B03JC4NL5",
    "https://link.amazon/B0hwjP3KF", "https://link.amazon/B0e4teK0D", "https://link.amazon/B0gq8fhD4",
    "https://link.amazon/B04xICsAV", "https://link.amazon/B0hur1vRe"
]


def procesar_productos():
    catalogo = []
    
    for idx, url in enumerate(ENLACES_AMAZON):
        # Aseguramos que la URL contenga tu tag de afiliado si no lo tiene
        url_final = url
        if "?tag=" not in url and "&tag=" not in url:
            separador = "&" if "?" in url else "?"
            url_final = f"{url}{separador}tag={MI_TAG_AFILIADO}"

        producto = {
            "id": f"PROD-{idx+1}",
            "nombre": f"Producto Seleccionado Oferta #{idx+1}",
            "precio": round(29.99 + (idx * 3.5), 2),  # Precios ilustrativos variados
            "imagen": "https://m.media-amazon.com/images/I/71wF7YDIQkL._AC_SX679_.jpg",
            "link_afiliado": url_final,
            "caracteristica": "Producto destacado con envío rápido y garantía de devolución."
        }
        catalogo.append(producto)
        
    return catalogo


def main():
    print(f"[{datetime.now()}] Generando catálogo moderno para {len(ENLACES_AMAZON)} productos...")
    
    catalogo = procesar_productos()
    
    # Guardamos en el archivo productos.json
    with open('productos.json', 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=4)
        
    print("¡Éxito! 'productos.json' ha sido actualizado correctamente.")


if __name__ == "__main__":
    main()