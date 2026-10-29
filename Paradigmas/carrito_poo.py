# ==============================================================================
# PROYECTO: ZUBBIT GAMING STORE (UTEM)
# Módulo: Paradigmas de Programación - Programación Orientada a Objetos (POO)
# Archivo: Paradigmas/carrito_poo.py
# Descripción: Script interactivo ejecutable basado en POO pura integrado con Shopify
# ==============================================================================

import os
import sys

# ------------------------------------------------------------------------------
# 1. RESOLUCIÓN DE RUTAS E IMPORTACIÓN DE MÓDULOS DEL PROYECTO
# ------------------------------------------------------------------------------
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.abspath(os.path.join(directorio_actual, ".."))
for ruta in (directorio_actual, directorio_raiz):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

# Importación de clases de dominio y conector de API
from poo_clases import Producto, ProductoGaming, Carrito
from api_shopify.conexion_shopify import ShopifyInventario


# ==============================================================================
# 2. EXCEPCIONES PERSONALIZADAS DE DOMINIO (POO)
# ==============================================================================
class ZubbitException(Exception):
    """Clase base para todas las excepciones del dominio Zubbit Gaming."""
    pass


class StockInsuficienteException(ZubbitException):
    """Lanzada cuando se intenta agregar o debitar más stock del existente en bodega."""
    def __init__(self, producto: str, solicitado: int, disponible: int):
        self.producto = producto
        self.solicitado = solicitado
        self.disponible = disponible
        super().__init__(
            f"Stock insuficiente para '{producto}'. Solicitado: {solicitado} unid. | Disponible: {disponible} unid."
        )


class CarritoVacioException(ZubbitException):
    """Lanzada cuando se intenta procesar el pago de un carrito sin productos."""
    def __init__(self):
        super().__init__("Operación inválida: El carrito de compras se encuentra vacío.")


class OperacionCanceladaException(ZubbitException):
    """Lanzada cuando el usuario o cliente anula la confirmación de compra."""
    def __init__(self):
        super().__init__("Transacción cancelada por el usuario. No se afectó el inventario en la nube.")


# ==============================================================================
# 3. CONTROLADOR PRINCIPAL: SistemaVentasPOO
# ==============================================================================
class SistemaVentasPOO:
    """
    Controlador orientado a objetos que encapsula la lógica de negocio,
    el catálogo sincronizado con Shopify, el carrito del cliente y la interfaz CLI.
    """

    def __init__(self):
        # 1. Instanciación del conector de Shopify
        self.__shopify: ShopifyInventario = ShopifyInventario()
        # 2. Instanciación del carrito de compras
        self.__carrito: Carrito = Carrito()
        # 3. Catálogo interno indexado: {opcion_num: ProductoGaming}
        self.__catalogo: dict[int, ProductoGaming] = {}
        # Sincronización inicial del inventario
        self._sincronizar_catalogo_con_shopify()

    # --------------------------------------------------------------------------
    # SINCRONIZACIÓN CON SHOPIFY ADMIN API
    # --------------------------------------------------------------------------
    def _sincronizar_catalogo_con_shopify(self) -> None:
        """
        Consulta el stock real desde la API de Shopify y construye
        las instancias polimórficas de ProductoGaming.
        """
        print("[*] Sincronizando catálogo en tiempo real con Shopify...")
        stock_shopify = self.__shopify.consultar_stock()

        stock_mouse = stock_shopify.get("Mouse Razer Viper V4 Pro", 30) if stock_shopify else 30
        stock_mousepad = stock_shopify.get("Mousepad Gamer Artisan", 20) if stock_shopify else 20
        stock_audifonos = stock_shopify.get("Audífonos HyperX Cloud III", 34) if stock_shopify else 34

        self.__catalogo = {
            1: ProductoGaming(
                nombre="Mouse Razer Viper V4 Pro",
                precio=100000,
                stock=stock_mouse,
                categoria="Mouse",
                dpi_o_hz="35.000 DPI / 8.000 Hz",
                id_shopify="52960852705345"
            ),
            2: ProductoGaming(
                nombre="Mousepad Gamer Artisan",
                precio=70000,
                stock=stock_mousepad,
                categoria="Mousepad",
                dpi_o_hz="FX Soft / 490x420mm",
                id_shopify="52960852705346"
            ),
            3: ProductoGaming(
                nombre="Audífonos HyperX Cloud III",
                precio=79990,
                stock=stock_audifonos,
                categoria="Audífonos",
                dpi_o_hz="Drivers 53mm / 10Hz-21kHz",
                id_shopify="52960852705347"
            )
        }
        print("[+] Catálogo sincronizado exitosamente.\n")

    # --------------------------------------------------------------------------
    # MÉTODOS DE VISTA Y PRESENTACIÓN
    # --------------------------------------------------------------------------
    def mostrar_banner(self) -> None:
        """Muestra el encabezado corporativo del sistema."""
        ancho = 88
        print("=" * ancho)
        print("                           ZUBBIT GAMING PERIFÉRICOS S.A.                               ")
        print("               SISTEMA DE VENTAS POS - PROGRAMACIÓN ORIENTADA A OBJETOS                 ")
        print("=" * ancho)
        print("                 EVENTO ESPECIAL: 'PACK SETUP COMPETITIVO' (-20% OFF)                   ")
        print("-" * ancho)

    def mostrar_catalogo(self) -> None:
        """Imprime la tabla formal del catálogo con precios chilenos y stock."""
        borde = "+----+------------------------------+---------------+---------------+------------------+"
        print("\n" + borde)
        print("| ID | PRODUCTO                     | PRECIO UNIT.  | STOCK DISP.   | ESTADO PROMO     |")
        print(borde)

        for id_opc, prod in self.__catalogo.items():
            p_fmt = f"${prod.get_precio():,.0f}".replace(",", ".")
            print(f"| {id_opc:02d} | {prod.get_nombre():<28} | {p_fmt:>13} | {prod.get_stock():>7} unid. | Pack Setup (20%) |")

        print(borde)
        print("¡Compra los 3 periféricos juntos y el sistema aplicará un 20% OFF automático!")

    def mostrar_menu_opciones(self) -> None:
        """Despliega el menú principal interactivo."""
        print("\n" + "-" * 45)
        print("               MENÚ PRINCIPAL                ")
        print("-" * 45)
        print(" [1] Ver catálogo de periféricos")
        print(" [2] Agregar producto al carrito")
        print(" [3] Ver detalle del carrito (con bundle)")
        print(" [4] Procesar Checkout y Actualizar Shopify")
        print(" [5] Vaciar carrito")
        print(" [0] Salir del sistema")
        print("-" * 45)

    # --------------------------------------------------------------------------
    # MÉTODOS DE OPERACIÓN DEL CARRITO
    # --------------------------------------------------------------------------
    def agregar_producto_interactivo(self) -> None:
        """Captura interactivamente la selección del usuario y valida stock."""
        self.mostrar_catalogo()
        opcion_str = input("\n -> Seleccione el ID del producto a agregar [1-3] (0 para volver): ").strip()
        if not opcion_str.isdigit() or int(opcion_str) not in self.__catalogo:
            if opcion_str == "0":
                return
            print("[!] Opción no válida. Ingrese un ID correspondiente al catálogo.")
            return

        id_prod = int(opcion_str)
        producto_sel = self.__catalogo[id_prod]

        cant_str = input(f" -> Ingrese cantidad para '{producto_sel.get_nombre()}' (Stock disponible: {producto_sel.get_stock()}): ").strip()
        if not cant_str.isdigit() or int(cant_str) <= 0:
            print("[!] Cantidad inválida. Debe ser un número entero mayor a 0.")
            return

        cantidad = int(cant_str)

        try:
            # Validación con excepción orientada a objetos
            if cantidad > producto_sel.get_stock():
                raise StockInsuficienteException(
                    producto=producto_sel.get_nombre(),
                    solicitado=cantidad,
                    disponible=producto_sel.get_stock()
                )

            exito = self.__carrito.agregar_producto(producto_sel, cantidad)
            if exito:
                print(f"[✓] Se agregaron {cantidad} unidad(es) de '{producto_sel.get_nombre()}' al carrito.")
        except StockInsuficienteException as e:
            print(f"\n[!] ERROR DE STOCK: {e}")
        except Exception as e:
            print(f"[!] Error inesperado al agregar producto: {e}")

    # --------------------------------------------------------------------------
    # CHECKOUT Y ACTUALIZACIÓN REAL EN SHOPIFY
    # --------------------------------------------------------------------------
    def procesar_checkout(self) -> None:
        """
        Ejecuta el flujo de confirmación de compra y, tras la autorización del cliente,
        actualiza físicamente el stock en la nube mediante Shopify REST Admin API.
        """
        try:
            if self.__carrito.esta_vacio():
                raise CarritoVacioException()

            # 1. Mostrar resumen con evaluación polimórfica del bundle
            self.__carrito.mostrar_detalle()

            # 2. Solicitud de autorización interactiva
            resp = ""
            while resp not in ["S", "N"]:
                resp = input("¿Desea autorizar la compra y descontar stock real en Shopify? [S/N]: ").strip().upper()
                if resp not in ["S", "N"]:
                    print(" -> Por favor, ingrese 'S' para confirmar o 'N' para cancelar.")

            if resp != "S":
                raise OperacionCanceladaException()

            # 3. Preparar el diccionario de cantidades para la API de Shopify
            items_carrito = self.__carrito.get_items()
            cantidades_debitar = {prod.get_nombre(): cant for prod, cant in items_carrito.items()}

            print("\n" + "=" * 88)
            print("         COMUNICACIÓN CON SHOPIFY ADMIN API - ACTUALIZACIÓN DE INVENTARIO        ")
            print("=" * 88)

            # Invocación real a la REST API de Shopify (simular=False)
            exito_shopify = self.__shopify.reducir_stock_bundle(cantidades_debitar, simular=False)

            if exito_shopify:
                print("\n" + "*" * 88)
                print("           ¡TRANSACCIÓN COMPLETADA Y REGISTRADA EN SHOPIFY CON ÉXITO!           ")
                print("*" * 88)

                # Descontar el stock en los objetos locales del catálogo (POO)
                for prod_obj, cant_vendida in items_carrito.items():
                    prod_obj.reducir_stock(cant_vendida)

                print("INVENTARIO ACTUALIZADO EN OBJETOS LOCALES Y BODEGA CENTRAL:")
                for prod_obj in self.__catalogo.values():
                    print(f" • {prod_obj.get_nombre():<28} : {prod_obj.get_stock():>2} unidades disponibles")

                # Vaciar el carrito tras compra exitosa
                self.__carrito.vaciar()
                print("*" * 88)
            else:
                print("\n[!] Hubo un problema al actualizar algunos ítems en Shopify. Revisa la consola.")

        except CarritoVacioException as e:
            print(f"\n[!] AVISO: {e}")
        except OperacionCanceladaException as e:
            print(f"\n[i] CANCELACIÓN: {e}")
        except Exception as e:
            print(f"\n[!] ERROR EN CHECKOUT: {e}")

    # --------------------------------------------------------------------------
    # BUCLE DE EJECUCIÓN PRINCIPAL
    # --------------------------------------------------------------------------
    def ejecutar(self) -> None:
        """Bucle principal del sistema interactivo."""
        self.mostrar_banner()

        ejecutando = True
        while ejecutando:
            self.mostrar_menu_opciones()
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self.mostrar_catalogo()
            elif opcion == "2":
                self.agregar_producto_interactivo()
            elif opcion == "3":
                self.__carrito.mostrar_detalle()
            elif opcion == "4":
                self.procesar_checkout()
            elif opcion == "5":
                self.__carrito.vaciar()
                print("[✓] El carrito ha sido vaciado completamente.")
            elif opcion == "0":
                print("\nGracias por utilizar el Sistema de Ventas de Zubbit Gaming Store. ¡Hasta pronto!")
                ejecutando = False
            else:
                print("[!] Opción inválida. Digite un número del 0 al 5.")


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    app = SistemaVentasPOO()
    app.ejecutar()
