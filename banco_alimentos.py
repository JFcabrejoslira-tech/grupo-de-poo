# ============================================================
# CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
# Version basica (sin POO): funciones, listas, tuplas y diccionarios
# ============================================================

# ------------------------------------------------------------
# ALMACENAMIENTO EN MEMORIA
# ------------------------------------------------------------
# Diccionarios: la llave es el codigo (las llaves son unicas)
donantes = {}       # {codigo: {"nombre", "tipo", "contacto"}}
beneficiarios = {}  # {codigo: {"nombre", "tipo", "personas"}}
productos = {}      # {codigo: {"nombre", "categoria", "unidad"}}
lotes = {}          # {codigoLote: {"producto", "donante", "recibido", "disponible", "perdido", "vencimiento"}}

# Listas de registros (historial)
donaciones = []     # [{"donante", "fecha", "producto", "lote", "cantidad"}]
entregas = []       # [{"beneficiario", "fecha", "producto", "lote", "cantidad"}]

# Acumulados generales
acumulados = {"recibido": 0.0, "entregado": 0.0, "perdido": 0.0}

# Fecha actual del sistema (se pide al iniciar el programa)
sistema = {"hoy": ""}

# Tuplas con las opciones validas definidas por el programa
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORGANIZACION = ("Comedor Popular", "Albergue", "Olla Comun", "Asociacion", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades", "Cajas")

# Criterio del grupo: un lote esta "proximo a vencer" si le quedan 7 dias o menos
DIAS_ALERTA = 7


# ============================================================
# FUNCIONES AUXILIARES DE LECTURA Y VALIDACION
# ============================================================
def leerTexto(mensaje):
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: el campo no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto


def leerEntero(mensaje):
    while True:
        try:
            numero = int(input(mensaje))
            if numero > 0:
                return numero
            print("Error: el numero debe ser mayor que cero.")
        except ValueError:
            print("Error: debe ingresar un numero entero.")


def leerCantidad(mensaje):
    while True:
        try:
            cantidad = float(input(mensaje))
            if cantidad > 0:
                return cantidad
            print("Error: la cantidad debe ser mayor que cero.")
        except ValueError:
            print("Error: debe ingresar un numero.")


def elegirOpcion(opciones):
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    while True:
        try:
            opcion = int(input("Elija una opcion: "))
            if 1 <= opcion <= len(opciones):
                return opciones[opcion - 1]
            print(f"Error: elija un numero entre 1 y {len(opciones)}.")
        except ValueError:
            print("Error: debe ingresar un numero.")


def leerCodigoNuevo(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print(f"Error: el codigo {codigo} ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def leerCodigoExistente(diccionario, mensaje):
    """Pide un codigo que SI exista. Retorna "" si el diccionario esta vacio."""
    if len(diccionario) == 0:
        print("No hay registros disponibles.")
        return ""
    codigo = leerTexto(mensaje).upper()
    while codigo not in diccionario:
        print(f"Error: el codigo {codigo} no existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


# ------------------------------------------------------------
# FECHAS (formato AAAA-MM-DD)
# ------------------------------------------------------------
def diasDelMes(anio, mes):
    dias = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if mes == 2 and (anio % 4 == 0 and anio % 100 != 0 or anio % 400 == 0):
        return 29
    return dias[mes - 1]


def fechaValida(fecha):
    partes = fecha.split("-")
    if len(partes) != 3:
        return False
    if not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return False
    anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
    if anio < 2000 or mes < 1 or mes > 12:
        return False
    return 1 <= dia <= diasDelMes(anio, mes)


def leerFecha(mensaje):
    fecha = input(mensaje).strip()
    while not fechaValida(fecha):
        print("Error: fecha invalida. Use el formato AAAA-MM-DD (ejemplo 2026-09-29).")
        fecha = input(mensaje).strip()
    return fecha


def fechaADias(fecha):
    """Convierte una fecha AAAA-MM-DD en un numero de dias para poder restar fechas."""
    partes = fecha.split("-")
    anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
    total = 0
    for a in range(2000, anio):
        total += 366 if (a % 4 == 0 and a % 100 != 0 or a % 400 == 0) else 365
    for m in range(1, mes):
        total += diasDelMes(anio, m)
    return total + dia


def diasParaVencer(codigoLote):
    return fechaADias(lotes[codigoLote]["vencimiento"]) - fechaADias(sistema["hoy"])


def estadoLote(codigoLote):
    dias = diasParaVencer(codigoLote)
    if dias < 0:
        return "Vencido"
    if dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    return "Disponible"


# ============================================================
# 1. REGISTRAR / GESTIONAR DONANTES
# ============================================================
def registrarDonante():
    print("\n--- REGISTRAR DONANTE ---")
    codigo = leerCodigoNuevo(donantes, "Codigo del donante: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    print("Tipo de donante:")
    tipo = elegirOpcion(TIPOS_DONANTE)
    contacto = leerTexto("Contacto (telefono o correo): ")

    donantes[codigo] = {"nombre": nombre, "tipo": tipo, "contacto": contacto}
    print(f"Donante {codigo} registrado correctamente.")


def listarDonantes():
    print("\n--- LISTA DE DONANTES ---")
    if len(donantes) == 0:
        print("No hay donantes registrados.")
        return
    print(f"{'Codigo':8} {'Nombre':25} {'Tipo':10} {'Contacto':20}")
    print(f"{'-' * 66}")
    for codigo, datos in donantes.items():
        print(f"{codigo:8} {datos['nombre']:25} {datos['tipo']:10} {datos['contacto']:20}")


def editarDonante():
    print("\n--- EDITAR DONANTE ---")
    codigo = leerTexto("Codigo del donante a editar: ").upper()
    if codigo not in donantes:
        print(f"No existe un donante con codigo {codigo}.")
        return

    datos = donantes[codigo]
    print("Presione Enter para mantener el valor actual.")

    nombre = input(f"Nombre [{datos['nombre']}]: ").strip()
    if nombre != "":
        datos["nombre"] = nombre.title()

    cambiar = input(f"Tipo actual: {datos['tipo']}. Desea cambiarlo? (s/n): ").strip().lower()
    if cambiar == "s":
        datos["tipo"] = elegirOpcion(TIPOS_DONANTE)

    contacto = input(f"Contacto [{datos['contacto']}]: ").strip()
    if contacto != "":
        datos["contacto"] = contacto

    nuevoCodigo = input(f"Codigo [{codigo}]: ").strip().upper()
    if nuevoCodigo != "" and nuevoCodigo != codigo:
        if nuevoCodigo in donantes:
            print(f"Error: el codigo {nuevoCodigo} ya existe. Se mantiene {codigo}.")
        else:
            donantes[nuevoCodigo] = donantes.pop(codigo)
            # Actualizar las referencias en lotes y donaciones
            for datosLote in lotes.values():
                if datosLote["donante"] == codigo:
                    datosLote["donante"] = nuevoCodigo
            for donacion in donaciones:
                if donacion["donante"] == codigo:
                    donacion["donante"] = nuevoCodigo
            codigo = nuevoCodigo

    print(f"Donante {codigo} actualizado correctamente.")


def menuDonantes():
    while True:
        print("\n===== GESTION DE DONANTES =====")
        print("1. Registrar donante")
        print("2. Listar donantes")
        print("3. Editar donante")
        print("4. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrarDonante()
        elif opcion == "2":
            listarDonantes()
        elif opcion == "3":
            editarDonante()
        elif opcion == "4":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ============================================================
def registrarBeneficiario():
    print("\n--- REGISTRAR ORGANIZACION BENEFICIARIA ---")
    codigo = leerCodigoNuevo(beneficiarios, "Codigo de la organizacion: ")
    nombre = leerTexto("Nombre de la organizacion: ").title()
    print("Tipo de organizacion:")
    tipo = elegirOpcion(TIPOS_ORGANIZACION)
    personas = leerEntero("Cantidad estimada de personas atendidas: ")

    beneficiarios[codigo] = {"nombre": nombre, "tipo": tipo, "personas": personas}
    print(f"Organizacion {codigo} registrada correctamente.")


def listarBeneficiarios():
    print("\n--- LISTA DE ORGANIZACIONES BENEFICIARIAS ---")
    if len(beneficiarios) == 0:
        print("No hay organizaciones registradas.")
        return
    print(f"{'Codigo':8} {'Nombre':25} {'Tipo':16} {'Personas':>8}")
    print(f"{'-' * 60}")
    for codigo, datos in beneficiarios.items():
        print(f"{codigo:8} {datos['nombre']:25} {datos['tipo']:16} {datos['personas']:8,d}")


def editarBeneficiario():
    print("\n--- EDITAR ORGANIZACION BENEFICIARIA ---")
    codigo = leerTexto("Codigo de la organizacion a editar: ").upper()
    if codigo not in beneficiarios:
        print(f"No existe una organizacion con codigo {codigo}.")
        return

    datos = beneficiarios[codigo]
    print("Presione Enter para mantener el valor actual.")

    nombre = input(f"Nombre [{datos['nombre']}]: ").strip()
    if nombre != "":
        datos["nombre"] = nombre.title()

    cambiar = input(f"Tipo actual: {datos['tipo']}. Desea cambiarlo? (s/n): ").strip().lower()
    if cambiar == "s":
        datos["tipo"] = elegirOpcion(TIPOS_ORGANIZACION)

    cambiar = input(f"Personas atendidas: {datos['personas']}. Desea cambiarlo? (s/n): ").strip().lower()
    if cambiar == "s":
        datos["personas"] = leerEntero("Nueva cantidad de personas atendidas: ")

    nuevoCodigo = input(f"Codigo [{codigo}]: ").strip().upper()
    if nuevoCodigo != "" and nuevoCodigo != codigo:
        if nuevoCodigo in beneficiarios:
            print(f"Error: el codigo {nuevoCodigo} ya existe. Se mantiene {codigo}.")
        else:
            beneficiarios[nuevoCodigo] = beneficiarios.pop(codigo)
            # Actualizar las referencias en entregas
            for entrega in entregas:
                if entrega["beneficiario"] == codigo:
                    entrega["beneficiario"] = nuevoCodigo
            codigo = nuevoCodigo

    print(f"Organizacion {codigo} actualizada correctamente.")


def menuBeneficiarios():
    while True:
        print("\n===== GESTION DE BENEFICIARIOS =====")
        print("1. Registrar organizacion beneficiaria")
        print("2. Listar organizaciones beneficiarias")
        print("3. Editar organizacion beneficiaria")
        print("4. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrarBeneficiario()
        elif opcion == "2":
            listarBeneficiarios()
        elif opcion == "3":
            editarBeneficiario()
        elif opcion == "4":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# 3. REGISTRAR PRODUCTOS
# ============================================================
def registrarProducto():
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = leerCodigoNuevo(productos, "Codigo del producto: ")
    nombre = leerTexto("Nombre del producto: ").title()
    print("Categoria:")
    categoria = elegirOpcion(CATEGORIAS)
    print("Unidad de medida:")
    unidad = elegirOpcion(UNIDADES)

    productos[codigo] = {"nombre": nombre, "categoria": categoria, "unidad": unidad}
    print(f"Producto {codigo} registrado correctamente.")


def listarProductos():
    print("\n--- LISTA DE PRODUCTOS ---")
    if len(productos) == 0:
        print("No hay productos registrados.")
        return
    print(f"{'Codigo':8} {'Nombre':20} {'Categoria':16} {'Unidad':10}")
    print(f"{'-' * 57}")
    for codigo, datos in productos.items():
        print(f"{codigo:8} {datos['nombre']:20} {datos['categoria']:16} {datos['unidad']:10}")


def menuProductos():
    while True:
        print("\n===== PRODUCTOS =====")
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrarProducto()
        elif opcion == "2":
            listarProductos()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# 4. REGISTRAR DONACION Y LOTE
# ============================================================
def registrarDonacion():
    print("\n--- REGISTRAR DONACION Y LOTE ---")
    if len(donantes) == 0 or len(productos) == 0:
        print("Primero debe registrar al menos un donante y un producto.")
        return

    codDonante = leerCodigoExistente(donantes, "Codigo del donante: ")
    fecha = leerFecha("Fecha de la donacion (AAAA-MM-DD): ")
    codProducto = leerCodigoExistente(productos, "Codigo del producto: ")
    unidad = productos[codProducto]["unidad"]
    cantidad = leerCantidad(f"Cantidad recibida ({unidad}): ")

    vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")
    while fechaADias(vencimiento) < fechaADias(fecha):
        print("Error: el vencimiento no puede ser anterior a la fecha de donacion.")
        vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")

    # Codigo unico de lote generado automaticamente
    numero = len(lotes) + 1
    codLote = f"L{numero}"
    while codLote in lotes:
        numero += 1
        codLote = f"L{numero}"

    lotes[codLote] = {
        "producto": codProducto,
        "donante": codDonante,
        "recibido": cantidad,
        "disponible": cantidad,
        "perdido": 0.0,
        "vencimiento": vencimiento,
    }
    donaciones.append({"donante": codDonante, "fecha": fecha, "producto": codProducto,
                       "lote": codLote, "cantidad": cantidad})
    acumulados["recibido"] += cantidad

    print(f"Donacion registrada. Se creo el lote {codLote} con {cantidad:.2f} {unidad}.")
    print(f"Estado del lote: {estadoLote(codLote)}")


# ============================================================
# 5. REGISTRAR ENTREGA
# ============================================================
def registrarEntrega():
    print("\n--- REGISTRAR ENTREGA ---")
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero debe registrar al menos un beneficiario y una donacion.")
        return

    codBeneficiario = leerCodigoExistente(beneficiarios, "Codigo del beneficiario: ")
    fecha = leerFecha("Fecha de la entrega (AAAA-MM-DD): ")
    codProducto = leerCodigoExistente(productos, "Codigo del producto: ")

    # Lotes del producto con stock y que no esten vencidos en la fecha de entrega
    lotesValidos = []
    for codLote, datos in lotes.items():
        noVencido = fechaADias(datos["vencimiento"]) >= fechaADias(fecha)
        if datos["producto"] == codProducto and datos["disponible"] > 0 and noVencido:
            lotesValidos.append(codLote)

    if len(lotesValidos) == 0:
        print("No hay lotes disponibles (con stock y sin vencer) de ese producto.")
        return

    unidad = productos[codProducto]["unidad"]
    print(f"{'Lote':6} {'Disponible':>12} {'Vencimiento':>12}")
    for codLote in lotesValidos:
        print(f"{codLote:6} {lotes[codLote]['disponible']:12.2f} {lotes[codLote]['vencimiento']:>12}")

    codLote = leerTexto("Codigo del lote: ").upper()
    while codLote not in lotesValidos:
        print("Error: el lote no existe, no es de ese producto, no tiene stock o esta vencido.")
        codLote = leerTexto("Codigo del lote: ").upper()

    disponible = lotes[codLote]["disponible"]
    cantidad = leerCantidad(f"Cantidad a entregar ({unidad}): ")
    while cantidad > disponible:
        print(f"Error: solo hay {disponible:.2f} {unidad} disponibles en el lote {codLote}.")
        cantidad = leerCantidad(f"Cantidad a entregar ({unidad}): ")

    # Descontar automaticamente del stock
    lotes[codLote]["disponible"] -= cantidad
    entregas.append({"beneficiario": codBeneficiario, "fecha": fecha, "producto": codProducto,
                     "lote": codLote, "cantidad": cantidad})
    acumulados["entregado"] += cantidad
    print(f"Entrega registrada. Quedan {lotes[codLote]['disponible']:.2f} {unidad} en el lote {codLote}.")


def detalleEntregasBeneficiario():
    print("\n--- DETALLE DE ENTREGAS POR BENEFICIARIO ---")
    codBeneficiario = leerCodigoExistente(beneficiarios, "Codigo del beneficiario: ")
    if codBeneficiario == "":
        return

    print(f"Organizacion: {beneficiarios[codBeneficiario]['nombre']}")
    print(f"{'Fecha':12} {'Lote':6} {'Producto':20} {'Cantidad':>10} {'Unidad':8}")
    print(f"{'-' * 60}")
    encontrado = False
    for entrega in entregas:
        if entrega["beneficiario"] == codBeneficiario:
            producto = productos[entrega["producto"]]
            print(f"{entrega['fecha']:12} {entrega['lote']:6} {producto['nombre']:20} "
                  f"{entrega['cantidad']:10.2f} {producto['unidad']:8}")
            encontrado = True
    if not encontrado:
        print("Esta organizacion aun no ha recibido entregas.")


def menuEntregas():
    while True:
        print("\n===== ENTREGAS =====")
        print("1. Registrar entrega")
        print("2. Ver detalle de entregas por beneficiario")
        print("3. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrarEntrega()
        elif opcion == "2":
            detalleEntregasBeneficiario()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# 6. CONSULTAR STOCK Y VENCIMIENTOS
# ============================================================
def stockPorProducto():
    """Retorna un diccionario {codigoProducto: cantidad disponible (sin vencidos)}."""
    stock = {}
    for codLote, datos in lotes.items():
        if estadoLote(codLote) != "Vencido":
            stock[datos["producto"]] = stock.get(datos["producto"], 0) + datos["disponible"]
    return stock


def reporteStock():
    print(f"\n--- STOCK DISPONIBLE POR CATEGORIA Y PRODUCTO (al {sistema['hoy']}) ---")
    stock = stockPorProducto()
    if len(stock) == 0:
        print("No hay stock disponible.")
        return
    for categoria in CATEGORIAS:
        hayProductos = False
        for codProducto, cantidad in stock.items():
            producto = productos[codProducto]
            if producto["categoria"] == categoria:
                if not hayProductos:
                    print(f"\n{categoria.upper()}")
                    hayProductos = True
                print(f"  {codProducto:8} {producto['nombre']:20} {cantidad:10.2f} {producto['unidad']}")


def listarLotes():
    print(f"\n--- LOTES Y SU ESTADO (al {sistema['hoy']}) ---")
    if len(lotes) == 0:
        print("No hay lotes registrados.")
        return
    print(f"{'Lote':6} {'Producto':18} {'Disponible':>10} {'Vence':>11} {'Dias':>5}  {'Estado':16}")
    print(f"{'-' * 72}")
    for codLote, datos in lotes.items():
        nombre = productos[datos["producto"]]["nombre"]
        print(f"{codLote:6} {nombre:18} {datos['disponible']:10.2f} {datos['vencimiento']:>11} "
              f"{diasParaVencer(codLote):5d}  {estadoLote(codLote):16}")


def listarProximosAVencer():
    print(f"\n--- LOTES PROXIMOS A VENCER ({DIAS_ALERTA} dias o menos) ---")
    proximos = []
    for codLote, datos in lotes.items():
        if estadoLote(codLote) == "Proximo a vencer" and datos["disponible"] > 0:
            proximos.append(codLote)
    if len(proximos) == 0:
        print("No hay lotes proximos a vencer.")
        return

    proximos.sort(key=diasParaVencer)  # los que vencen antes van primero
    comprometido = 0
    print(f"{'Lote':6} {'Producto':18} {'Cantidad':>10} {'Unidad':8} {'Vence':>11} {'Dias':>5}")
    print(f"{'-' * 63}")
    for codLote in proximos:
        datos = lotes[codLote]
        producto = productos[datos["producto"]]
        print(f"{codLote:6} {producto['nombre']:18} {datos['disponible']:10.2f} {producto['unidad']:8} "
              f"{datos['vencimiento']:>11} {diasParaVencer(codLote):5d}")
        comprometido += datos["disponible"]
    print(f"Cantidad comprometida (en riesgo de perderse): {comprometido:,.2f}")


def registrarPerdidas():
    print("\n--- REGISTRAR PERDIDAS POR VENCIMIENTO ---")
    vencidos = []
    for codLote, datos in lotes.items():
        if estadoLote(codLote) == "Vencido" and datos["disponible"] > 0:
            vencidos.append(codLote)
    if len(vencidos) == 0:
        print("No hay lotes vencidos con cantidad remanente.")
        return

    for codLote in vencidos:
        datos = lotes[codLote]
        producto = productos[datos["producto"]]
        print(f"  {codLote}: {producto['nombre']} - {datos['disponible']:.2f} {producto['unidad']} "
              f"(vencio el {datos['vencimiento']})")

    confirmar = input("Registrar estas cantidades como perdida? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operacion cancelada.")
        return
    for codLote in vencidos:
        datos = lotes[codLote]
        datos["perdido"] += datos["disponible"]
        acumulados["perdido"] += datos["disponible"]
        datos["disponible"] = 0
    print(f"Se registraron {len(vencidos)} lote(s) como perdida.")


def cambiarFechaActual():
    print(f"Fecha actual del sistema: {sistema['hoy']}")
    sistema["hoy"] = leerFecha("Nueva fecha actual (AAAA-MM-DD): ")
    print("Fecha actualizada.")


def menuStock():
    while True:
        print(f"\n===== STOCK Y VENCIMIENTOS (hoy: {sistema['hoy']}) =====")
        print("1. Stock disponible por categoria y producto")
        print("2. Ver todos los lotes y su estado")
        print("3. Lotes proximos a vencer")
        print("4. Registrar perdidas por vencimiento")
        print("5. Cambiar fecha actual")
        print("6. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            reporteStock()
        elif opcion == "2":
            listarLotes()
        elif opcion == "3":
            listarProximosAVencer()
        elif opcion == "4":
            registrarPerdidas()
        elif opcion == "5":
            cambiarFechaActual()
        elif opcion == "6":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# 7. GENERAR REPORTES
# ============================================================
def ordenaPorCantidad(llaveValor):
    return llaveValor[1]


def rankingDonantes():
    print("\n--- RANKING DE DONANTES POR CANTIDAD DONADA ---")
    totales = {}
    for donacion in donaciones:
        totales[donacion["donante"]] = totales.get(donacion["donante"], 0) + donacion["cantidad"]
    if len(totales) == 0:
        print("No hay donaciones registradas.")
        return
    ranking = dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))
    print(f"{'Puesto':6} {'Codigo':8} {'Nombre':25} {'Total donado':>14}")
    print(f"{'-' * 56}")
    puesto = 1
    for codigo, total in ranking.items():
        print(f"{puesto:6d} {codigo:8} {donantes[codigo]['nombre']:25} {total:14,.2f}")
        puesto += 1


def totalPorBeneficiario():
    print("\n--- CANTIDAD TOTAL ENTREGADA POR ORGANIZACION ---")
    totales = {}
    for entrega in entregas:
        totales[entrega["beneficiario"]] = totales.get(entrega["beneficiario"], 0) + entrega["cantidad"]
    if len(totales) == 0:
        print("No hay entregas registradas.")
        return
    ordenado = dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))
    print(f"{'Codigo':8} {'Organizacion':25} {'Personas':>9} {'Total recibido':>15}")
    print(f"{'-' * 60}")
    for codigo, total in ordenado.items():
        datos = beneficiarios[codigo]
        print(f"{codigo:8} {datos['nombre']:25} {datos['personas']:9,d} {total:15,.2f}")


def indicadoresGenerales():
    print("\n--- ACUMULADOS, APROVECHAMIENTO Y DESPERDICIO ---")
    recibido = acumulados["recibido"]
    entregado = acumulados["entregado"]
    perdido = acumulados["perdido"]
    enStock = recibido - entregado - perdido
    print(f"{'Total recibido':30} {recibido:12,.2f}")
    print(f"{'Total entregado':30} {entregado:12,.2f}")
    print(f"{'Total perdido por vencimiento':30} {perdido:12,.2f}")
    print(f"{'Total aun en almacen':30} {enStock:12,.2f}")
    if recibido == 0:
        print("No hay donaciones para calcular porcentajes.")
        return
    print(f"{'Porcentaje de aprovechamiento':30} {entregado / recibido * 100:11.2f}%")
    print(f"{'Porcentaje de desperdicio':30} {perdido / recibido * 100:11.2f}%")


# Reporte adicional 1
def donacionesPorTipoDonante():
    print("\n--- REPORTE ADICIONAL: DONACIONES POR TIPO DE DONANTE ---")
    if len(donaciones) == 0:
        print("No hay donaciones registradas.")
        return
    totales = {}
    for donacion in donaciones:
        tipo = donantes[donacion["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + donacion["cantidad"]
    totalGeneral = sum(totales.values())
    print(f"{'Tipo':10} {'Cantidad':>12} {'Porcentaje':>11}")
    print(f"{'-' * 35}")
    for tipo in TIPOS_DONANTE:
        cantidad = totales.get(tipo, 0)
        print(f"{tipo:10} {cantidad:12,.2f} {cantidad / totalGeneral * 100:10.2f}%")


# Reporte adicional 2
def resumenPorProducto():
    print("\n--- REPORTE ADICIONAL: RECIBIDO, ENTREGADO Y PERDIDO POR PRODUCTO ---")
    if len(lotes) == 0:
        print("No hay lotes registrados.")
        return
    print(f"{'Producto':18} {'Unidad':8} {'Recibido':>10} {'Entregado':>10} {'Perdido':>9} {'Aprovech.':>10}")
    print(f"{'-' * 70}")
    for codProducto, producto in productos.items():
        recibido = 0
        perdido = 0
        for datos in lotes.values():
            if datos["producto"] == codProducto:
                recibido += datos["recibido"]
                perdido += datos["perdido"]
        if recibido == 0:
            continue
        entregado = 0
        for entrega in entregas:
            if entrega["producto"] == codProducto:
                entregado += entrega["cantidad"]
        print(f"{producto['nombre']:18} {producto['unidad']:8} {recibido:10.2f} {entregado:10.2f} "
              f"{perdido:9.2f} {entregado / recibido * 100:9.2f}%")


def menuReportes():
    while True:
        print("\n===== REPORTES =====")
        print("1. Stock disponible por categoria y producto")
        print("2. Lotes proximos a vencer y cantidad comprometida")
        print("3. Ranking de donantes")
        print("4. Cantidad total entregada por organizacion")
        print("5. Acumulados, % de aprovechamiento y % de desperdicio")
        print("6. Donaciones por tipo de donante (adicional)")
        print("7. Recibido / entregado / perdido por producto (adicional)")
        print("8. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            reporteStock()
        elif opcion == "2":
            listarProximosAVencer()
        elif opcion == "3":
            rankingDonantes()
        elif opcion == "4":
            totalPorBeneficiario()
        elif opcion == "5":
            indicadoresGenerales()
        elif opcion == "6":
            donacionesPorTipoDonante()
        elif opcion == "7":
            resumenPorProducto()
        elif opcion == "8":
            break
        else:
            print("Opcion no valida.")


# ============================================================
# MENU PRINCIPAL
# ============================================================
def menuPrincipal():
    print("=" * 55)
    print(f"{'SISTEMA DE GESTION DE BANCO DE ALIMENTOS':^55}")
    print("=" * 55)
    sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")

    while True:
        print(f"\n========== MENU PRINCIPAL (hoy: {sistema['hoy']}) ==========")
        print("1. Registrar / gestionar donantes")
        print("2. Registrar / gestionar beneficiarios")
        print("3. Registrar productos")
        print("4. Registrar donacion y lote")
        print("5. Registrar entrega")
        print("6. Consultar stock y vencimientos")
        print("7. Generar reportes")
        print("8. Salir")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            menuDonantes()
        elif opcion == "2":
            menuBeneficiarios()
        elif opcion == "3":
            menuProductos()
        elif opcion == "4":
            registrarDonacion()
        elif opcion == "5":
            menuEntregas()
        elif opcion == "6":
            menuStock()
        elif opcion == "7":
            menuReportes()
        elif opcion == "8":
            print("Gracias por usar el sistema. Hasta pronto!")
            break
        else:
            print("Opcion no valida.")


# Programa principal
menuPrincipal()
