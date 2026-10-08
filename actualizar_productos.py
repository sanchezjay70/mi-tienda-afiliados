import json
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
MI_TAG_AFILIADO = "todoloencue00-20"

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

ARCHIVO = "productos.json"
IMAGEN_DEFECTO = "https://m.media-amazon.com/images/I/71wF7YDIQkL._AC_SX679_.jpg"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}
COOKIES = {'lc-main': 'en_US', 'i18n-prefs': 'USD'}

session = requests.Session()
session.headers.update(HEADERS)
session.cookies.update(COOKIES)


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def cargar_previos():
    """Carga el catálogo anterior para conservar el último precio bueno."""
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, encoding='utf-8') as f:
                return {p['id']: p for p in json.load(f)}
        except Exception:
            pass
    return {}


def a_float(texto):
    """Convierte '$1,299.99' o 'US$29.99' en 1299.99 (formato EE.UU.)."""
    if not texto:
        return None
    m = re.search(r'\d[\d,]*\.?\d*', texto)
    if not m:
        return None
    try:
        return float(m.group(0).replace(',', ''))
    except ValueError:
        return None


def extraer_precio(soup):
    """Busca SOLO en los bloques del precio principal. Nunca 'el primer precio de la página'."""
    selectores = [
        '#corePriceDisplay_desktop_feature_div .priceToPay',
        '#corePrice_feature_div .priceToPay',
        '#corePrice_desktop .priceToPay',
        '#apex_desktop .priceToPay',
        '#corePriceDisplay_desktop_feature_div',
        '#corePrice_feature_div',
        '#apex_desktop',
        '#buybox .a-price',
    ]
    for sel in selectores:
        bloque = soup.select_one(sel)
        if not bloque:
            continue

        # Opción A: precio completo en a-offscreen dentro de .a-price
        precio_el = bloque.select_one('.a-price:not(.a-text-price) .a-offscreen')
        if precio_el:
            p = a_float(precio_el.get_text())
            if p:
                return p

        # Opción B: whole + fraction
        whole = bloque.select_one('.a-price-whole')
        if whole:
            fraction = bloque.select_one('.a-price-fraction')
            entero = re.sub(r'\D', '', whole.get_text())
            decimales = re.sub(r'\D', '', fraction.get_text()) if fraction else '00'
            if entero:
                return float(f"{entero}.{decimales or '00'}")
    return None


def es_captcha(html):
    h = html.lower()
    return ('captcha' in h and 'validatecaptcha' in h) or 'api-services-support@amazon.com' in h


def resolver_asin(url):
    """Sigue la redirección del link corto y devuelve (ASIN, url_final)."""
    r = session.get(url, timeout=15, allow_redirects=True)
    m = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', r.url)
    return (m.group(1) if m else None), r.url


# ==============================================================================
# EXTRACCIÓN POR PRODUCTO
# ==============================================================================
def obtener_datos_amazon(url, index, previo):
    id_prod = f"PROD-{index+1}"
    asin = None
    try:
        asin, _ = resolver_asin(url)
    except Exception as e:
        print(f"⚠️ [{index+1}] No se pudo resolver el enlace: {e}")

    if asin:
        url_consulta = f"https://www.amazon.com/dp/{asin}?th=1&psc=1&tag={MI_TAG_AFILIADO}"
        link_afiliado = url_consulta
    else:
        url_consulta = url
        link_afiliado = url

    for intento in range(3):
        try:
            r = session.get(url_consulta, timeout=15)
            if r.status_code != 200 or es_captcha(r.text):
                print(f"⏳ [{index+1}] Bloqueo/CAPTCHA (intento {intento+1}), reintentando...")
                time.sleep(5 + intento * 5)
                continue

            soup = BeautifulSoup(r.content, 'html.parser')
            titulo = soup.find(id='productTitle')
            nombre = titulo.get_text().strip() if titulo else (previo or {}).get('nombre', f"Producto #{index+1}")

            img = soup.find(id='landingImage') or soup.find(id='imgBlkFront')
            if img:
                imagen = img.get('data-old-hires') or img.get('src') or IMAGEN_DEFECTO
            else:
                imagen = (previo or {}).get('imagen', IMAGEN_DEFECTO)

            precio = extraer_precio(soup)
            if precio:
                print(f"✅ [{index+1}/{len(ENLACES_AMAZON)}] {nombre[:35]}... | ${precio:.2f}")
                return {
                    "id": id_prod,
                    "asin": asin,
                    "nombre": nombre,
                    "precio": precio,
                    "imagen": imagen,
                    "link_afiliado": link_afiliado,
                    "caracteristica": "Producto seleccionado con envío rápido y garantía Amazon.",
                    "precio_verificado": True,
                    "actualizado": datetime.now().isoformat(timespec='minutes'),
                }

            print(f"⚠️ [{index+1}] Sin precio de compra en la página (¿sin stock o no envía a la zona?).")
            break
        except Exception as e:
            print(f"⚠️ [{index+1}] Error: {e}")
            time.sleep(3)

    # FALLÓ: conservamos el último precio bueno, sin inventar nada
    if previo:
        previo = dict(previo)
        previo["precio_verificado"] = False
        previo["link_afiliado"] = link_afiliado
        print(f"↩️  [{index+1}] Se conserva el último precio guardado: ${previo.get('precio')}")
        return previo

    return {
        "id": id_prod, "asin": asin, "nombre": f"Producto #{index+1}", "precio": None,
        "imagen": IMAGEN_DEFECTO, "link_afiliado": link_afiliado,
        "caracteristica": "Consulta el precio actualizado en Amazon.",
        "precio_verificado": False,
    }


# ==============================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================
def main():
    # Verificar que Python sale por EE.UU. (VPN de escritorio activa)
    try:
        info = requests.get("https://ipinfo.io/json", timeout=10).json()
        pais = info.get("country")
        print(f"🌐 Python sale desde: {pais} ({info.get('city')}) - IP {info.get('ip')}")
        if pais != "US":
            print("❌ Python NO está usando la VPN de EE.UU. Actívala y vuelve a correr el script.")
            return
    except Exception:
        print("⚠️ No pude verificar tu país, continúo igual.")

    print(f"[{datetime.now()}] Iniciando extracción con tag: {MI_TAG_AFILIADO}")
    previos = cargar_previos()
    catalogo = []

    # Calentar sesión: visitar la home como lo haría una persona
    try:
        session.get("https://www.amazon.com/", timeout=15)
        time.sleep(random.uniform(3, 6))
    except Exception:
        pass

    # Primera pasada
    for idx, url in enumerate(ENLACES_AMAZON):
        datos = obtener_datos_amazon(url, idx, previos.get(f"PROD-{idx+1}"))
        catalogo.append(datos)
        time.sleep(random.uniform(4, 8))

    # Segunda pasada solo para los que fallaron
    fallidos = [i for i, p in enumerate(catalogo) if not p.get("precio_verificado")]
    if fallidos:
        print(f"\n🔁 Reintentando {len(fallidos)} producto(s) fallido(s) tras una pausa de 30 s...")
        time.sleep(30)
        for i in fallidos:
            datos = obtener_datos_amazon(ENLACES_AMAZON[i], i, previos.get(f"PROD-{i+1}"))
            catalogo[i] = datos
            time.sleep(random.uniform(8, 14))

    with open(ARCHIVO, 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=4)

    ok = sum(1 for p in catalogo if p.get("precio_verificado"))
    print(f"\n🎉 Listo: {ok}/{len(catalogo)} precios verificados.")
    pendientes = [p["id"] for p in catalogo if not p.get("precio_verificado")]
    if pendientes:
        print(f"⏳ Pendientes (vuelve a correr en 10-15 min o cambia de servidor VPN): {', '.join(pendientes)}")


if __name__ == "__main__":
    main()