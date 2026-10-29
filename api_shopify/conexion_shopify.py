# ==============================================================================
# ZUBBIT GAMING STORE - INTEGRACIÓN SHOPIFY ADMIN REST API
# Archivo: api_shopify/conexion_shopify.py
# Actualización de Inventario en Tiempo Real vía POST /inventory_levels/set.json
# ==============================================================================

import os
import requests

# ------------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y CREDENCIALES OFICIALES DE SHOPIFY
# ------------------------------------------------------------------------------
SHOP_DOMAIN = "zubbit.myshopify.com"
API_VERSION = "2026-01"

# Credenciales oficiales de tu Custom App:
CLIENT_ID = "bfdd27bb5e12a4efb950fc7e579754a6"
CLIENT_SECRET = "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"

# Token permanente shpat_ (dejar vacío para auto-autenticación OAuth):
ADMIN_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "").strip()

# ID de ubicación (Bodega/Sucursal en Shopify).
# Si es None, el script lo extraerá automáticamente de los niveles de inventario
# del producto sin requerir el permiso restringido 'read_locations'.
LOCATION_ID = os.getenv("SHOPIFY_LOCATION_ID", None)

# Nombres comerciales estándar para la terminal
NOMBRES_COMERCIALES = [
    "Mouse Razer Viper V4 Pro",
    "Mousepad Gamer Artisan",
    "Audífonos HyperX Cloud III"
]

# Patrones para mapear los títulos de Shopify a nombres comerciales
PATRONES_BUSQUEDA = {
    "Mouse Razer Viper V4 Pro": ["razer", "viper"],
    "Mousepad Gamer Artisan": ["artisan"],
    "Audífonos HyperX Cloud III": ["cloud", "hyperx"]
}


# ==============================================================================
# 2. CLASE PRINCIPAL: ShopifyInventario
# ==============================================================================
class ShopifyInventario:
    """
    Gestiona la comunicación HTTP REST con la Admin API de Shopify:
    - Autenticación dinámica OAuth Client Credentials o Token shpat_ directo.
    - Consulta de stock en vivo (/products.json).
    - Detección automática de Location ID vía /inventory_levels.json.
    - Actualización y reducción real del inventario en la nube (/inventory_levels/set.json).
    """

    def __init__(self, shop_domain=SHOP_DOMAIN, access_token=ADMIN_ACCESS_TOKEN, 
                 location_id=LOCATION_ID, api_version=API_VERSION):
        self.shop_domain = shop_domain
        self.api_version = api_version
        self.access_token = access_token
        self.location_id = location_id
        self.base_url = f"https://{self.shop_domain}/admin/api/{self.api_version}"

        # Mapeo interno de metadata: {nombre_comercial: {"inventory_item_id": 12345, ...}}
        self._metadata_productos = {}
        # Stock actual en memoria: {nombre_comercial: cantidad_entera}
        self._stock_actual = {}

        # Inicialización y validación del token de acceso
        self._inicializar_token()

    # --------------------------------------------------------------------------
    # GESTIÓN DE AUTENTICACIÓN DINÁMICA
    # --------------------------------------------------------------------------
    def _inicializar_token(self):
        """Determina y obtiene el token de acceso válido mediante OAuth o shpat_."""
        if self.access_token and self.access_token.startswith("shpat_") and not self.access_token.startswith("shpat_52d3ea"):
            return True

        token_oauth = self._autenticar_client_credentials()
        if token_oauth:
            self.access_token = token_oauth
            return True
        else:
            print("[!] No se pudo obtener el token de acceso. Revisa las credenciales.")
            return False

    def _autenticar_client_credentials(self):
        """
        Ejecuta el flujo OAuth 2.0 Client Credentials Grant para obtener
        un Access Token válido usando CLIENT_ID y CLIENT_SECRET (shpss_).
        """
        token_url = f"https://{self.shop_domain}/admin/oauth/access_token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print("[*] Autenticando con Shopify (OAuth Client Credentials Grant)...")
        try:
            res = requests.post(token_url, json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                token = data.get("access_token")
                print(f"[+] ¡Autenticación exitosa! Token obtenido: {token[:12]}...")
                return token
            else:
                print(f"[!] Error al solicitar Access Token a Shopify (HTTP {res.status_code}):")
                print(f"    Detalle: {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"[!] Error de red al autenticar en Shopify: {e}")

        return None

    def _headers(self):
        """Genera las cabeceras HTTP oficiales de autenticación para Shopify."""
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    # --------------------------------------------------------------------------
    # MAPEO DE NOMBRES
    # --------------------------------------------------------------------------
    @staticmethod
    def normalizar_nombre(titulo_raw):
        """Convierte cualquier título largo de Shopify al nombre comercial del pack."""
        t_lower = titulo_raw.lower()
        for nombre_limpio, palabras_clave in PATRONES_BUSQUEDA.items():
            if all(kw in t_lower for kw in palabras_clave):
                return nombre_limpio
        return None

    # --------------------------------------------------------------------------
    # CONSULTA DE STOCK Y METADATA (GET /products.json)
    # --------------------------------------------------------------------------
    def consultar_stock(self, producto=None):
        """
        Petición GET a Shopify para consultar el stock real y registrar
        el INVENTORY_ITEM_ID de cada periférico del pack.
        """
        if not self.access_token:
            if not self._inicializar_token():
                return None if producto else {}

        endpoint = f"{self.base_url}/products.json"
        params = {"limit": 250, "fields": "id,title,variants"}

        try:
            response = requests.get(endpoint, headers=self._headers(), params=params, timeout=12)

            if response.status_code == 200:
                productos_data = response.json().get("products", [])
                nuevo_stock = {nombre: 0 for nombre in NOMBRES_COMERCIALES}

                for p in productos_data:
                    nombre_limpio = self.normalizar_nombre(p.get("title", ""))
                    if nombre_limpio:
                        variantes = p.get("variants", [])
                        total_stock = sum(v.get("inventory_quantity", 0) for v in variantes)
                        nuevo_stock[nombre_limpio] += total_stock

                        # Guardamos el inventory_item_id de la variante principal
                        if variantes:
                            self._metadata_productos[nombre_limpio] = {
                                "product_id": p.get("id"),
                                "variant_id": variantes[0].get("id"),
                                "inventory_item_id": variantes[0].get("inventory_item_id")
                            }

                self._stock_actual = nuevo_stock
                if producto:
                    return self._stock_actual.get(producto, 0)
                return self._stock_actual.copy()

            elif response.status_code == 401:
                print("[!] ERROR 401: No autorizado. El token de acceso fue rechazado.")
            elif response.status_code == 403:
                print("[!] ERROR 403: Permisos insuficientes. Asegúrate de tener el scope 'read_products'.")
            else:
                print(f"[!] Error al consultar inventario (HTTP {response.status_code}): {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Error de conexión al consultar stock en Shopify: {e}")

        if producto:
            return self._stock_actual.get(producto, 0)
        return self._stock_actual.copy()

    # --------------------------------------------------------------------------
    # DETECCIÓN DE UBICACIÓN INTELIGENTE (Sin requerir 'read_locations')
    # --------------------------------------------------------------------------
    def obtener_location_id(self):
        """
        Obtiene el ID de ubicación de la bodega en Shopify:
        1. Si LOCATION_ID está configurado manualmente, lo usa.
        2. Consulta /inventory_levels.json usando el inventory_item_id ya obtenido
           (Este endpoint NO requiere el permiso 'read_locations').
        3. Intenta /locations.json como respaldo.
        """
        if self.location_id:
            return self.location_id

        # Aseguramos tener los inventory_item_ids consultando el stock
        if not self._metadata_productos:
            self.consultar_stock()

        # Método A: Extraer location_id directamente desde inventory_levels
        for prod_nombre, meta in self._metadata_productos.items():
            item_id = meta.get("inventory_item_id")
            if item_id:
                endpoint_inv = f"{self.base_url}/inventory_levels.json?inventory_item_ids={item_id}"
                try:
                    res = requests.get(endpoint_inv, headers=self._headers(), timeout=12)
                    if res.status_code == 200:
                        levels = res.json().get("inventory_levels", [])
                        if levels:
                            self.location_id = levels[0].get("location_id")
                            print(f"[i] Location ID detectado automáticamente vía inventory_levels: {self.location_id}")
                            return self.location_id
                except requests.exceptions.RequestException:
                    pass

        # Método B: Consulta directa a /locations.json (por si tuviera el scope)
        endpoint_loc = f"{self.base_url}/locations.json"
        try:
            res = requests.get(endpoint_loc, headers=self._headers(), timeout=12)
            if res.status_code == 200:
                locations = res.json().get("locations", [])
                for loc in locations:
                    if loc.get("active", True):
                        self.location_id = loc.get("id")
                        print(f"[i] Location ID detectado vía locations.json: {self.location_id}")
                        return self.location_id
                if locations:
                    self.location_id = locations[0].get("id")
                    return self.location_id
        except requests.exceptions.RequestException:
            pass

        return None

    # --------------------------------------------------------------------------
    # ACTUALIZACIÓN REAL DE STOCK (POST /inventory_levels/set.json)
    # --------------------------------------------------------------------------
    def actualizar_stock_real(self, producto, nueva_cantidad):
        """
        Ejecuta una petición POST REAL a Shopify (/inventory_levels/set.json)
        para establecer el nuevo nivel de inventario exacto en la base de datos.
        """
        if producto not in self._metadata_productos:
            self.consultar_stock()

        meta = self._metadata_productos.get(producto)
        if not meta or not meta.get("inventory_item_id"):
            print(f"[!] Error: No se encontró 'inventory_item_id' para '{producto}'.")
            return False

        inventory_item_id = meta.get("inventory_item_id")
        loc_id = self.obtener_location_id()

        if not loc_id:
            print("[!] Error: No se pudo determinar el LOCATION_ID de la tienda.")
            return False

        endpoint_set = f"{self.base_url}/inventory_levels/set.json"
        payload = {
            "location_id": int(loc_id),
            "inventory_item_id": int(inventory_item_id),
            "available": int(nueva_cantidad)
        }

        print(f"[*] Enviando POST a {endpoint_set}...")
        print(f"    - Producto          : {producto}")
        print(f"    - Location ID       : {loc_id}")
        print(f"    - Inventory Item ID : {inventory_item_id}")
        print(f"    - Nueva Cantidad    : {nueva_cantidad} unid.")

        try:
            response = requests.post(endpoint_set, json=payload, headers=self._headers(), timeout=12)

            if response.status_code == 200:
                print(f"[+] HTTP 200 OK: ¡Stock de '{producto}' actualizado con éxito en Shopify a {nueva_cantidad} unidades!\n")
                self._stock_actual[producto] = nueva_cantidad
                return True
            elif response.status_code == 403:
                print(f"[!] ERROR 403: Permisos insuficientes para escribir inventario.")
                print("    Asegúrate de haber activado el scope 'write_inventory' en tu Custom App de Shopify.")
            elif response.status_code == 422:
                print(f"[!] ERROR 422 (Unprocessable Entity): Shopify rechazó los parámetros ({response.text}).")
            else:
                print(f"[!] ERROR HTTP {response.status_code} al actualizar stock: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Error de red al ejecutar petición POST a Shopify: {e}")

        return False

    # --------------------------------------------------------------------------
    # REDUCCIÓN DE STOCK POR VENTA (BUNDLE / CARRITO)
    # --------------------------------------------------------------------------
    def reducir_stock_bundle(self, cantidades_compradas, simular=False):
        """
        Calcula la nueva cantidad tras la compra del bundle y ejecuta la
        actualización real en Shopify para cada periférico.
        - cantidades_compradas: dict ej: {"Mouse Razer Viper V4 Pro": 1, ...}
        - simular: si es False, ejecuta la petición HTTP real a Shopify.
        """
        if not self._stock_actual:
            self.consultar_stock()

        todos_exitosos = True

        for producto, cant_comprada in cantidades_compradas.items():
            if cant_comprada <= 0:
                continue

            stock_previo = self._stock_actual.get(producto, 0)
            nueva_cantidad = max(0, stock_previo - cant_comprada)

            if simular:
                print(f"[SIMULACIÓN] '{producto}': {stock_previo} -> {nueva_cantidad} unid.")
                self._stock_actual[producto] = nueva_cantidad
            else:
                print(f"\n--- Actualizando en la nube: {producto} ---")
                exito = self.actualizar_stock_real(producto, nueva_cantidad)
                if not exito:
                    todos_exitosos = False

        return todos_exitosos


# ==============================================================================
# PRUEBA DIRECTA DEL SCRIPT
# ==============================================================================
if __name__ == "__main__":
    print("=" * 75)
    print("       PRUEBA DE CONEXIÓN Y ACTUALIZACIÓN REAL EN SHOPIFY ADMIN API     ")
    print("=" * 75)
    
    inventario = ShopifyInventario()

    # 1. Consultar stock actual
    print("\n1. Consultando stock actual en Shopify...")
    stock = inventario.consultar_stock()
    print("Stock recuperado:", stock)

    # 2. Obtener Location ID de forma inteligente
    print("\n2. Detectando Location ID...")
    loc = inventario.obtener_location_id()

    # 3. Prueba de reducción real en la nube (simular=False)
    if loc:
        print("\n3. Ejecutando actualización HTTP real tras venta de prueba...")
        inventario.reducir_stock_bundle({
            "Mouse Razer Viper V4 Pro": 1
        }, simular=False)
    else:
        print("\n[!] No se pudo proceder con la actualización porque falta el Location ID.")

    print("=" * 75)
    print("                         FIN DE LA PRUEBA                                ")
    print("=" * 75)