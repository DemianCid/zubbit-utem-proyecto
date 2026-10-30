# ==============================================================================
# PROYECTO: ZUBBIT GAMING STORE (UTEM)
# Módulo: Paradigmas de Programación - Programación Funcional
# Archivo: Paradigmas/carrito_funcional.py
# Conceptos: Funciones Puras, Inmutabilidad, Funciones de Orden Superior (HOF),
#            map, filter, reduce, Composición (pipe), Integración Shopify Admin API
#            y Menú Interactivo Funcional basado en Transición de Estados
# ==============================================================================

"""
GUÍA TEÓRICA Y CONCEPTUAL: PARADIGMA FUNCIONAL EN PYTHON

1. ¿QUÉ ES UNA FUNCIÓN PURA?
   - Determinismo: Retorna siempre el mismo resultado para los mismos parámetros.
   - Sin Efectos Secundarios (No Side Effects): No modifica el estado externo ni
     muta los objetos recibidos como entrada. Toda la información entra por los
     parámetros y sale por el valor de retorno.

2. ¿POR QUÉ IMPORTA LA INMUTABILIDAD?
   - Elimina la mutabilidad compartida (Shared Mutable State), previniendo errores
     de concurrencia y efectos secundarios inesperados.
   - Otorga Transparencia Referencial: Cualquier llamada a una función puede
     reemplazarse por su valor resultante sin alterar el funcionamiento del sistema.

3. FUNCIONES DE ORDEN SUPERIOR (HIGHER-ORDER FUNCTIONS - HOF):
   Funciones que reciben otras funciones como argumentos o retornan una nueva función:
   - map(f, coleccion): Transforma cada elemento aplicando 'f'.
   - filter(predicado, coleccion): Conserva los elementos que cumplen la condición booleana.
   - reduce(acumulador, coleccion, inicial): Pliega (fold) la colección a un único valor.

4. ARQUITECTURA FUNCIONAL INTERACTIVA:
   En lugar de usar objetos con estado mutable o variables globales, la aplicación
   se modela como una Máquina de Estados Inmutable:
   - 'EstadoSistema': Estructura de datos inmutable que almacena (catalogo, carrito, api).
   - 'Despachador de Acciones': Diccionario de funciones puras donde cada opción
     del menú es una función con firma: (EstadoSistema) -> EstadoSistema.
   - 'Núcleo Funcional, Capa Externa Imperativa': Los cálculos, validaciones y
     descuentos son 100% funcionales y puros; la entrada/salida y llamadas HTTP
     a la nube de Shopify se aíslan en la frontera de ejecución.
"""

import os
import sys
from typing import NamedTuple, Tuple, Optional, Callable, Any, Dict
from functools import reduce

# ------------------------------------------------------------------------------
# Configuración del entorno de importaciones (Soporte desde raíz o subcarpeta)
# ------------------------------------------------------------------------------
DIRECTORIO_PADRE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if DIRECTORIO_PADRE not in sys.path:
    sys.path.insert(0, DIRECTORIO_PADRE)

try:
    from api_shopify.conexion_shopify import ShopifyInventario
except ImportError as error:
    print(f"[!] Error al importar conexion_shopify: {error}")
    # Definición de respaldo en caso de prueba aislada sin el módulo
    class ShopifyInventario:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def consultar_stock(self): return {}
        def reducir_stock_bundle(self, cantidades, simular=False): return True


# ==============================================================================
# 1. ESTRUCTURAS DE DATOS INMUTABLES (NamedTuples)
# ==============================================================================

class Producto(NamedTuple):
    """
    Registro inmutable de un periférico gaming.
    Garantiza que ningún atributo pueda modificarse tras su creación.
    """
    id: int
    nombre: str
    precio: int
    stock: int
    categoria: str
    specs: str
    id_shopify: Optional[str] = None


class ItemCarrito(NamedTuple):
    """
    Representa una línea inmutable de compra: asocia un Producto con su cantidad.
    """
    producto: Producto
    cantidad: int


class DetalleCheckout(NamedTuple):
    """
    Estructura inmutable que encapsula el resultado financiero del checkout.
    """
    subtotal_bruto: int
    packs_bundle: int
    descuento_bundle: int
    total_neto: int
    cantidad_items: int
    unidades_totales: int


# Alias de tipo funcional: Una tupla inmutable de Items de Carrito
CarritoInmutable = Tuple[ItemCarrito, ...]


class EstadoSistema(NamedTuple):
    """
    Estado global inmutable de la aplicación.
    Cada acción del menú recibe un EstadoSistema y genera un NUEVO EstadoSistema.
    """
    catalogo: Tuple[Producto, ...]
    carrito: CarritoInmutable
    api: ShopifyInventario


# ==============================================================================
# 2. CATÁLOGO BASE INMUTABLE DE ZUBBIT GAMING STORE
# ==============================================================================

CATALOGO_BASE: Tuple[Producto, ...] = (
    Producto(
        id=1,
        nombre="Mouse Razer Viper V4 Pro",
        precio=100000,
        stock=30,
        categoria="Mouse",
        specs="35.000 DPI / 8.000 Hz",
        id_shopify="52960852705345"
    ),
    Producto(
        id=2,
        nombre="Mousepad Gamer Artisan",
        precio=70000,
        stock=20,
        categoria="Mousepad",
        specs="FX Soft / 490x420mm",
        id_shopify="52960794443841"
    ),
    Producto(
        id=3,
        nombre="Audífonos HyperX Cloud III",
        precio=79990,
        stock=34,
        categoria="Audífonos",
        specs="Drivers 53mm / 10Hz-21kHz",
        id_shopify="52960912998465"
    )
)

PORCENTAJE_DESCUENTO_BUNDLE: float = 0.20


# ==============================================================================
# 3. FUNCIONES PURAS DE OPERACIÓN DEL ESTADO (Sin efectos colaterales)
# ==============================================================================

def crear_carrito_vacio() -> CarritoInmutable:
    """Función pura que retorna una tupla vacía representando el carrito inicial."""
    return ()


def buscar_item_por_id(carrito: CarritoInmutable, id_producto: int) -> Optional[ItemCarrito]:
    """
    Función pura que busca un ítem en el carrito utilizando 'filter' funcional.
    """
    coincidencias = tuple(filter(lambda item: item.producto.id == id_producto, carrito))
    return coincidencias[0] if coincidencias else None


def buscar_producto_catalogo(catalogo: Tuple[Producto, ...], id_producto: int) -> Optional[Producto]:
    """
    Función pura que localiza un producto en el catálogo por su ID numérico.
    """
    coincidencias = tuple(filter(lambda p: p.id == id_producto, catalogo))
    return coincidencias[0] if coincidencias else None


def agregar_producto(carrito: CarritoInmutable, producto: Producto, cantidad: int = 1) -> CarritoInmutable:
    """
    FUNCIÓN PURA: Agrega un producto retornando una NUEVA tupla inmutable.
    El carrito recibido como argumento jamás se muta.
    """
    if cantidad <= 0:
        return carrito

    item_existente = buscar_item_por_id(carrito, producto.id)
    cantidad_actual = item_existente.cantidad if item_existente else 0
    cantidad_total = cantidad_actual + cantidad

    # Validación de stock físico disponible
    if cantidad_total > producto.stock:
        print(f"\n[!] Stock insuficiente para '{producto.nombre}'.")
        print(f"    Disponible en bodega: {producto.stock} | Solicitado: {cantidad_total}")
        return carrito

    if item_existente:
        # Reconstrucción inmutable: genera un nuevo ItemCarrito reemplazándolo
        nuevo_item = ItemCarrito(producto=producto, cantidad=cantidad_total)
        return tuple(
            nuevo_item if item.producto.id == producto.id else item
            for item in carrito
        )
    else:
        # Concatenación pura de tuplas
        nuevo_item = ItemCarrito(producto=producto, cantidad=cantidad)
        return carrito + (nuevo_item,)


def eliminar_producto(carrito: CarritoInmutable, id_producto: int, cantidad: Optional[int] = None) -> CarritoInmutable:
    """
    FUNCIÓN PURA: Reduce la cantidad o remueve un ítem retornando una NUEVA tupla.
    """
    item_existente = buscar_item_por_id(carrito, id_producto)
    if not item_existente:
        print("[!] El producto no se encuentra en el carrito.")
        return carrito

    if cantidad is None or cantidad >= item_existente.cantidad:
        # 'filter' funcional para excluir el producto del nuevo carrito
        return tuple(filter(lambda item: item.producto.id != id_producto, carrito))
    else:
        nueva_cantidad = item_existente.cantidad - cantidad
        nuevo_item = ItemCarrito(producto=item_existente.producto, cantidad=nueva_cantidad)
        return tuple(
            nuevo_item if item.producto.id == id_producto else item
            for item in carrito
        )


# ==============================================================================
# 4. FUNCIONES DE ORDEN SUPERIOR (HOF), PREDICADOS Y COMPOSICIÓN
# ==============================================================================

def crear_filtro_por_categoria(categoria: str) -> Callable[[ItemCarrito], bool]:
    """
    FUNCIÓN DE ORDEN SUPERIOR (Closure / Currying):
    Recibe una categoría y retorna una nueva función predicado pura.
    """
    cat_normalizada = categoria.strip().lower()
    return lambda item: item.producto.categoria.strip().lower() == cat_normalizada


def crear_filtro_precio_minimo(precio_min: int) -> Callable[[Producto], bool]:
    """
    FUNCIÓN DE ORDEN SUPERIOR:
    Retorna un predicado para filtrar productos con precio mayor o igual a 'precio_min'.
    """
    return lambda prod: prod.precio >= precio_min


def pipe(valor_inicial: Any, *funciones: Callable[[Any], Any]) -> Any:
    """
    FUNCIÓN DE ORDEN SUPERIOR (Pipeline / Composición Funcional):
    Aplica una secuencia de transformaciones de izquierda a derecha usando 'reduce'.
    """
    return reduce(lambda acumulado, funcion: funcion(acumulado), funciones, valor_inicial)


# ==============================================================================
# 5. TRANSFORMACIONES CON MAP, FILTER Y REDUCE
# ==============================================================================

def calcular_subtotal_linea(item: ItemCarrito) -> int:
    """Función pura que calcula el subtotal de una línea de compra."""
    return item.producto.precio * item.cantidad


def mapear_subtotales(carrito: CarritoInmutable) -> Tuple[int, ...]:
    """USO DE MAP: Transforma cada ItemCarrito en su subtotal en pesos chilenos."""
    return tuple(map(calcular_subtotal_linea, carrito))


def mapear_nombres_catalogo(productos: Tuple[Producto, ...]) -> Tuple[str, ...]:
    """USO DE MAP: Extrae exclusivamente los nombres de los productos."""
    return tuple(map(lambda p: p.nombre, productos))


def filtrar_items_por_categoria(carrito: CarritoInmutable, categoria: str) -> Tuple[ItemCarrito, ...]:
    """USO DE FILTER: Filtra ítems usando predicados generados por orden superior."""
    predicado = crear_filtro_por_categoria(categoria)
    return tuple(filter(predicado, carrito))


def filtrar_catalogo_gama_alta(productos: Tuple[Producto, ...], precio_corte: int = 75000) -> Tuple[Producto, ...]:
    """USO DE FILTER: Filtra productos de gama alta."""
    return tuple(filter(crear_filtro_precio_minimo(precio_corte), productos))


def calcular_subtotal_bruto(carrito: CarritoInmutable) -> int:
    """
    USO DE REDUCE: Suma el total bruto del carrito iterando funcionalmente.
    Equivale al foldl funcional con acumulador inicial 0.
    """
    return reduce(
        lambda acumulador, item: acumulador + (item.producto.precio * item.cantidad),
        carrito,
        0
    )


def contar_total_unidades(carrito: CarritoInmutable) -> int:
    """USO DE REDUCE: Acumula el conteo total de piezas físicas."""
    return reduce(lambda acc, item: acc + item.cantidad, carrito, 0)


def obtener_producto_tope_gama(productos: Tuple[Producto, ...]) -> Optional[Producto]:
    """USO DE REDUCE: Determina el periférico con el precio más alto."""
    if not productos:
        return None
    return reduce(
        lambda p_max, p_actual: p_actual if p_actual.precio > p_max.precio else p_max,
        productos
    )


# ==============================================================================
# 6. REGLA DE NEGOCIO: BUNDLE COMPETITIVO (-20% OFF)
# ==============================================================================

def contar_unidades_categoria(carrito: CarritoInmutable, categoria: str) -> int:
    """COMBINACIÓN FUNCIONAL (filter + reduce) para totalizar piezas de una categoría."""
    items_categoria = filter(crear_filtro_por_categoria(categoria), carrito)
    return reduce(lambda acc, item: acc + item.cantidad, items_categoria, 0)


def evaluar_packs_bundle(carrito: CarritoInmutable) -> int:
    """
    FUNCIÓN PURA: Determina cuántos 'Packs Setup Competitivo' completos se pueden armar.
    Regla: Requiere simultáneamente (1 Mouse + 1 Mousepad + 1 Audífonos).
    """
    cant_mouse = contar_unidades_categoria(carrito, "Mouse")
    cant_mousepad = contar_unidades_categoria(carrito, "Mousepad")
    cant_audifonos = contar_unidades_categoria(carrito, "Audífonos")

    return min(cant_mouse, cant_mousepad, cant_audifonos)


def calcular_descuento_bundle(carrito: CarritoInmutable) -> int:
    """
    FUNCIÓN PURA: Aplica el 20% de descuento del 'Bundle Competitivo'.
    - Precio base del setup completo: $100.000 + $70.000 + $79.990 = $249.990
    - Descuento por cada trío completo: $249.990 * 20% = $49.998
    """
    num_packs = evaluar_packs_bundle(carrito)
    if num_packs <= 0:
        return 0

    precio_base_pack = reduce(lambda acc, p: acc + p.precio, CATALOGO_BASE, 0)
    descuento_unitario_pack = int(round(precio_base_pack * PORCENTAJE_DESCUENTO_BUNDLE))

    return num_packs * descuento_unitario_pack


def calcular_total_neto(carrito: CarritoInmutable) -> int:
    """FUNCIÓN PURA: Subtotal Bruto - Descuento del Bundle Competitivo."""
    return calcular_subtotal_bruto(carrito) - calcular_descuento_bundle(carrito)


def procesar_checkout_funcional(carrito: CarritoInmutable) -> DetalleCheckout:
    """
    FUNCIÓN PURA DE CHECKOUT:
    Encapsula en una estructura inmutable 'DetalleCheckout' el balance completo.
    """
    subtotal = calcular_subtotal_bruto(carrito)
    packs = evaluar_packs_bundle(carrito)
    descuento = calcular_descuento_bundle(carrito)
    total_neto = subtotal - descuento
    cantidad_items = len(carrito)
    unidades_totales = contar_total_unidades(carrito)

    return DetalleCheckout(
        subtotal_bruto=subtotal,
        packs_bundle=packs,
        descuento_bundle=descuento,
        total_neto=total_neto,
        cantidad_items=cantidad_items,
        unidades_totales=unidades_totales
    )


# ==============================================================================
# 7. INTEGRACIÓN FUNCIONAL CON SHOPIFY ADMIN REST API
# ==============================================================================

def sincronizar_catalogo_con_shopify(
    catalogo_actual: Tuple[Producto, ...], 
    api: ShopifyInventario
) -> Tuple[Producto, ...]:
    """
    FUNCIÓN DE INTEGRACIÓN FUNCIONAL:
    Consulta el inventario en tiempo real en Shopify y genera una NUEVA tupla
    inmutable de productos con los stocks sincronizados desde la nube.
    """
    print("\n[*] Sincronizando catálogo en tiempo real con Shopify...")
    stock_remoto = api.consultar_stock()

    if not stock_remoto:
        print("[!] No fue posible obtener stock remoto; se conserva el catálogo actual.")
        return catalogo_actual

    # Transformación pura mediante map()
    def sincronizar_producto(prod: Producto) -> Producto:
        stock_nube = stock_remoto.get(prod.nombre, prod.stock)
        return prod._replace(stock=stock_nube)

    catalogo_actualizado = tuple(map(sincronizar_producto, catalogo_actual))
    print("[+] Catálogo sincronizado exitosamente con Shopify.")
    return catalogo_actualizado


def construir_mapa_cantidades_carrito(carrito: CarritoInmutable) -> Dict[str, int]:
    """
    Función pura que transforma la tupla inmutable de Items del carrito
    en el diccionario {nombre_producto: cantidad_total} requerido por la API de Shopify.
    """
    return {item.producto.nombre: item.cantidad for item in carrito}


def ejecutar_descuento_stock_shopify(carrito: CarritoInmutable, api: ShopifyInventario) -> bool:
    """
    EJECUCIÓN DE CHECKOUT EN LA NUBE:
    Envía las peticiones POST a Shopify vía 'reducir_stock_bundle'.
    Aísla los efectos secundarios de red en una frontera clara.
    """
    cantidades = construir_mapa_cantidades_carrito(carrito)
    print("\n" + "=" * 70)
    print("PROCESANDO ACTUALIZACIÓN DE INVENTARIO EN SHOPIFY CLOUD...")
    print("=" * 70)
    
    # Invoca el método oficial de la API de Shopify
    exito = api.reducir_stock_bundle(cantidades, simular=False)
    return exito


# ==============================================================================
# 8. PRESENTACIÓN DECLARATIVA Y FORMATEADORES EN CONSOLA
# ==============================================================================

def formatear_precio_clp(monto: int) -> str:
    """Función pura que formatea enteros a moneda nacional chilena."""
    return f"${monto:,.0f}".replace(",", ".")


def mostrar_catalogo(catalogo: Tuple[Producto, ...]) -> None:
    """Renderiza la tabla formateada del catálogo sincronizado con Shopify."""
    ancho = 86
    borde = "+" + "-" * ancho + "+"
    print("\n" + "=" * (ancho + 2))
    print(f"| {'CATÁLOGO DE PERIFÉRICOS GAMING - ZUBBIT GAMING STORE':^{ancho}} |")
    print("=" * (ancho + 2))
    print(borde)
    print(f"| {'ID':<4} | {'PRODUCTO':<28} | {'CATEGORÍA':<11} | {'ESPECIFICACIONES':<22} | {'PRECIO':<11} | {'STOCK':<5} |")
    print(borde)
    for p in catalogo:
        precio_str = formatear_precio_clp(p.precio)
        print(f"| [{p.id}]  | {p.nombre:<28} | {p.categoria:<11} | {p.specs:<22} | {precio_str:>11} | {p.stock:>5} |")
    print(borde + "\n")


def mostrar_resumen_carrito(carrito: CarritoInmutable, titulo: str = "DETALLE DEL CARRITO") -> None:
    """Renderiza el desglose financiero del carrito con el bundle calculado."""
    ancho = 86
    borde = "+" + "-" * ancho + "+"
    linea_doble = "=" * (ancho + 2)

    detalle = procesar_checkout_funcional(carrito)

    print("\n" + linea_doble)
    print(f"| {titulo:^{ancho}} |")
    print(linea_doble)
    print(borde)
    print(f"| {'CANT.':<6} | {'PRODUCTO':<38} | {'PRECIO UNIT.':<16} | {'SUBTOTAL':<18} |")
    print(borde)

    if not carrito:
        print(f"| {'El carrito se encuentra actualmente vacío.':^{ancho}} |")
    else:
        for item in carrito:
            p_unit = formatear_precio_clp(item.producto.precio)
            subtotal = formatear_precio_clp(calcular_subtotal_linea(item))
            print(f"| {item.cantidad:>5}  | {item.producto.nombre:<38} | {p_unit:>16} | {subtotal:>18} |")

        print(borde)
        sub_bruto = formatear_precio_clp(detalle.subtotal_bruto)
        descuento = formatear_precio_clp(detalle.descuento_bundle)
        total_neto = formatear_precio_clp(detalle.total_neto)

        print(f"| {'SUBTOTAL BRUTO (PRECIOS DE LISTA):':<65} {sub_bruto:>18} |")
        if detalle.packs_bundle > 0:
            texto_pack = f"BUNDLE COMPETITIVO: {detalle.packs_bundle}x Setup Completo (-20% OFF)"
            print(f"| {texto_pack:<65} -{descuento:>17} |")
        else:
            print(f"| {'BUNDLE COMPETITIVO:':<65} {'No califica (Falta trío)':>18} |")

        print(borde)
        print(f"| {'TOTAL NETO A PAGAR:':<65} {total_neto:>18} |")
        print(f"| {'RESUMEN FÍSICO: ' + str(detalle.unidades_totales) + ' piezas en ' + str(detalle.cantidad_items) + ' líneas distintas':<86} |")

    print(linea_doble + "\n")


def mostrar_menu_principal() -> None:
    """Despliega el menú de opciones del sistema funcional."""
    print("----------------------------------------------------------------------------------------")
    print("                    ZUBBIT GAMING PERIFÉRICOS S.A. - UTEM (FUNCIONAL)                   ")
    print("                  EVENTO ESPECIAL: 'PACK SETUP COMPETITIVO' (-20% OFF)                  ")
    print("----------------------------------------------------------------------------------------")
    print("[1] Ver catálogo de periféricos (sincronizado con Shopify)")
    print("[2] Agregar producto al carrito")
    print("[3] Eliminar producto del carrito (o reducir cantidad)")
    print("[4] Ver detalle del carrito (con cálculo de Bundle Competitivo)")
    print("[5] Procesar Checkout y Actualizar Inventario en la nube de Shopify")
    print("[6] Vaciar carrito")
    print("[7] Ejecutar Demostración Educativa (map, filter, reduce, pipe, tests)")
    print("[0] Salir del sistema")
    print("----------------------------------------------------------------------------------------")


# ==============================================================================
# 9. MANEJADORES DE ACCIÓN PURA DEL MENÚ (TRANSICIONES DE ESTADO)
# ==============================================================================

def accion_ver_catalogo(estado: EstadoSistema) -> EstadoSistema:
    """Muestra el catálogo actual. No altera el estado."""
    mostrar_catalogo(estado.catalogo)
    return estado


def accion_agregar_producto(estado: EstadoSistema) -> EstadoSistema:
    """Permite seleccionar un producto y cantidad para agregarlo puramente."""
    mostrar_catalogo(estado.catalogo)
    try:
        id_ingresado = int(input("Ingrese el ID del producto que desea agregar: ").strip())
        producto_encontrado = buscar_producto_catalogo(estado.catalogo, id_ingresado)

        if not producto_encontrado:
            print(f"[!] No existe ningún producto con el ID {id_ingresado}.")
            return estado

        cant_ingresada = int(input(f"Ingrese la cantidad para '{producto_encontrado.nombre}': ").strip())
        if cant_ingresada <= 0:
            print("[!] La cantidad debe ser mayor a 0.")
            return estado

        # Genera el nuevo carrito inmutable mediante la función pura
        nuevo_carrito = agregar_producto(estado.carrito, producto_encontrado, cant_ingresada)

        if len(nuevo_carrito) != len(estado.carrito) or (
            buscar_item_por_id(nuevo_carrito, id_ingresado).cantidad !=  # type: ignore
            (buscar_item_por_id(estado.carrito, id_ingresado).cantidad if buscar_item_por_id(estado.carrito, id_ingresado) else 0)
        ):
            print(f"[+] ¡Éxito! Se agregaron {cant_ingresada}x '{producto_encontrado.nombre}' al carrito.")

        return estado._replace(carrito=nuevo_carrito)

    except ValueError:
        print("[!] Entrada inválida. Debe ingresar valores numéricos enteros.")
        return estado


def accion_eliminar_producto(estado: EstadoSistema) -> EstadoSistema:
    """Permite retirar o reducir un producto retornando un nuevo carrito inmutable."""
    if not estado.carrito:
        print("\n[!] El carrito se encuentra actualmente vacío.")
        return estado

    mostrar_resumen_carrito(estado.carrito, titulo="ESTADO ACTUAL DEL CARRITO")
    try:
        id_ingresado = int(input("Ingrese el ID del producto que desea eliminar: ").strip())
        item_existente = buscar_item_por_id(estado.carrito, id_ingresado)

        if not item_existente:
            print(f"[!] El producto con ID {id_ingresado} no está en el carrito.")
            return estado

        print(f"Cantidad actual en carrito: {item_existente.cantidad} unidades.")
        resp_cant = input("¿Cuántas unidades desea retirar? (Presione Enter para eliminar todo): ").strip()

        if resp_cant == "":
            cant_a_retirar = None
        else:
            cant_a_retirar = int(resp_cant)
            if cant_a_retirar <= 0:
                print("[!] La cantidad debe ser mayor a 0.")
                return estado

        nuevo_carrito = eliminar_producto(estado.carrito, id_ingresado, cant_a_retirar)
        print(f"[+] Operación completada sobre '{item_existente.producto.nombre}'.")
        return estado._replace(carrito=nuevo_carrito)

    except ValueError:
        print("[!] Entrada inválida. Debe ingresar números enteros.")
        return estado


def accion_ver_carrito(estado: EstadoSistema) -> EstadoSistema:
    """Muestra el estado actual del carrito y sus bonificaciones."""
    mostrar_resumen_carrito(estado.carrito, titulo="CARRITO DE COMPRAS - DETALLE FINANCIERO")
    return estado


def accion_checkout(estado: EstadoSistema) -> EstadoSistema:
    """
    PROCESO DE CHECKOUT FUNCIONAL CON CONEXIÓN REAL A SHOPIFY:
    1. Valida existencia de ítems.
    2. Computa descuentos mediante la regla del Bundle Competitivo.
    3. Solicita confirmación expresa para actualizar la bodega de Shopify.
    4. Ejecuta las peticiones POST vía 'ejecutar_descuento_stock_shopify'.
    5. Retorna el nuevo estado con catálogo sincronizado y carrito vacío.
    """
    if not estado.carrito:
        print("\n[!] No hay productos en el carrito para procesar el checkout.")
        return estado

    mostrar_resumen_carrito(estado.carrito, titulo="RESUMEN PREVIO AL CHECKOUT")
    detalle = procesar_checkout_funcional(estado.carrito)

    print("========================================================================================")
    print(f" TOTAL NETO A PAGAR: {formatear_precio_clp(detalle.total_neto)}")
    if detalle.packs_bundle > 0:
        print(f" ¡Ahorro aplicado por Bundle Competitivo: {formatear_precio_clp(detalle.descuento_bundle)} (-20%)!")
    print("========================================================================================")

    confirmacion = input("\n¿Desea autorizar la transacción y descontar stock real en Shopify? [S/N]: ").strip().upper()
    if confirmacion != "S":
        print("[*] Transacción cancelada por el usuario. El carrito permanece intacto.")
        return estado

    # Ejecuta la sincronización en la nube con Shopify
    exito_api = ejecutar_descuento_stock_shopify(estado.carrito, estado.api)

    if exito_api:
        print("\n" + "*" * 75)
        print("¡TRANSACCIÓN COMPLETADA Y REGISTRADA EN SHOPIFY CON ÉXITO!")
        print("*" * 75)
        # Sincronizamos el catálogo local para reflejar las nuevas existencias de la nube
        catalogo_actualizado = sincronizar_catalogo_con_shopify(estado.catalogo, estado.api)
        # Retornamos el nuevo estado con el carrito vaciado y catálogo actualizado
        return estado._replace(catalogo=catalogo_actualizado, carrito=crear_carrito_vacio())
    else:
        print("\n[!] Hubo un problema al comunicar los cambios con Shopify. Revise las credenciales o conexión.")
        return estado


def accion_vaciar_carrito(estado: EstadoSistema) -> EstadoSistema:
    """Retorna un nuevo estado con el carrito vacío."""
    if not estado.carrito:
        print("\n[i] El carrito ya se encuentra vacío.")
        return estado

    print("\n[+] El carrito de compras ha sido vaciado exitosamente.")
    return estado._replace(carrito=crear_carrito_vacio())


def accion_ejecutar_pruebas(estado: EstadoSistema) -> EstadoSistema:
    """Ejecuta la batería de pruebas y demostraciones pedagógicas funcionales."""
    ejecutar_bateria_pruebas_funcionales(estado.catalogo)
    return estado


def obtener_despachador_acciones() -> Dict[str, Callable[[EstadoSistema], EstadoSistema]]:
    """
    TABLA DE DESPACHO FUNCIONAL (Pattern Matching / Dispatcher):
    Mapea cada opción del menú a su función pura de transición de estado.
    """
    return {
        "1": accion_ver_catalogo,
        "2": accion_agregar_producto,
        "3": accion_eliminar_producto,
        "4": accion_ver_carrito,
        "5": accion_checkout,
        "6": accion_vaciar_carrito,
        "7": accion_ejecutar_pruebas
    }


# ==============================================================================
# 10. BATERÍA DE PRUEBAS EDUCATIVAS AUTOMATIZADAS
# ==============================================================================

def ejecutar_bateria_pruebas_funcionales(catalogo: Tuple[Producto, ...]) -> None:
    """Ejecuta los tests de map, filter, reduce, inmutabilidad y casos del bundle."""
    print("\n" + "=" * 88)
    print("      DEMOSTRACIÓN EDUCATIVA: FUNCIONES DE ORDEN SUPERIOR Y BUNDLE (UTEM)       ")
    print("=" * 88)

    p_mouse = catalogo[0]
    p_mousepad = catalogo[1]
    p_audifonos = catalogo[2]

    # PRUEBA 1: Transformación con MAP
    print("\n[+] PRUEBA 1: MAP()")
    nombres = mapear_nombres_catalogo(catalogo)
    print(f"    - Nombres en catálogo obtenidos con 'map': {nombres}")

    # PRUEBA 2: Filtrado con FILTER y Predicados
    print("\n[+] PRUEBA 2: FILTER() Y PREDICADOS")
    gama_alta = filtrar_catalogo_gama_alta(catalogo, precio_corte=75000)
    for prod in gama_alta:
        print(f"    - Gama Alta (>= $75.000): {prod.nombre} | {formatear_precio_clp(prod.precio)}")

    # PRUEBA 3: Reducción con REDUCE
    print("\n[+] PRUEBA 3: REDUCE()")
    carrito_test = pipe(
        crear_carrito_vacio(),
        lambda c: agregar_producto(c, p_mouse, 2),
        lambda c: agregar_producto(c, p_mousepad, 3),
        lambda c: agregar_producto(c, p_audifonos, 2)
    )
    subtotal_bruto = calcular_subtotal_bruto(carrito_test)
    total_piezas = contar_total_unidades(carrito_test)
    print(f"    - Total unidades físicas con 'reduce': {total_piezas} piezas.")
    print(f"    - Subtotal bruto con 'reduce'        : {formatear_precio_clp(subtotal_bruto)}")

    # PRUEBA 4: Regla del Bundle (-20% OFF)
    print("\n[+] PRUEBA 4: REGLA DE NEGOCIO 'BUNDLE COMPETITIVO'")
    chk = procesar_checkout_funcional(carrito_test)
    print(f"    - Subtotal Bruto       : {formatear_precio_clp(chk.subtotal_bruto)}")
    print(f"    - Packs Armados (Min)  : {chk.packs_bundle} packs completos")
    print(f"    - Descuento (-20%)     : -{formatear_precio_clp(chk.descuento_bundle)}")
    print(f"    - Total Neto a Pagar   : {formatear_precio_clp(chk.total_neto)}")

    assert chk.packs_bundle == 2, f"Fallo en cálculo de packs: {chk.packs_bundle}"
    assert chk.descuento_bundle == 99996, f"Fallo en monto descuento: {chk.descuento_bundle}"
    print("[✓ Verificación Exitosa]: Todas las aserciones funcionales superadas.")
    print("=" * 88 + "\n")


# ==============================================================================
# 11. BUCLE INTERACTIVO FUNCIONAL Y PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

def ciclo_interactivo(estado_inicial: EstadoSistema) -> None:
    """
    CICLO PRINCIPAL (Máquina de Estados Funcional):
    Mantiene la inmutabilidad: cada vuelta del bucle evalúa la entrada del usuario,
    aplica la función de transición de estado correspondiente y entrega el nuevo
    'EstadoSistema' a la siguiente iteración sin mutar el estado anterior.
    """
    estado = estado_inicial
    despachador = obtener_despachador_acciones()

    while True:
        mostrar_menu_principal()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            print("\n[+] Finalizando sesión en Zubbit Gaming Store. ¡Hasta pronto!\n")
            break

        accion = despachador.get(opcion)
        if accion:
            # Transición pura de estado: estado_(t+1) = accion(estado_t)
            estado = accion(estado)
        else:
            print("\n[!] Opción no reconocida. Por favor ingrese un número del menú [0-7].\n")


if __name__ == "__main__":
    print("=" * 88)
    print("          INICIALIZANDO SISTEMA POS FUNCIONAL - ZUBBIT GAMING (UTEM)            ")
    print("=" * 88)

    # 1. Instanciamos el cliente de integración oficial con Shopify Admin API
    cliente_shopify = ShopifyInventario()

    # 2. Sincronizamos el catálogo funcional inmutable con los stocks reales de Shopify
    catalogo_sincronizado = sincronizar_catalogo_con_shopify(CATALOGO_BASE, cliente_shopify)

    # 3. Construimos el estado inicial inmutable
    estado_inicial = EstadoSistema(
        catalogo=catalogo_sincronizado,
        carrito=crear_carrito_vacio(),
        api=cliente_shopify
    )

    # 4. Iniciamos el bucle interactivo funcional
    try:
        ciclo_interactivo(estado_inicial)
    except KeyboardInterrupt:
        print("\n\n[!] Operación interrumpida por el usuario. Sesión finalizada.")
