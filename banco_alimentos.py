# ============================================================
# CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
# Version basica (sin POO): funciones, listas, tuplas y diccionarios
# ============================================================

# ------------------------------------------------------------
# DATOS DEL SISTEMA (se guardan en memoria)
# ------------------------------------------------------------
# Diccionarios: la llave es el codigo, asi no se pueden repetir codigos
donantes = {}       # {codigo: {"nombre", "tipo", "contacto"}}
beneficiarios = {}  # {codigo: {"nombre", "tipo", "personas"}}
productos = {}      # {codigo: {"nombre", "categoria", "unidad"}}
lotes = {}          # {codigoLote: {"producto", "donante", "recibido", "disponible", "perdido", "vencimiento"}}

# Listas: historial de movimientos
donaciones = []     # cada elemento: {"donante", "fecha", "producto", "lote", "cantidad"}
entregas = []       # cada elemento: {"beneficiario", "fecha", "producto", "lote", "cantidad"}

# Totales acumulados del sistema
acumulados = {"recibido": 0.0, "entregado": 0.0, "perdido": 0.0}

# Fecha de hoy: empieza vacia y se pide la primera vez que se necesita
sistema = {"hoy": ""}

# Tuplas con las opciones validas
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORGANIZACION = ("Comedor Popular", "Albergue", "Olla Comun", "Asociacion", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades", "Cajas")

# Criterio del grupo: un lote esta "proximo a vencer" si le quedan 7 dias o menos
DIAS_ALERTA = 7


# ------------------------------------------------------------
# FUNCIONES PARA LEER Y VALIDAR DATOS
# ------------------------------------------------------------
def leerTexto(mensaje):
    """Pide un texto y no acepta que este vacio."""
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: el campo no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto


def leerEntero(mensaje):
    """Pide un numero entero mayor que cero."""
    while True:
        try:
            numero = int(input(mensaje))
            if numero > 0:
                return numero
            print("Error: debe ser mayor que cero.")
        except ValueError:
            print("Error: debe ingresar un numero entero.")


def leerDecimal(mensaje):
    """Pide una cantidad (puede tener decimales) mayor que cero."""
    while True:
        try:
            numero = float(input(mensaje))
            if numero > 0:
                return numero
            print("Error: debe ser mayor que cero.")
        except ValueError:
            print("Error: debe ingresar un numero.")


def elegirOpcion(titulo, opciones):
    """Muestra las opciones de una tupla numeradas y retorna la elegida."""
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    opcion = input("Elija una opcion: ").strip()
    while not (opcion.isdigit() and 1 <= int(opcion) <= len(opciones)):
        print(f"Error: elija un numero entre 1 y {len(opciones)}.")
        opcion = input("Elija una opcion: ").strip()
    return opciones[int(opcion) - 1]


def leerCodigoNuevo(diccionario, mensaje):
    """Pide un codigo que NO exista todavia (para registrar)."""
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print(f"Error: el codigo {codigo} ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def leerCodigoExistente(diccionario, mensaje):
    """Pide un codigo que SI exista (para usarlo en donaciones y entregas)."""
    codigo = leerTexto(mensaje).upper()
    while codigo not in diccionario:
        print(f"Error: el codigo {codigo} no existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def leerCodigoEditado(diccionario, codigoActual):
    """Al editar: pide el nuevo codigo. Enter o un codigo repetido mantienen el actual."""
    nuevo = input(f"Codigo [{codigoActual}]: ").strip().upper()
    if nuevo == "" or nuevo == codigoActual:
        return codigoActual
    if nuevo in diccionario:
        print(f"Error: el codigo {nuevo} ya existe. Se mantiene {codigoActual}.")
        return codigoActual
    return nuevo


def mantener(campo, valorActual):
    """Al editar: si se presiona Enter se mantiene el valor actual."""
    texto = input(f"{campo} [{valorActual}]: ").strip()
    if texto == "":
        return valorActual
    return texto


def confirmar(mensaje):
    """Retorna True si el usuario responde 's'."""
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta == "s"


# ------------------------------------------------------------
# FUNCIONES DE FECHAS (formato AAAA-MM-DD)
# ------------------------------------------------------------
def esBisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or anio % 400 == 0


def diasDelMes(anio, mes):
    diasPorMes = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if mes == 2 and esBisiesto(anio):
        return 29
    return diasPorMes[mes - 1]


def fechaValida(fecha):
    """Revisa que la fecha tenga el formato AAAA-MM-DD y que exista."""
    partes = fecha.split("-")
    if len(partes) != 3:
        return False
    if not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return False
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
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
    """Convierte una fecha en la cantidad de dias contados desde el anio 2000.
    Asi se pueden restar dos fechas para saber cuantos dias hay entre ellas."""
    partes = fecha.split("-")
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])

    total = dia
    for a in range(2000, anio):       # sumar los dias de los anios completos
        if esBisiesto(a):
            total += 366
        else:
            total += 365
    for m in range(1, mes):           # sumar los dias de los meses completos
        total += diasDelMes(anio, m)
    return total


def fechaHoy():
    """Pide la fecha de hoy solo la primera vez que se necesita."""
    if sistema["hoy"] == "":
        sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
    return sistema["hoy"]


def diasParaVencer(codLote):
    """Dias que faltan para que venza el lote (negativo si ya vencio)."""
    return fechaADias(lotes[codLote]["vencimiento"]) - fechaADias(fechaHoy())


def estadoLote(codLote):
    dias = diasParaVencer(codLote)
    if dias < 0:
        return "Vencido"
    elif dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    else:
        return "Disponible"


# ============================================================
# 1. REGISTRAR / GESTIONAR DONANTES
# ============================================================
def registrarDonante():
    print("\n--- REGISTRAR DONANTE ---")
    codigo = leerCodigoNuevo(donantes, "Codigo del donante: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    tipo = elegirOpcion("Tipo de donante:", TIPOS_DONANTE)
    contacto = leerTexto("Contacto (telefono o correo): ")

    donantes[codigo] = {"nombre": nombre, "tipo": tipo, "contacto": contacto}
    print(f"Donante {codigo} registrado correctamente.")


def listarDonantes():
    print("\n--- LISTA DE DONANTES ---")
    print(f"{'Codigo':8} {'Nombre':25} {'Tipo':10} {'Contacto':20}")
    for codigo, datos in donantes.items():
        print(f"{codigo:8} {datos['nombre']:25} {datos['tipo']:10} {datos['contacto']:20}")
    print(f"Total de donantes: {len(donantes)}")


def editarDonante():
    print("\n--- EDITAR DONANTE ---")
    codigo = input("Codigo del donante a editar: ").strip().upper()
    if codigo not in donantes:
        print("No existe ese donante.")
        return

    datos = donantes[codigo]
    print("Presione Enter para mantener el valor actual.")
    datos["nombre"] = mantener("Nombre", datos["nombre"]).title()
    if confirmar(f"Tipo actual: {datos['tipo']}. Desea cambiarlo?"):
        datos["tipo"] = elegirOpcion("Nuevo tipo:", TIPOS_DONANTE)
    datos["contacto"] = mantener("Contacto", datos["contacto"])

    nuevoCodigo = leerCodigoEditado(donantes, codigo)
    if nuevoCodigo != codigo:
        donantes[nuevoCodigo] = donantes.pop(codigo)   # cambiar la llave del diccionario
        for donacion in donaciones:                    # actualizar el codigo en el historial
            if donacion["donante"] == codigo:
                donacion["donante"] = nuevoCodigo
        for datosLote in lotes.values():               # y en los lotes
            if datosLote["donante"] == codigo:
                datosLote["donante"] = nuevoCodigo
    print(f"Donante {nuevoCodigo} actualizado correctamente.")


# ============================================================
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ============================================================
def registrarBeneficiario():
    print("\n--- REGISTRAR ORGANIZACION BENEFICIARIA ---")
    codigo = leerCodigoNuevo(beneficiarios, "Codigo de la organizacion: ")
    nombre = leerTexto("Nombre de la organizacion: ").title()
    tipo = elegirOpcion("Tipo de organizacion:", TIPOS_ORGANIZACION)
    personas = leerEntero("Cantidad estimada de personas atendidas: ")

    beneficiarios[codigo] = {"nombre": nombre, "tipo": tipo, "personas": personas}
    print(f"Organizacion {codigo} registrada correctamente.")


def listarBeneficiarios():
    print("\n--- LISTA DE ORGANIZACIONES BENEFICIARIAS ---")
    print(f"{'Codigo':8} {'Nombre':25} {'Tipo':16} {'Personas':>8}")
    for codigo, datos in beneficiarios.items():
        print(f"{codigo:8} {datos['nombre']:25} {datos['tipo']:16} {datos['personas']:8,d}")
    print(f"Total de organizaciones: {len(beneficiarios)}")


def editarBeneficiario():
    print("\n--- EDITAR ORGANIZACION BENEFICIARIA ---")
    codigo = input("Codigo de la organizacion a editar: ").strip().upper()
    if codigo not in beneficiarios:
        print("No existe esa organizacion.")
        return

    datos = beneficiarios[codigo]
    print("Presione Enter para mantener el valor actual.")
    datos["nombre"] = mantener("Nombre", datos["nombre"]).title()
    if confirmar(f"Tipo actual: {datos['tipo']}. Desea cambiarlo?"):
        datos["tipo"] = elegirOpcion("Nuevo tipo:", TIPOS_ORGANIZACION)
    if confirmar(f"Personas atendidas: {datos['personas']}. Desea cambiarlo?"):
        datos["personas"] = leerEntero("Nueva cantidad de personas: ")

    nuevoCodigo = leerCodigoEditado(beneficiarios, codigo)
    if nuevoCodigo != codigo:
        beneficiarios[nuevoCodigo] = beneficiarios.pop(codigo)  # cambiar la llave
        for entrega in entregas:                                # actualizar el historial
            if entrega["beneficiario"] == codigo:
                entrega["beneficiario"] = nuevoCodigo
    print(f"Organizacion {nuevoCodigo} actualizada correctamente.")


# ============================================================
# 3. REGISTRAR PRODUCTOS
# ============================================================
def registrarProducto():
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = leerCodigoNuevo(productos, "Codigo del producto: ")
    nombre = leerTexto("Nombre del producto: ").title()
    categoria = elegirOpcion("Categoria:", CATEGORIAS)
    unidad = elegirOpcion("Unidad de medida:", UNIDADES)

    productos[codigo] = {"nombre": nombre, "categoria": categoria, "unidad": unidad}
    print(f"Producto {codigo} registrado correctamente.")


def listarProductos():
    print("\n--- LISTA DE PRODUCTOS ---")
    print(f"{'Codigo':8} {'Nombre':20} {'Categoria':16} {'Unidad':10}")
    for codigo, datos in productos.items():
        print(f"{codigo:8} {datos['nombre']:20} {datos['categoria']:16} {datos['unidad']:10}")
    print(f"Total de productos: {len(productos)}")


# ============================================================
# 4. REGISTRAR DONACION Y LOTE
# ============================================================
def registrarDonacion():
    print("\n--- REGISTRAR DONACION Y LOTE ---")
    if len(donantes) == 0 or len(productos) == 0:
        print("Primero registre al menos un donante y un producto.")
        return

    codDonante = leerCodigoExistente(donantes, "Codigo del donante: ")
    fecha = leerFecha("Fecha de la donacion (AAAA-MM-DD): ")
    codProducto = leerCodigoExistente(productos, "Codigo del producto: ")
    unidad = productos[codProducto]["unidad"]
    cantidad = leerDecimal(f"Cantidad recibida ({unidad}): ")
    vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")
    while fechaADias(vencimiento) < fechaADias(fecha):
        print("Error: el vencimiento no puede ser anterior a la fecha de donacion.")
        vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")

    # Codigo unico del lote: L1, L2, L3... (los lotes nunca se eliminan)
    codLote = f"L{len(lotes) + 1}"

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
    print(f"Lote {codLote} creado con {cantidad:.2f} {unidad}. Estado: {estadoLote(codLote)}")


# ============================================================
# 5. REGISTRAR ENTREGA
# ============================================================
def registrarEntrega():
    print("\n--- REGISTRAR ENTREGA ---")
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero registre al menos un beneficiario y una donacion.")
        return

    codBenef = leerCodigoExistente(beneficiarios, "Codigo del beneficiario: ")
    fecha = leerFecha("Fecha de la entrega (AAAA-MM-DD): ")
    codProducto = leerCodigoExistente(productos, "Codigo del producto: ")
    unidad = productos[codProducto]["unidad"]

    # Buscar los lotes de ese producto que tienen stock y no estan vencidos
    lotesValidos = []
    print("Lotes disponibles:")
    for codLote, datos in lotes.items():
        esDelProducto = datos["producto"] == codProducto
        tieneStock = datos["disponible"] > 0
        noVencido = fechaADias(datos["vencimiento"]) >= fechaADias(fecha)
        if esDelProducto and tieneStock and noVencido:
            lotesValidos.append(codLote)
            print(f"  {codLote}: {datos['disponible']:.2f} {unidad}, vence {datos['vencimiento']}")

    if len(lotesValidos) == 0:
        print("No hay lotes con stock y sin vencer de ese producto.")
        return

    codLote = leerTexto("Codigo del lote: ").upper()
    while codLote not in lotesValidos:
        print("Error: lote invalido, sin stock o vencido.")
        codLote = leerTexto("Codigo del lote: ").upper()

    disponible = lotes[codLote]["disponible"]
    cantidad = leerDecimal(f"Cantidad a entregar ({unidad}): ")
    while cantidad > disponible:
        print(f"Error: solo hay {disponible:.2f} {unidad} en el lote {codLote}.")
        cantidad = leerDecimal(f"Cantidad a entregar ({unidad}): ")

    lotes[codLote]["disponible"] -= cantidad   # descontar del stock automaticamente
    entregas.append({"beneficiario": codBenef, "fecha": fecha, "producto": codProducto,
                     "lote": codLote, "cantidad": cantidad})
    acumulados["entregado"] += cantidad
    print(f"Entrega registrada. Quedan {lotes[codLote]['disponible']:.2f} {unidad} en el lote {codLote}.")


def detalleEntregas():
    print("\n--- DETALLE DE ENTREGAS POR BENEFICIARIO ---")
    codBenef = input("Codigo del beneficiario: ").strip().upper()
    if codBenef not in beneficiarios:
        print("No existe ese beneficiario.")
        return

    print(f"Entregas a {beneficiarios[codBenef]['nombre']}:")
    total = 0
    for entrega in entregas:
        if entrega["beneficiario"] == codBenef:
            producto = productos[entrega["producto"]]
            print(f"  {entrega['fecha']:12} {entrega['lote']:6} {producto['nombre']:20} "
                  f"{entrega['cantidad']:10.2f} {producto['unidad']}")
            total += entrega["cantidad"]
    print(f"Total entregado: {total:,.2f}")


# ============================================================
# 6. CONSULTAR STOCK Y VENCIMIENTOS
# ============================================================
def imprimirEncabezadoLotes():
    print(f"{'Lote':6} {'Producto':18} {'Disponible':>10} {'Unidad':8} {'Vence':>11} {'Dias':>5}  Estado")


def imprimirLote(codLote):
    datos = lotes[codLote]
    producto = productos[datos["producto"]]
    print(f"{codLote:6} {producto['nombre']:18} {datos['disponible']:10.2f} {producto['unidad']:8} "
          f"{datos['vencimiento']:>11} {diasParaVencer(codLote):5d}  {estadoLote(codLote)}")


def lotesConEstado(estado):
    """Retorna una lista con los lotes que tienen stock y el estado indicado.
    La lista se ordena por dias para vencer (los mas urgentes primero)."""
    resultado = []
    for codLote, datos in lotes.items():
        if estadoLote(codLote) == estado and datos["disponible"] > 0:
            resultado.append(codLote)
    resultado.sort(key=diasParaVencer)
    return resultado


def reporteStock():
    print(f"\n--- STOCK DISPONIBLE POR CATEGORIA Y PRODUCTO (al {fechaHoy()}) ---")

    # Sumar el stock de cada producto (sin contar lotes vencidos)
    stock = {}
    for codLote, datos in lotes.items():
        if estadoLote(codLote) != "Vencido":
            codProducto = datos["producto"]
            stock[codProducto] = stock.get(codProducto, 0) + datos["disponible"]

    # Mostrar agrupado por categoria
    print(f"{'Categoria':16} {'Producto':20} {'Cantidad':>10} Unidad")
    for categoria in CATEGORIAS:
        for codProducto, cantidad in stock.items():
            producto = productos[codProducto]
            if producto["categoria"] == categoria and cantidad > 0:
                print(f"{categoria:16} {producto['nombre']:20} {cantidad:10.2f} {producto['unidad']}")


def listarLotes():
    print(f"\n--- LOTES Y SU ESTADO (al {fechaHoy()}) ---")
    imprimirEncabezadoLotes()
    for codLote in lotes:
        imprimirLote(codLote)


def listarProximosAVencer():
    print(f"\n--- LOTES PROXIMOS A VENCER ({DIAS_ALERTA} dias o menos) ---")
    imprimirEncabezadoLotes()
    comprometido = 0
    for codLote in lotesConEstado("Proximo a vencer"):
        imprimirLote(codLote)
        comprometido += lotes[codLote]["disponible"]
    print(f"Cantidad comprometida (en riesgo de perderse): {comprometido:,.2f}")


def registrarPerdidas():
    print("\n--- REGISTRAR PERDIDAS POR VENCIMIENTO ---")
    vencidos = lotesConEstado("Vencido")
    if len(vencidos) == 0:
        print("No hay lotes vencidos con cantidad remanente.")
        return

    imprimirEncabezadoLotes()
    for codLote in vencidos:
        imprimirLote(codLote)

    if confirmar("Registrar estas cantidades como perdida?"):
        for codLote in vencidos:
            remanente = lotes[codLote]["disponible"]
            lotes[codLote]["perdido"] += remanente
            lotes[codLote]["disponible"] = 0
            acumulados["perdido"] += remanente
        print(f"Se registraron {len(vencidos)} lote(s) como perdida.")


def cambiarFechaActual():
    sistema["hoy"] = leerFecha(f"Nueva fecha actual [{sistema['hoy']}] (AAAA-MM-DD): ")
    print("Fecha actualizada.")


# ============================================================
# 7. GENERAR REPORTES
# ============================================================
def ordenaPorCantidad(llaveValor):
    """Se usa en sorted(): ordena los pares (llave, valor) por el valor."""
    return llaveValor[1]


def sumarCantidades(registros, campo):
    """Suma las cantidades de una lista (donaciones o entregas) agrupando por un campo.
    Ejemplo: sumarCantidades(donaciones, "donante") -> {"D1": 120.0, "D2": 50.0}"""
    totales = {}
    for registro in registros:
        llave = registro[campo]
        totales[llave] = totales.get(llave, 0) + registro["cantidad"]
    return totales


def rankingDonantes():
    print("\n--- RANKING DE DONANTES POR CANTIDAD DONADA ---")
    totales = sumarCantidades(donaciones, "donante")
    ranking = dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))
    puesto = 1
    for codigo, total in ranking.items():
        print(f"{puesto:3d}. {codigo:8} {donantes[codigo]['nombre']:25} {total:12,.2f}")
        puesto += 1


def totalPorBeneficiario():
    print("\n--- CANTIDAD TOTAL ENTREGADA POR ORGANIZACION ---")
    totales = sumarCantidades(entregas, "beneficiario")
    ordenado = dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))
    for codigo, total in ordenado.items():
        datos = beneficiarios[codigo]
        print(f"{codigo:8} {datos['nombre']:25} {datos['personas']:6,d} personas {total:12,.2f}")


def indicadoresGenerales():
    print("\n--- ACUMULADOS, APROVECHAMIENTO Y DESPERDICIO ---")
    recibido = acumulados["recibido"]
    entregado = acumulados["entregado"]
    perdido = acumulados["perdido"]
    enAlmacen = recibido - entregado - perdido

    print(f"{'Total recibido':30} {recibido:12,.2f}")
    print(f"{'Total entregado':30} {entregado:12,.2f}")
    print(f"{'Total perdido por vencimiento':30} {perdido:12,.2f}")
    print(f"{'Total aun en almacen':30} {enAlmacen:12,.2f}")
    if recibido > 0:
        print(f"{'Porcentaje de aprovechamiento':30} {entregado / recibido * 100:11.2f}%")
        print(f"{'Porcentaje de desperdicio':30} {perdido / recibido * 100:11.2f}%")


def donacionesPorTipoDonante():  # reporte adicional 1
    print("\n--- DONACIONES POR TIPO DE DONANTE ---")
    if acumulados["recibido"] == 0:
        print("No hay donaciones registradas.")
        return

    totales = {}
    for donacion in donaciones:
        tipo = donantes[donacion["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + donacion["cantidad"]

    for tipo in TIPOS_DONANTE:
        cantidad = totales.get(tipo, 0)
        porcentaje = cantidad / acumulados["recibido"] * 100
        print(f"{tipo:10} {cantidad:12,.2f} {porcentaje:9.2f}%")


def resumenPorProducto():  # reporte adicional 2
    print("\n--- RECIBIDO, ENTREGADO Y PERDIDO POR PRODUCTO ---")
    entregadoPorProducto = sumarCantidades(entregas, "producto")
    print(f"{'Producto':18} {'Unidad':8} {'Recibido':>10} {'Entregado':>10} {'Perdido':>9} {'Aprovech.':>10}")

    for codProducto, producto in productos.items():
        recibido = 0
        perdido = 0
        for datosLote in lotes.values():
            if datosLote["producto"] == codProducto:
                recibido += datosLote["recibido"]
                perdido += datosLote["perdido"]
        if recibido > 0:
            entregado = entregadoPorProducto.get(codProducto, 0)
            aprovechamiento = entregado / recibido * 100
            print(f"{producto['nombre']:18} {producto['unidad']:8} {recibido:10.2f} "
                  f"{entregado:10.2f} {perdido:9.2f} {aprovechamiento:9.2f}%")


# ============================================================
# MENUS
# ============================================================
def menuDonantes():
    while True:
        print("\n===== DONANTES =====")
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


def menuBeneficiarios():
    while True:
        print("\n===== BENEFICIARIOS =====")
        print("1. Registrar organizacion")
        print("2. Listar organizaciones")
        print("3. Editar organizacion")
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


def menuEntregas():
    while True:
        print("\n===== ENTREGAS =====")
        print("1. Registrar entrega")
        print("2. Detalle de entregas por beneficiario")
        print("3. Volver")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrarEntrega()
        elif opcion == "2":
            detalleEntregas()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")


def menuStock():
    while True:
        print("\n===== STOCK Y VENCIMIENTOS =====")
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


def menuPrincipal():
    print(f"{'SISTEMA DE GESTION DE BANCO DE ALIMENTOS':^50}")
    while True:
        print("\n===== MENU PRINCIPAL =====")
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
