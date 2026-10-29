# ==============================================================================
# ZUBBIT GAMING STORE - INTEGRACIÓN SHOPIFY ADMIN REST API
# Archivo: api_shopify/conexion_shopify.py
# ==============================================================================

import requests

# ------------------------------------------------------------------------------
# 1. CREDENCIALES OFICIALES Y CONFIGURACIÓN
# ------------------------------------------------------------------------------
SHOP_DOMAIN = "zubbit.myshopify.com"
API_VERSION = "2026-10"

CLIENT_ID = "bfdd27bb5e12a4efb950fc7e579754a6"
CLIENT_SECRET = "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"

# ------------------------------------------------------------------------------
# 2. DICCIONARIO DE MAPEO Y LIMPIEZA DE NOMBRES
# ------------------------------------------------------------------------------
# Nombres comerciales exactos para la terminal
NOMBRES_COMERCIALES = [
    "Mouse Razer Viper V4 Pro",
    "Mousepad Gamer Artisan",
    "Audífonos HyperX Cloud III"
]

# Patrones de coincidencia para filtrar títulos extensos de Shopify
PATRONES_BUSQUEDA = {
    "Mouse Razer Viper V4 Pro": ["razer", "viper"],
    "Mousepad Gamer Artisan": ["artisan"],
    "Audífonos HyperX Cloud III": ["cloud", "hyperx"]
}


def mapear_nombre_comercial(titulo_shopify):
    """
    Normaliza cualquier título extenso proveniente de Shopify
    y lo asigna a su nombre comercial limpio oficial.
    """
    t_lower = titulo_shopify.lower()
    for nombre_limpio, palabras_clave in PATRONES_BUSQUEDA.items():
        if all(kw in t_lower for kw in palabras_clave):
            return nombre_limpio
    return None


def autenticar_client_credentials():
    """
    Obtiene el Access Token dinámico a través de OAuth 2.0 Client Credentials.
    """
    token_url = f"https://{SHOP_DOMAIN}/admin/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(token_url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"[!] Error al solicitar token (HTTP {response.status_code}): {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error de conexión en autenticación: {e}")
        return None


def consultar_stock_pack():
    """
    Consulta los productos vía REST Admin API, normaliza los títulos largos
    mediante el diccionario de mapeo y genera la tabla alineada en la terminal.
    """
    access_token = autenticar_client_credentials()
    if not access_token:
        print("[!] No se pudo completar la autenticación frente a Shopify.")
        return

    endpoint_productos = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/products.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    params = {
        "limit": 250,
        "fields": "id,title,variants"
    }

    try:
        response = requests.get(endpoint_productos, headers=headers, params=params, timeout=12)

        if response.status_code != 200:
            print(f"[!] Error al consultar API de productos (HTTP {response.status_code}): {response.text}")
            return

        productos_api = response.json().get("products", [])

        # Consolidación de stock bajo los nombres limpios
        stock_consolidado = {nombre: 0 for nombre in NOMBRES_COMERCIALES}
        encontrados_set = set()

        for prod in productos_api:
            titulo_raw = prod.get("title", "")
            nombre_limpio = mapear_nombre_comercial(titulo_raw)

            if nombre_limpio:
                # Suma de inventario de todas las variantes del producto
                total_prod = sum(v.get("inventory_quantity", 0) for v in prod.get("variants", []))
                stock_consolidado[nombre_limpio] += total_prod
                encontrados_set.add(nombre_limpio)

        # ----------------------------------------------------------------------
        # PRESENTACIÓN EN CONSOLA CON BORDES Y TABULACIÓN MONOSPACIO
        # ----------------------------------------------------------------------
        borde_tabla = "+----+------------------------------------------+-------------------+"
        ancho_tabla = len(borde_tabla)
        linea_doble = "=" * ancho_tabla

        print("\n" + linea_doble)
        print("          ZUBBIT GAMING STORE - AUDITORÍA DE INVENTARIO (SHOPIFY)        ")
        print(linea_doble)
        print(borde_tabla)
        print("| ID | PRODUCTO COMERCIAL (PACK SETUP)          | STOCK EN BODEGA   |")
        print(borde_tabla)

        for i, nombre in enumerate(NOMBRES_COMERCIALES, start=1):
            stock_val = stock_consolidado.get(nombre, 0)
            stock_str = f"{stock_val} unid."
            print(f"| {i:02d} | {nombre:<40} | {stock_str:>17} |")

        print(borde_tabla)
        total_auditados = len(encontrados_set)
        print(f"\n[i] Auditoría de inventario: {total_auditados} de 3 productos del pack disponibles.")
        print(linea_doble + "\n")

    except requests.exceptions.RequestException as e:
        print(f"[!] Error de comunicación con la API de Shopify: {e}")


if __name__ == "__main__":
    consultar_stock_pack()