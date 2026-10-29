# ==============================================================================
# PROYECTO: ZUBBIT GAMING STORE (UTEM)
# Módulo: Paradigmas de Programación - Programación Orientada a Objetos (POO)
# Archivo: Paradigmas/poo_clases.py
# Conceptos: Encapsulamiento, Herencia y Polimorfismo
# ==============================================================================

"""
GUÍA TEÓRICA Y CONCEPTUAL DE POO:

1. ENCAPSULAMIENTO:
   Empaqueta datos y métodos dentro de una clase restringiendo el acceso directo
   al estado interno. En Python se emplean atributos privados con doble guión bajo
   (__nombre) y métodos Getters/Setters explícitos con validación de invariantes
   (por ejemplo, impedir que el stock sea negativo).

2. HERENCIA:
   Mecanismo por el cual una subclase ('ProductoGaming') hereda atributos y
   comportamientos de una superclase ('Producto'), promoviendo la reutilización
   de código y permitiendo la especialización mediante 'super().__init__(...)'.

3. POLIMORFISMO (SOBRESCRITURA DE MÉTODOS):
   Habilidad de distintas clases de responder a un mismo mensaje o llamada de
   método de forma particular. 'ProductoGaming' sobrescribe el método
   'calcular_descuento()' y 'calcular_subtotal()' de 'Producto' para aplicar
   la regla de negocio del 'Bundle Competitivo' (20% de descuento).
"""

from typing import List, Dict, Optional


# ==============================================================================
# 1. CLASE BASE: Producto
# ==============================================================================
class Producto:
    """
    Clase base que representa un artículo general del catálogo.
    Aplica encapsulamiento estricto sobre sus datos esenciales.
    """

    def __init__(self, nombre: str, precio: int, stock: int, id_shopify: Optional[str] = None):
        """
        Constructor de la clase base Producto.
        Valida tipos y valores iniciales protegiendo el estado interno.
        """
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del producto debe ser una cadena de texto no vacía.")
        if precio < 0:
            raise ValueError(f"El precio no puede ser negativo. Recibido: ${precio}")
        if stock < 0:
            raise ValueError(f"El stock inicial no puede ser negativo. Recibido: {stock}")

        # Atributos fuertemente privados (Name Mangling: _Producto__atributo)
        self.__nombre: str = nombre.strip()
        self.__precio: int = int(precio)
        self.__stock: int = int(stock)
        self.__id_shopify: Optional[str] = str(id_shopify) if id_shopify else None

    # --------------------------------------------------------------------------
    # GETTERS EXPLÍCITOS
    # --------------------------------------------------------------------------
    def get_nombre(self) -> str:
        """Retorna el nombre comercial del producto."""
        return self.__nombre

    def get_precio(self) -> int:
        """Retorna el precio unitario oficial del producto en CLP."""
        return self.__precio

    def get_stock(self) -> int:
        """Retorna la cantidad física de unidades disponibles en inventario."""
        return self.__stock

    def get_id_shopify(self) -> Optional[str]:
        """Retorna el identificador del producto en la plataforma Shopify."""
        return self.__id_shopify

    # --------------------------------------------------------------------------
    # SETTERS EXPLÍCITOS CON VALIDACIÓN
    # --------------------------------------------------------------------------
    def set_nombre(self, nuevo_nombre: str) -> None:
        """Actualiza el nombre del producto validando que no sea nulo ni vacío."""
        if not nuevo_nombre or not isinstance(nuevo_nombre, str) or not nuevo_nombre.strip():
            raise ValueError("El nuevo nombre no puede estar vacío.")
        self.__nombre = nuevo_nombre.strip()

    def set_precio(self, nuevo_precio: int) -> None:
        """Actualiza el precio garantizando que no sea negativo."""
        if not isinstance(nuevo_precio, (int, float)) or nuevo_precio < 0:
            raise ValueError(f"Precio inválido: ${nuevo_precio}. Debe ser mayor o igual a 0.")
        self.__precio = int(nuevo_precio)

    def set_stock(self, nuevo_stock: int) -> None:
        """
        Actualiza el inventario físico disponible.
        REGLA DE ENCAPSULAMIENTO: Valida estrictamente que el stock nunca sea negativo.
        """
        if not isinstance(nuevo_stock, int):
            raise TypeError(f"El stock debe ser un entero. Tipo recibido: {type(nuevo_stock).__name__}")
        if nuevo_stock < 0:
            raise ValueError(f"Violación de invariante: El stock no puede ser negativo ({nuevo_stock}).")
        self.__stock = nuevo_stock

    def set_id_shopify(self, nuevo_id: str) -> None:
        """Actualiza o asocia el ID de inventario de Shopify."""
        if not nuevo_id:
            raise ValueError("El ID de Shopify proporcionado es inválido.")
        self.__id_shopify = str(nuevo_id)

    # --------------------------------------------------------------------------
    # MÉTODOS DE CÁLCULO POLIMÓRFICOS
    # --------------------------------------------------------------------------
    def calcular_descuento(self, cantidad: int = 1, aplica_bundle: bool = False) -> int:
        """
        MÉTODO POLIMÓRFICO BASE:
        Los productos estándar no aplican descuentos por bundle (descuento = 0).
        """
        return 0

    def calcular_subtotal(self, cantidad: int = 1, aplica_bundle: bool = False) -> int:
        """
        Calcula el subtotal a pagar restando el descuento polimórfico al precio regular.
        """
        bruto = self.__precio * cantidad
        descuento = self.calcular_descuento(cantidad, aplica_bundle)
        return bruto - descuento

    # --------------------------------------------------------------------------
    # MÉTODOS DE OPERACIÓN DE INVENTARIO
    # --------------------------------------------------------------------------
    def reducir_stock(self, cantidad: int) -> bool:
        """Disminuye el stock disponible tras una venta si existen unidades suficientes."""
        if cantidad <= 0:
            raise ValueError("La cantidad a descontar debe ser un número entero positivo.")
        if self.__stock >= cantidad:
            self.__stock -= cantidad
            return True
        return False

    def reabastecer_stock(self, cantidad: int) -> None:
        """Incrementa el stock físico tras la llegada de mercancía."""
        if cantidad <= 0:
            raise ValueError("La cantidad a reabastecer debe ser estrictamente positiva.")
        self.__stock += cantidad

    # --------------------------------------------------------------------------
    # REPRESENTACIÓN EN TEXTO
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Representación limpia en texto del producto estándar."""
        precio_fmt = f"${self.__precio:,.0f}".replace(",", ".")
        return f"[PRODUCTO] {self.__nombre:<28} | Precio: {precio_fmt:>10} | Stock: {self.__stock:>3} unid."

    def __repr__(self) -> str:
        return f"Producto(nombre='{self.__nombre}', precio={self.__precio}, stock={self.__stock})"


# ==============================================================================
# 2. SUBCLASE: ProductoGaming (HERENCIA Y POLIMORFISMO)
# ==============================================================================
class ProductoGaming(Producto):
    """
    Subclase especializada que hereda de 'Producto'.
    Representa periféricos de alto rendimiento para gaming competitivo en Zubbit.
    Añade atributos propios (categoría, dpi_o_hz) y sobrescribe métodos
    polimórficamente para implementar la regla del Bundle Competitivo (20% OFF).
    """

    # Regla de negocio oficial de Zubbit: 20% de descuento en el Bundle Competitivo
    PORCENTAJE_DESCUENTO_BUNDLE = 0.20

    def __init__(self, nombre: str, precio: int, stock: int, 
                 categoria: str, dpi_o_hz: str, id_shopify: Optional[str] = None):
        """
        Constructor de ProductoGaming.
        Utiliza 'super().__init__(...)' para delegar la inicialización base
        e inicializa sus propios atributos protegidos/privados.
        """
        super().__init__(nombre=nombre, precio=precio, stock=stock, id_shopify=id_shopify)

        if not categoria or not isinstance(categoria, str) or not categoria.strip():
            raise ValueError("La categoría gaming debe ser una cadena válida (ej. Mouse, Mousepad, Audífonos).")
        if not dpi_o_hz or not isinstance(dpi_o_hz, str) or not dpi_o_hz.strip():
            raise ValueError("La especificación técnica (dpi_o_hz) debe ser una cadena válida.")

        # Atributos específicos encapsulados de ProductoGaming
        self.__categoria: str = categoria.strip().capitalize()
        self.__dpi_o_hz: str = dpi_o_hz.strip()

    # --------------------------------------------------------------------------
    # GETTERS Y SETTERS ESPECÍFICOS
    # --------------------------------------------------------------------------
    def get_categoria(self) -> str:
        """Retorna la categoría del periférico (ej. Mouse, Mousepad, Audífonos)."""
        return self.__categoria

    def set_categoria(self, nueva_categoria: str) -> None:
        """Modifica la categoría validando que no sea nula."""
        if not nueva_categoria or not isinstance(nueva_categoria, str) or not nueva_categoria.strip():
            raise ValueError("Categoría gaming inválida.")
        self.__categoria = nueva_categoria.strip().capitalize()

    def get_dpi_o_hz(self) -> str:
        """Retorna las especificaciones de rendimiento (DPI del sensor o Hz de tasa de refresco)."""
        return self.__dpi_o_hz

    def set_dpi_o_hz(self, nuevo_dpi_o_hz: str) -> None:
        """Modifica la especificación de rendimiento."""
        if not nuevo_dpi_o_hz or not isinstance(nuevo_dpi_o_hz, str) or not nuevo_dpi_o_hz.strip():
            raise ValueError("Especificación de rendimiento inválida.")
        self.__dpi_o_hz = nuevo_dpi_o_hz.strip()

    # --------------------------------------------------------------------------
    # POLIMORFISMO: Sobrescritura de métodos de cálculo
    # --------------------------------------------------------------------------
    def calcular_descuento(self, cantidad: int = 1, aplica_bundle: bool = False) -> int:
        """
        POLIMORFISMO EN ACCIÓN:
        Sobrescribe el método de la clase padre 'Producto'.
        Si 'aplica_bundle' es True, aplica de forma automática un 20% de descuento
        sobre el valor del periférico gaming participante en el pack.
        """
        if aplica_bundle:
            descuento_unitario = self.get_precio() * self.PORCENTAJE_DESCUENTO_BUNDLE
            return int(round(descuento_unitario * cantidad))
        return 0

    def calcular_subtotal(self, cantidad: int = 1, aplica_bundle: bool = False) -> int:
        """
        POLIMORFISMO:
        Retorna el subtotal neto tras descontar el 20% si forma parte del bundle.
        """
        precio_bruto = self.get_precio() * cantidad
        descuento = self.calcular_descuento(cantidad, aplica_bundle)
        return precio_bruto - descuento

    # --------------------------------------------------------------------------
    # REPRESENTACIÓN POLIMÓRFICA EN TEXTO
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """
        POLIMORFISMO: Sobrescribe __str__ para mostrar la información completa
        del periférico gaming (categoría, specs de rendimiento, precio y stock).
        """
        precio_fmt = f"${self.get_precio():,.0f}".replace(",", ".")
        return (f"[GAMING: {self.__categoria:<9}] {self.get_nombre():<26} "
                f"| Specs: {self.__dpi_o_hz:<26} | Precio: {precio_fmt:>10} | Stock: {self.get_stock():>2} unid.")

    def __repr__(self) -> str:
        return (f"ProductoGaming(nombre='{self.get_nombre()}', precio={self.get_precio()}, "
                f"stock={self.get_stock()}, categoria='{self.__categoria}', dpi_o_hz='{self.__dpi_o_hz}')")


# ==============================================================================
# 3. CLASE: Carrito (ADMINISTRADOR DE COLECCIÓN DE PRODUCTOS)
# ==============================================================================
class Carrito:
    """
    Administra una colección de objetos 'Producto' y 'ProductoGaming'.
    Aplica Polimorfismo al interactuar con cualquier producto de la jerarquía
    y encapsula las reglas del negocio de la tienda Zubbit Gaming.
    """

    def __init__(self):
        """
        Inicializa un carrito vacío.
        Colección encapsulada: {Producto: cantidad_enteros}
        """
        self.__items: Dict[Producto, int] = {}

    # --------------------------------------------------------------------------
    # GESTIÓN DE ELEMENTOS
    # --------------------------------------------------------------------------
    def agregar_producto(self, producto: Producto, cantidad: int = 1) -> bool:
        """
        Agrega un Producto al carrito (aprovechando el polimorfismo, acepta 'Producto'
        o cualquier subclase derivada como 'ProductoGaming').
        """
        if not isinstance(producto, Producto):
            raise TypeError("Solo se pueden agregar instancias derivadas de 'Producto' al carrito.")
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad a agregar debe ser un número entero mayor a cero.")

        cantidad_actual = self.__items.get(producto, 0)
        cantidad_pretendida = cantidad_actual + cantidad

        # Validación con el stock disponible en el objeto
        if cantidad_pretendida > producto.get_stock():
            print(f"[!] Stock insuficiente para '{producto.get_nombre()}'. "
                  f"Disponible en bodega: {producto.get_stock()} | Solicitado: {cantidad_pretendida}")
            return False

        self.__items[producto] = cantidad_pretendida
        return True

    def eliminar_producto(self, producto: Producto, cantidad: Optional[int] = None) -> bool:
        """
        Elimina un producto del carrito o disminuye su cantidad.
        """
        if producto not in self.__items:
            print(f"[!] El producto '{producto.get_nombre()}' no está en el carrito.")
            return False

        if cantidad is None or cantidad >= self.__items[producto]:
            del self.__items[producto]
            return True

        if cantidad > 0:
            self.__items[producto] -= cantidad
            return True

        return False

    def vaciar(self) -> None:
        """Vacía completamente el carrito."""
        self.__items.clear()

    def get_items(self) -> Dict[Producto, int]:
        """
        Retorna una copia del diccionario encapsulado de ítems y cantidades
        {Producto: cantidad} para proteger la colección interna.
        """
        return self.__items.copy()

    # --------------------------------------------------------------------------
    # REGLAS DEL NEGOCIO Y EVALUACIÓN POLIMÓRFICA DE BUNDLE
    # --------------------------------------------------------------------------
    def evaluar_bundle_competitivo(self) -> int:
        """
        Evalúa si el carrito contiene el trío calificado de periféricos gaming:
        (1 Mouse + 1 Mousepad + 1 Audífono).
        Retorna la cantidad exacta de packs completos formables.
        """
        cant_mouse = 0
        cant_mousepad = 0
        cant_audifonos = 0

        for producto, cantidad in self.__items.items():
            if isinstance(producto, ProductoGaming):
                cat = producto.get_categoria().lower()
                if "mousepad" in cat or "pad" in cat:
                    cant_mousepad += cantidad
                elif "mouse" in cat:
                    cant_mouse += cantidad
                elif "audífono" in cat or "audifono" in cat or "headset" in cat:
                    cant_audifonos += cantidad

        # La cantidad de bundles completos formados es el mínimo de las 3 categorías
        return min(cant_mouse, cant_mousepad, cant_audifonos)

    def calcular_subtotal_bruto(self) -> int:
        """Calcula el total regular sin descuentos (precio de lista * cantidad)."""
        return sum(producto.get_precio() * cant for producto, cant in self.__items.items())

    def calcular_descuento_total(self) -> int:
        """
        POLIMORFISMO EN LA COLECCIÓN:
        Recorre los productos del carrito invocando el método 'calcular_descuento()'.
        Cada objeto responderá según su propia implementación polimórfica.
        """
        packs_bundle = self.evaluar_bundle_competitivo()
        descuento_acumulado = 0

        if packs_bundle > 0:
            for producto, cantidad in self.__items.items():
                unidades_en_pack = min(cantidad, packs_bundle)
                # Invocación polimórfica: ProductoGaming aplica 20%, Producto aplica 0%
                descuento_acumulado += producto.calcular_descuento(unidades_en_pack, aplica_bundle=True)

        return descuento_acumulado

    def calcular_total(self) -> int:
        """Calcula el total final neto a pagar con el beneficio aplicado."""
        return self.calcular_subtotal_bruto() - self.calcular_descuento_total()

    def esta_vacio(self) -> bool:
        """Indica si el carrito carece de artículos."""
        return len(self.__items) == 0

    # --------------------------------------------------------------------------
    # PRESENTACIÓN VISUAL
    # --------------------------------------------------------------------------
    def mostrar_detalle(self) -> None:
        """Muestra en consola el resumen oficial y alineado del carrito."""
        borde = "+" + "-" * 88 + "+"
        ancho = 88
        linea_doble = "=" * (ancho + 2)

        print("\n" + linea_doble)
        print(f"| {'DETALLE DEL CARRITO - ZUBBIT GAMING STORE (POO)':^{ancho}} |")
        print(linea_doble)
        print(borde)
        print(f"| {'CANT.':<6} | {'DESCRIPCIÓN DEL ARTÍCULO':<38} | {'PRECIO UNIT.':<16} | {'SUBTOTAL BRUTO':<20} |")
        print(borde)

        if self.esta_vacio():
            print(f"| {'El carrito se encuentra actualmente vacío.':^{ancho}} |")
        else:
            packs_bundle = self.evaluar_bundle_competitivo()

            for producto, cantidad in self.__items.items():
                p_unit_str = f"${producto.get_precio():,.0f}".replace(",", ".")
                sub_bruto_str = f"${(producto.get_precio() * cantidad):,.0f}".replace(",", ".")
                print(f"| {cantidad:>5}  | {producto.get_nombre():<38} | {p_unit_str:>16} | {sub_bruto_str:>20} |")

            print(borde)
            subtotal_bruto = self.calcular_subtotal_bruto()
            descuento = self.calcular_descuento_total()
            total_final = self.calcular_total()

            sub_bruto_str = f"${subtotal_bruto:,.0f}".replace(",", ".")
            desc_str = f"-${descuento:,.0f}".replace(",", ".")
            total_str = f"${total_final:,.0f}".replace(",", ".")

            print(f"| {'SUBTOTAL BRUTO (PRECIOS DE LISTA):':<65} {sub_bruto_str:>20} |")

            if packs_bundle > 0:
                texto_promo = f"BONIFICACIÓN: {packs_bundle}x Pack Setup Competitivo (-20% OFF)"
                print(f"| {texto_promo:<65} {desc_str:>20} |")
            else:
                print(f"| {'PROMOCIÓN BUNDLE COMPETITIVO:':<65} {'No califica':>20} |")

            print(borde)
            print(f"| {'TOTAL NETO A PAGAR:':<65} {total_str:>20} |")

        print(linea_doble + "\n")


# ==============================================================================
# 4. BLOQUE DE PRUEBA Y DEMOSTRACIÓN DE HERENCIA Y POLIMORFISMO
# ==============================================================================
if __name__ == "__main__":
    print("=" * 90)
    print("        DEMOSTRACIÓN DE POO AVANZADA: HERENCIA Y POLIMORFISMO (UTEM)     ")
    print("=" * 90)

    # 1. Instanciación exclusiva de los 3 periféricos oficiales de Zubbit Gaming Store
    print("\n--- 1. Instanciación de Periféricos Oficiales (ProductoGaming) ---")
    mouse = ProductoGaming(
        nombre="Mouse Razer Viper V4 Pro",
        precio=100000,
        stock=30,
        categoria="Mouse",
        dpi_o_hz="35.000 DPI / 8.000 Hz",
        id_shopify="52960852705345"
    )

    mousepad = ProductoGaming(
        nombre="Mousepad Gamer Artisan",
        precio=70000,
        stock=20,
        categoria="Mousepad",
        dpi_o_hz="FX Soft / 490x420mm",
        id_shopify="52960852705346"
    )

    audifonos = ProductoGaming(
        nombre="Audífonos HyperX Cloud III",
        precio=79990,
        stock=34,
        categoria="Audífonos",
        dpi_o_hz="Drivers 53mm / 10Hz-21kHz",
        id_shopify="52960852705347"
    )

    # Impresión utilizando el método __str__ polimórfico de cada objeto
    print(mouse)
    print(mousepad)
    print(audifonos)

    # 2. Demostración de Polimorfismo en el cálculo de descuento individual vs bundle
    print("\n--- 2. Demostración de Polimorfismo en Métodos de Descuento ---")
    print(f"Comportamiento de '{mouse.get_nombre()}':")
    desc_individual = mouse.calcular_descuento(1, aplica_bundle=False)
    sub_individual = mouse.calcular_subtotal(1, aplica_bundle=False)
    desc_bundle = mouse.calcular_descuento(1, aplica_bundle=True)
    sub_bundle = mouse.calcular_subtotal(1, aplica_bundle=True)

    print(f" -> Compra individual (sin bundle) : Subtotal: ${sub_individual:,.0f}".replace(",", ".") + f" | Descuento: ${desc_individual}")
    print(f" -> Compra en bundle (20% OFF)     : Subtotal: ${sub_bundle:,.0f}".replace(",", ".") + f" | Descuento: -${desc_bundle:,.0f}".replace(",", "."))

    # 3. Integración en el Carrito de Compras (Escenario oficial: 2 Mouses, 1 Mousepad, 1 Audífono)
    print("\n--- 3. Integración en el Carrito de Compras (Pack Setup Competitivo) ---")
    carrito = Carrito()

    # Añadimos los periféricos reales de Zubbit:
    # 2 Mouses, 1 Mousepad y 1 Audífono:
    # Forma 1 Pack Competitivo con 20% OFF sobre el pack ($49.998), y el 2do mouse paga precio regular.
    carrito.agregar_producto(mouse, cantidad=2)
    carrito.agregar_producto(mousepad, cantidad=1)
    carrito.agregar_producto(audifonos, cantidad=1)

    # Mostramos el desglose completo del carrito con la bonificación aplicada
    carrito.mostrar_detalle()

    print("=" * 90)
    print("                     FIN DE LA DEMOSTRACIÓN POO                          ")
    print("=" * 90)
