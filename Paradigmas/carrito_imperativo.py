# ==============================================================================
# TIENDA DE PERIFÉRICOS GAMING: ZUBBIT
# EVENTO ESPECIAL: Pack Setup Competitivo
# Paradigma: Imperativo (Flujo secuencial plano de principio a fin sin funciones)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. ESTADO INICIAL DEL SISTEMA (Catálogo, Precios Reales y Stock Exacto)
# ------------------------------------------------------------------------------
# Periférico 1: Mouse
nombre_p1 = "Mouse Razer Viper V4 Pro"
precio_p1 = 100000
stock_p1 = 30

# Periférico 2: Mousepad
nombre_p2 = "Mousepad Artisan"
precio_p2 = 70000
stock_p2 = 20

# Periférico 3: Audífonos
nombre_p3 = "Audífonos Cloud III"
precio_p3 = 79990
stock_p3 = 34

# Porcentaje de descuento comercial del bundle (20%)
PORCENTAJE_DESCUENTO_PACK = 0.20

# Cálculo del valor unitario del pack base y descuento
precio_base_pack = precio_p1 + precio_p2 + precio_p3  # $249.990
descuento_unit_pack = int(round(precio_base_pack * PORCENTAJE_DESCUENTO_PACK))  # $49.998
precio_pack_con_descuento = precio_base_pack - descuento_unit_pack  # $199.992

# Detección del límite de packs formables según el stock inicial disponible
stock_max_packs = stock_p1
if stock_p2 < stock_max_packs:
    stock_max_packs = stock_p2
if stock_p3 < stock_max_packs:
    stock_max_packs = stock_p3

# Formateo monetario en pesos chilenos (CLP) con '.' como separador de miles
p1_precio_str = f"${precio_p1:,.0f}".replace(",", ".")
p2_precio_str = f"${precio_p2:,.0f}".replace(",", ".")
p3_precio_str = f"${precio_p3:,.0f}".replace(",", ".")
pack_base_str = f"${precio_base_pack:,.0f}".replace(",", ".")
dscto_pack_str = f"-${descuento_unit_pack:,.0f}".replace(",", ".")
pack_promo_str = f"${precio_pack_con_descuento:,.0f}".replace(",", ".")

ancho_total = 88
linea_doble = "=" * ancho_total
linea_simple = "-" * ancho_total
borde_tabla_cat = "+----+------------------------------+---------------+---------------+------------------+"
borde_tabla_res = "+----+------------------------------+-------+---------------+--------------------------+"
borde_cierre_res = "+" + ("-" * (ancho_total - 2)) + "+"

# ------------------------------------------------------------------------------
# 2. ENCABEZADO FORMAL Y REGLAS DEL EVENTO ESPECIAL
# ------------------------------------------------------------------------------
print(linea_doble)
print("                           ZUBBIT GAMING PERIFÉRICOS S.A.                               ")
print("                  SISTEMA DE GESTIÓN COMERCIAL Y FACTURACIÓN (POS)                      ")
print(linea_doble)
print("                 EVENTO ESPECIAL DE TEMPORADA: 'PACK SETUP COMPETITIVO'                 ")
print(linea_simple)
print("TÉRMINOS Y CONDICIONES DE LA PROMOCIÓN:")
print(" • Al comprar los 3 productos en conjunto (Bundle Competitivo), el sistema aplica un")
print("   20% DE DESCUENTO AUTOMÁTICO sobre el valor total de cada pack completo.")
print(" • La bonificación aplica de forma directa por cada trío completo conformado.")
print(" • Unidades adicionales o sobrantes que no conformen un pack se liquidarán a precio de lista.")
print(" • Venta supeditada estrictamente a la validación de existencias en almacén central.")
print(linea_simple)
print("                            CATÁLOGO DE PRODUCTOS EN CAMPAÑA                            ")
print(borde_tabla_cat)
print("| ID | PRODUCTO                     | PRECIO UNIT.  | STOCK DISP.   | ESTADO EVENTO    |")
print(borde_tabla_cat)
print(f"| 01 | {nombre_p1:<28} | {p1_precio_str:>13} | {stock_p1:>7} unid. | Incluido en Pack |")
print(f"| 02 | {nombre_p2:<28} | {p2_precio_str:>13} | {stock_p2:>7} unid. | Incluido en Pack |")
print(f"| 03 | {nombre_p3:<28} | {p3_precio_str:>13} | {stock_p3:>7} unid. | Incluido en Pack |")
print(borde_tabla_cat)
texto_ahorro = f"AHORRO: {dscto_pack_str}"
print(f"| -- | {'TOTAL PACK BASE (3 ÍTEMS)':<28} | {pack_base_str:>13} | {stock_max_packs:>7} packs | {texto_ahorro:<16} |")
print(f"| ** | {'PACK PROMOCIONAL (-20% OFF)':<28} | {pack_promo_str:>13} |  ¡DISPONIBLE! | {'BUNDLE COMPLETO':<16} |")
print(borde_tabla_cat)
print("")

# ------------------------------------------------------------------------------
# 3. CAPTURA Y VALIDACIÓN INTERACTIVA DE CANTIDADES (Flujo lineal secuencial)
# ------------------------------------------------------------------------------
print(">>> SOLICITUD DE PEDIDO - INGRESO DE CANTIDADES:")

# --- Captura secuencial: Periférico 1 (Mouse Razer Viper V4 Pro) ---
cant_p1 = -1
while cant_p1 < 0 or cant_p1 > stock_p1:
    entrada = input(f" -> Ingrese cantidad para [01] {nombre_p1} (Stock disponible: {stock_p1}): ").strip()
    if not entrada.isdigit():
        print("    [!] ERROR: Ingrese un número entero positivo o cero.")
        continue
    cant_p1 = int(entrada)
    if cant_p1 > stock_p1:
        print(f"    [!] RECHAZADO: Stock insuficiente. La bodega solo dispone de {stock_p1} unidades.")
        cant_p1 = -1

# --- Captura secuencial: Periférico 2 (Mousepad Artisan) ---
cant_p2 = -1
while cant_p2 < 0 or cant_p2 > stock_p2:
    entrada = input(f" -> Ingrese cantidad para [02] {nombre_p2} (Stock disponible: {stock_p2}): ").strip()
    if not entrada.isdigit():
        print("    [!] ERROR: Ingrese un número entero positivo o cero.")
        continue
    cant_p2 = int(entrada)
    if cant_p2 > stock_p2:
        print(f"    [!] RECHAZADO: Stock insuficiente. La bodega solo dispone de {stock_p2} unidades.")
        cant_p2 = -1

# --- Captura secuencial: Periférico 3 (Audífonos Cloud III) ---
cant_p3 = -1
while cant_p3 < 0 or cant_p3 > stock_p3:
    entrada = input(f" -> Ingrese cantidad para [03] {nombre_p3} (Stock disponible: {stock_p3}): ").strip()
    if not entrada.isdigit():
        print("    [!] ERROR: Ingrese un número entero positivo o cero.")
        continue
    cant_p3 = int(entrada)
    if cant_p3 > stock_p3:
        print(f"    [!] RECHAZADO: Stock insuficiente. La bodega solo dispone de {stock_p3} unidades.")
        cant_p3 = -1

# ------------------------------------------------------------------------------
# 4. CÁLCULO DE TOTALES, PACKS COMPETITIVOS Y DESCUENTO AUTOMÁTICO
# ------------------------------------------------------------------------------
total_articulos = cant_p1 + cant_p2 + cant_p3

if total_articulos == 0:
    print("\n" + linea_simple)
    print("AVISO: No se ingresaron unidades para facturar. Transacción finalizada.")
    print("Gracias por visitar Zubbit Gaming Store. ¡Hasta pronto!")
    print(linea_simple)
else:
    # Subtotales por producto sin descuento
    subtotal_p1 = cant_p1 * precio_p1
    subtotal_p2 = cant_p2 * precio_p2
    subtotal_p3 = cant_p3 * precio_p3
    subtotal_regular = subtotal_p1 + subtotal_p2 + subtotal_p3

    # Detección imperativa de Packs Competitivos completos (tríos de p1 + p2 + p3)
    packs_completos = cant_p1
    if cant_p2 < packs_completos:
        packs_completos = cant_p2
    if cant_p3 < packs_completos:
        packs_completos = cant_p3

    # Cálculo del descuento según packs completos formados
    monto_descuento = 0
    monto_base_con_descuento = 0

    if packs_completos > 0:
        monto_base_con_descuento = packs_completos * precio_base_pack
        monto_descuento = int(round(monto_base_con_descuento * PORCENTAJE_DESCUENTO_PACK))

    total_final = subtotal_regular - monto_descuento

    # Formateo de subtotales y totales en pesos chilenos
    sub_p1_fmt = f"${subtotal_p1:,.0f}".replace(",", ".")
    sub_p2_fmt = f"${subtotal_p2:,.0f}".replace(",", ".")
    sub_p3_fmt = f"${subtotal_p3:,.0f}".replace(",", ".")
    sub_reg_fmt = f"${subtotal_regular:,.0f}".replace(",", ".")
    desc_fmt = f"-${monto_descuento:,.0f}".replace(",", ".")
    tot_fmt = f"${total_final:,.0f}".replace(",", ".")

    # ------------------------------------------------------------------------------
    # 5. RESUMEN DETALLADO PROFESIONAL DE LA COMPRA (BOLETA COMERCIAL)
    # ------------------------------------------------------------------------------
    print("\n" + linea_doble)
    print("                   RESUMEN DETALLADO DE COMPRA - COMPROBANTE OFICIAL                    ")
    print(linea_doble)
    print(borde_tabla_res)
    print("| ID | DESCRIPCIÓN DEL ARTÍCULO     | CANT. | PRECIO UNIT.  |           SUBTOTAL (CLP) |")
    print(borde_tabla_res)
    print(f"| 01 | {nombre_p1:<28} | {cant_p1:>5} | {p1_precio_str:>13} | {sub_p1_fmt:>24} |")
    print(f"| 02 | {nombre_p2:<28} | {cant_p2:>5} | {p2_precio_str:>13} | {sub_p2_fmt:>24} |")
    print(f"| 03 | {nombre_p3:<28} | {cant_p3:>5} | {p3_precio_str:>13} | {sub_p3_fmt:>24} |")
    print(borde_tabla_res)
    
    # Filas de consolidación y descuentos
    fila_subtotal = f"| {'SUBTOTAL BRUTO (PRECIOS DE LISTA):':<60}{sub_reg_fmt:>24} |"
    print(fila_subtotal)

    if packs_completos > 0:
        texto_pack = f"{packs_completos}x Pack Setup Competitivo calificado(s)"
        fila_pack = f"| BONIFICACIÓN: {texto_pack:<70} |"
        fila_desc = f"| {'DESCUENTO PROMOCIONAL ESPECIAL (20% SOBRE PACKS):':<60}{desc_fmt:>24} |"
        print(fila_pack)
        print(fila_desc)
    else:
        fila_no_pack = f"| {'BONIFICACIÓN: No califica a Pack Competitivo (Incompleto)':<84} |"
        print(fila_no_pack)

    print(borde_cierre_res)
    fila_total = f"| {'TOTAL NETO A PAGAR (CLP):':<60}{tot_fmt:>24} |"
    print(fila_total)
    print(linea_doble)

    # ------------------------------------------------------------------------------
    # 6. CONFIRMACIÓN Y ACTUALIZACIÓN DE STOCK
    # ------------------------------------------------------------------------------
    respuesta = ""
    while respuesta not in ["S", "N"]:
        respuesta = input("\n[CONFIRMACIÓN] ¿Desea autorizar la compra y descontar stock de bodega? [S/N]: ").strip().upper()
        if respuesta not in ["S", "N"]:
            print(" -> Entrada no válida. Digite 'S' para confirmar la compra o 'N' para anularla.")

    if respuesta == "S":
        stock_p1 = stock_p1 - cant_p1
        stock_p2 = stock_p2 - cant_p2
        stock_p3 = stock_p3 - cant_p3

        print("\n" + ("*" * ancho_total))
        print("          ¡TRANSACCIÓN COMPLETADA CON ÉXITO EN ZUBBIT GAMING STORE!                     ")
        print("*" * ancho_total)
        print("ESTADO ACTUALIZADO DEL INVENTARIO EN BODEGA CENTRAL:")
        print(f" • [ID 01] {nombre_p1:<26}: {stock_p1:>2} unid. disponibles (Descargadas: {cant_p1})")
        print(f" • [ID 02] {nombre_p2:<26}: {stock_p2:>2} unid. disponibles (Descargadas: {cant_p2})")
        print(f" • [ID 03] {nombre_p3:<26}: {stock_p3:>2} unid. disponibles (Descargadas: {cant_p3})")
        print("*" * ancho_total)
    else:
        print("\n" + linea_simple)
        print("OPERACIÓN ANULADA: La compra fue cancelada por el usuario. No se afectó el stock.")
        print(linea_simple)

print("\nFin del programa.")