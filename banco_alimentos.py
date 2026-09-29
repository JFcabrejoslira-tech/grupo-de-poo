# ============================================================
# CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
# Version basica (sin POO): funciones, listas, tuplas y diccionarios
# ============================================================

# Diccionarios: la llave es el codigo (las llaves son unicas)
donantes = {}       # {codigo: {"nombre", "tipo", "contacto"}}
beneficiarios = {}  # {codigo: {"nombre", "tipo", "personas"}}
productos = {}      # {codigo: {"nombre", "categoria", "unidad"}}
lotes = {}          # {codLote: {"producto", "donante", "recibido", "disponible", "perdido", "vencimiento"}}
donaciones = []     # [{"donante", "fecha", "producto", "lote", "cantidad"}]
entregas = []       # [{"beneficiario", "fecha", "producto", "lote", "cantidad"}]
acumulados = {"recibido": 0.0, "entregado": 0.0, "perdido": 0.0}
sistema = {"hoy": ""}  # fecha actual, se pide al iniciar el programa

TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORGANIZACION = ("Comedor Popular", "Albergue", "Olla Comun", "Asociacion", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades", "Cajas")
DIAS_ALERTA = 7  # criterio del grupo: "proximo a vencer" = 7 dias o menos


# ------------------------------------------------------------
# LECTURA Y VALIDACION DE DATOS
# ------------------------------------------------------------
def leerTexto(mensaje):
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: el campo no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto


def leerNumero(mensaje, tipo):
    """tipo es int o float. Solo acepta numeros mayores que cero."""
    while True:
        try:
            numero = tipo(input(mensaje))
            if numero > 0:
                return numero
            print("Error: debe ser mayor que cero.")
        except ValueError:
            print("Error: numero invalido.")


def elegirOpcion(titulo, opciones):
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    opcion = input("Elija una opcion: ").strip()
    while not (opcion.isdigit() and 1 <= int(opcion) <= len(opciones)):
        print(f"Error: elija un numero entre 1 y {len(opciones)}.")
        opcion = input("Elija una opcion: ").strip()
    return opciones[int(opcion) - 1]


def leerCodigo(diccionario, mensaje, debeExistir):
    codigo = leerTexto(mensaje).upper()
    while (codigo in diccionario) != debeExistir:
        if debeExistir:
            print(f"Error: el codigo {codigo} no existe.")
        else:
            print(f"Error: el codigo {codigo} ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def mantener(campo, actual):
    """Para editar: si se presiona Enter se mantiene el valor actual."""
    texto = input(f"{campo} [{actual}]: ").strip()
    if texto == "":
        return actual
    return texto


def confirmar(mensaje):
    return input(f"{mensaje} (s/n): ").strip().lower() == "s"


def cambiarCodigo(diccionario, codigo, registros, campo):
    """Cambia la llave de un registro sin repetir codigos y actualiza los registros que la usan."""
    nuevo = input(f"Codigo [{codigo}]: ").strip().upper()
    if nuevo == "" or nuevo == codigo:
        return codigo
    if nuevo in diccionario:
        print(f"Error: el codigo {nuevo} ya existe. Se mantiene {codigo}.")
        return codigo
    diccionario[nuevo] = diccionario.pop(codigo)
    for registro in registros:
        if registro[campo] == codigo:
            registro[campo] = nuevo
    return nuevo


def menu(titulo, opciones, textoSalir):
    """opciones es una lista de tuplas (texto, funcion que se ejecuta al elegirla)."""
    while True:
        print(f"\n===== {titulo} =====")
        for i in range(len(opciones)):
            print(f"{i + 1}. {opciones[i][0]}")
        print(f"{len(opciones) + 1}. {textoSalir}")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == str(len(opciones) + 1):
            return
        if opcion.isdigit() and 1 <= int(opcion) <= len(opciones):
            opciones[int(opcion) - 1][1]()
        else:
            print("Opcion no valida.")


# ------------------------------------------------------------
# FECHAS (formato AAAA-MM-DD)
# ------------------------------------------------------------
def esBisiesto(anio):
    return anio % 4 == 0 and anio % 100 != 0 or anio % 400 == 0


def diasDelMes(anio, mes):
    if mes == 2 and esBisiesto(anio):
        return 29
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[mes - 1]


def leerFecha(mensaje):
    while True:
        partes = input(mensaje).strip().split("-")
        if len(partes) == 3 and partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit():
            anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
            if anio >= 2000 and 1 <= mes <= 12 and 1 <= dia <= diasDelMes(anio, mes):
                return "-".join(partes)
        print("Error: fecha invalida. Use el formato AAAA-MM-DD (ejemplo 2026-09-29).")


def fechaADias(fecha):
    """Convierte AAAA-MM-DD en un numero de dias para poder restar fechas."""
    anio, mes, dia = map(int, fecha.split("-"))
    total = dia
    for a in range(2000, anio):
        total += 365
        if esBisiesto(a):
            total += 1
    for m in range(1, mes):
        total += diasDelMes(anio, m)
    return total


def diasParaVencer(codLote):
    return fechaADias(lotes[codLote]["vencimiento"]) - fechaADias(sistema["hoy"])


def estadoLote(codLote):
    dias = diasParaVencer(codLote)
    if dias < 0:
        return "Vencido"
    if dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    return "Disponible"


# ============================================================
# 1. REGISTRAR / GESTIONAR DONANTES
# ============================================================
def registrarDonante():
    codigo = leerCodigo(donantes, "Codigo del donante: ", False)
    donantes[codigo] = {"nombre": leerTexto("Nombre o razon social: ").title(),
                        "tipo": elegirOpcion("Tipo de donante:", TIPOS_DONANTE),
                        "contacto": leerTexto("Contacto (telefono o correo): ")}
    print(f"Donante {codigo} registrado correctamente.")


def listarDonantes():
    print(f"\n{'Codigo':8} {'Nombre':25} {'Tipo':10} {'Contacto':20}")
    for codigo, d in donantes.items():
        print(f"{codigo:8} {d['nombre']:25} {d['tipo']:10} {d['contacto']:20}")
    print(f"Total de donantes: {len(donantes)}")


def editarDonante():
    codigo = input("Codigo del donante a editar: ").strip().upper()
    if codigo not in donantes:
        print("No existe ese donante.")
        return
    d = donantes[codigo]
    print("Presione Enter para mantener el valor actual.")
    d["nombre"] = mantener("Nombre", d["nombre"]).title()
    if confirmar(f"Tipo actual: {d['tipo']}. Desea cambiarlo?"):
        d["tipo"] = elegirOpcion("Nuevo tipo:", TIPOS_DONANTE)
    d["contacto"] = mantener("Contacto", d["contacto"])
    codigo = cambiarCodigo(donantes, codigo, donaciones + list(lotes.values()), "donante")
    print(f"Donante {codigo} actualizado correctamente.")


# ============================================================
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ============================================================
def registrarBeneficiario():
    codigo = leerCodigo(beneficiarios, "Codigo de la organizacion: ", False)
    beneficiarios[codigo] = {"nombre": leerTexto("Nombre de la organizacion: ").title(),
                             "tipo": elegirOpcion("Tipo de organizacion:", TIPOS_ORGANIZACION),
                             "personas": leerNumero("Personas atendidas (estimado): ", int)}
    print(f"Organizacion {codigo} registrada correctamente.")


def listarBeneficiarios():
    print(f"\n{'Codigo':8} {'Nombre':25} {'Tipo':16} {'Personas':>8}")
    for codigo, b in beneficiarios.items():
        print(f"{codigo:8} {b['nombre']:25} {b['tipo']:16} {b['personas']:8,d}")
    print(f"Total de organizaciones: {len(beneficiarios)}")


def editarBeneficiario():
    codigo = input("Codigo de la organizacion a editar: ").strip().upper()
    if codigo not in beneficiarios:
        print("No existe esa organizacion.")
        return
    b = beneficiarios[codigo]
    print("Presione Enter para mantener el valor actual.")
    b["nombre"] = mantener("Nombre", b["nombre"]).title()
    if confirmar(f"Tipo actual: {b['tipo']}. Desea cambiarlo?"):
        b["tipo"] = elegirOpcion("Nuevo tipo:", TIPOS_ORGANIZACION)
    if confirmar(f"Personas atendidas: {b['personas']}. Desea cambiarlo?"):
        b["personas"] = leerNumero("Nueva cantidad de personas: ", int)
    codigo = cambiarCodigo(beneficiarios, codigo, entregas, "beneficiario")
    print(f"Organizacion {codigo} actualizada correctamente.")


# ============================================================
# 3. REGISTRAR PRODUCTOS
# ============================================================
def registrarProducto():
    codigo = leerCodigo(productos, "Codigo del producto: ", False)
    productos[codigo] = {"nombre": leerTexto("Nombre del producto: ").title(),
                         "categoria": elegirOpcion("Categoria:", CATEGORIAS),
                         "unidad": elegirOpcion("Unidad de medida:", UNIDADES)}
    print(f"Producto {codigo} registrado correctamente.")


def listarProductos():
    print(f"\n{'Codigo':8} {'Nombre':20} {'Categoria':16} {'Unidad':10}")
    for codigo, p in productos.items():
        print(f"{codigo:8} {p['nombre']:20} {p['categoria']:16} {p['unidad']:10}")
    print(f"Total de productos: {len(productos)}")


# ============================================================
# 4. REGISTRAR DONACION Y LOTE
# ============================================================
def registrarDonacion():
    if len(donantes) == 0 or len(productos) == 0:
        print("Primero registre al menos un donante y un producto.")
        return
    codDonante = leerCodigo(donantes, "Codigo del donante: ", True)
    fecha = leerFecha("Fecha de la donacion (AAAA-MM-DD): ")
    codProducto = leerCodigo(productos, "Codigo del producto: ", True)
    unidad = productos[codProducto]["unidad"]
    cantidad = leerNumero(f"Cantidad recibida ({unidad}): ", float)
    vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")
    while fechaADias(vencimiento) < fechaADias(fecha):
        print("Error: el vencimiento no puede ser anterior a la fecha de donacion.")
        vencimiento = leerFecha("Fecha de vencimiento del lote (AAAA-MM-DD): ")

    codLote = f"L{len(lotes) + 1}"  # los lotes nunca se eliminan, asi que el codigo es unico
    lotes[codLote] = {"producto": codProducto, "donante": codDonante, "recibido": cantidad,
                      "disponible": cantidad, "perdido": 0.0, "vencimiento": vencimiento}
    donaciones.append({"donante": codDonante, "fecha": fecha, "producto": codProducto,
                       "lote": codLote, "cantidad": cantidad})
    acumulados["recibido"] += cantidad
    print(f"Lote {codLote} creado con {cantidad:.2f} {unidad}. Estado: {estadoLote(codLote)}")


# ============================================================
# 5. REGISTRAR ENTREGA
# ============================================================
def registrarEntrega():
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero registre al menos un beneficiario y una donacion.")
        return
    codBenef = leerCodigo(beneficiarios, "Codigo del beneficiario: ", True)
    fecha = leerFecha("Fecha de la entrega (AAAA-MM-DD): ")
    codProducto = leerCodigo(productos, "Codigo del producto: ", True)
    unidad = productos[codProducto]["unidad"]

    # Solo se muestran lotes del producto, con stock y sin vencer en la fecha de entrega
    validos = []
    for codLote, datos in lotes.items():
        if (datos["producto"] == codProducto and datos["disponible"] > 0
                and fechaADias(datos["vencimiento"]) >= fechaADias(fecha)):
            validos.append(codLote)
            print(f"  {codLote}: {datos['disponible']:.2f} {unidad}, vence {datos['vencimiento']}")
    if len(validos) == 0:
        print("No hay lotes con stock y sin vencer de ese producto.")
        return

    codLote = leerTexto("Codigo del lote: ").upper()
    while codLote not in validos:
        print("Error: lote invalido, sin stock o vencido.")
        codLote = leerTexto("Codigo del lote: ").upper()
    cantidad = leerNumero(f"Cantidad a entregar ({unidad}): ", float)
    while cantidad > lotes[codLote]["disponible"]:
        print(f"Error: solo hay {lotes[codLote]['disponible']:.2f} {unidad} en el lote {codLote}.")
        cantidad = leerNumero(f"Cantidad a entregar ({unidad}): ", float)

    lotes[codLote]["disponible"] -= cantidad  # se descuenta automaticamente del stock
    entregas.append({"beneficiario": codBenef, "fecha": fecha, "producto": codProducto,
                     "lote": codLote, "cantidad": cantidad})
    acumulados["entregado"] += cantidad
    print(f"Entrega registrada. Quedan {lotes[codLote]['disponible']:.2f} {unidad} en el lote {codLote}.")


def detalleEntregas():
    codBenef = input("Codigo del beneficiario: ").strip().upper()
    if codBenef not in beneficiarios:
        print("No existe ese beneficiario.")
        return
    print(f"Entregas a {beneficiarios[codBenef]['nombre']}:")
    total = 0
    for e in entregas:
        if e["beneficiario"] == codBenef:
            p = productos[e["producto"]]
            print(f"  {e['fecha']:12} {e['lote']:6} {p['nombre']:20} {e['cantidad']:10.2f} {p['unidad']}")
            total += e["cantidad"]
    print(f"Total entregado: {total:,.2f}")


# ============================================================
# 6. CONSULTAR STOCK Y VENCIMIENTOS
# ============================================================
ENCABEZADO_LOTES = f"{'Lote':6} {'Producto':18} {'Disponible':>10} {'Unidad':8} {'Vence':>11} {'Dias':>5}  Estado"


def imprimirLote(codLote):
    datos = lotes[codLote]
    p = productos[datos["producto"]]
    print(f"{codLote:6} {p['nombre']:18} {datos['disponible']:10.2f} {p['unidad']:8} "
          f"{datos['vencimiento']:>11} {diasParaVencer(codLote):5d}  {estadoLote(codLote)}")


def lotesConEstado(estado):
    """Lotes con stock en el estado indicado, ordenados: los que vencen antes van primero."""
    resultado = []
    for codLote, datos in lotes.items():
        if estadoLote(codLote) == estado and datos["disponible"] > 0:
            resultado.append(codLote)
    resultado.sort(key=diasParaVencer)
    return resultado


def reporteStock():
    print(f"\n--- STOCK DISPONIBLE POR CATEGORIA Y PRODUCTO (al {sistema['hoy']}) ---")
    stock = {}
    for codLote, datos in lotes.items():
        if estadoLote(codLote) != "Vencido" and datos["disponible"] > 0:
            stock[datos["producto"]] = stock.get(datos["producto"], 0) + datos["disponible"]
    print(f"{'Categoria':16} {'Producto':20} {'Cantidad':>10} Unidad")
    for categoria in CATEGORIAS:
        for codProducto, cantidad in stock.items():
            p = productos[codProducto]
            if p["categoria"] == categoria:
                print(f"{categoria:16} {p['nombre']:20} {cantidad:10.2f} {p['unidad']}")


def listarLotes():
    print(f"\n--- LOTES Y SU ESTADO (al {sistema['hoy']}) ---")
    print(ENCABEZADO_LOTES)
    for codLote in lotes:
        imprimirLote(codLote)


def listarProximosAVencer():
    print(f"\n--- LOTES PROXIMOS A VENCER ({DIAS_ALERTA} dias o menos) ---")
    print(ENCABEZADO_LOTES)
    comprometido = 0
    for codLote in lotesConEstado("Proximo a vencer"):
        imprimirLote(codLote)
        comprometido += lotes[codLote]["disponible"]
    print(f"Cantidad comprometida (en riesgo de perderse): {comprometido:,.2f}")


def registrarPerdidas():
    vencidos = lotesConEstado("Vencido")
    if len(vencidos) == 0:
        print("No hay lotes vencidos con cantidad remanente.")
        return
    print(ENCABEZADO_LOTES)
    for codLote in vencidos:
        imprimirLote(codLote)
    if confirmar("Registrar estas cantidades como perdida?"):
        for codLote in vencidos:
            datos = lotes[codLote]
            datos["perdido"] += datos["disponible"]
            acumulados["perdido"] += datos["disponible"]
            datos["disponible"] = 0
        print(f"Se registraron {len(vencidos)} lote(s) como perdida.")


def cambiarFechaActual():
    sistema["hoy"] = leerFecha(f"Nueva fecha actual [{sistema['hoy']}] (AAAA-MM-DD): ")


# ============================================================
# 7. GENERAR REPORTES
# ============================================================
def ordenaPorCantidad(llaveValor):
    return llaveValor[1]


def totalizar(registros, campoLlave, campoValor):
    """Suma campoValor agrupando por campoLlave. Retorna un diccionario de mayor a menor."""
    totales = {}
    for r in registros:
        totales[r[campoLlave]] = totales.get(r[campoLlave], 0) + r[campoValor]
    return dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))


def rankingDonantes():
    print("\n--- RANKING DE DONANTES POR CANTIDAD DONADA ---")
    puesto = 1
    for codigo, total in totalizar(donaciones, "donante", "cantidad").items():
        print(f"{puesto:3d}. {codigo:8} {donantes[codigo]['nombre']:25} {total:12,.2f}")
        puesto += 1


def totalPorBeneficiario():
    print("\n--- CANTIDAD TOTAL ENTREGADA POR ORGANIZACION ---")
    for codigo, total in totalizar(entregas, "beneficiario", "cantidad").items():
        b = beneficiarios[codigo]
        print(f"{codigo:8} {b['nombre']:25} {b['personas']:6,d} personas {total:12,.2f}")


def indicadoresGenerales():
    print("\n--- ACUMULADOS, APROVECHAMIENTO Y DESPERDICIO ---")
    recibido, entregado, perdido = acumulados["recibido"], acumulados["entregado"], acumulados["perdido"]
    print(f"{'Total recibido':30} {recibido:12,.2f}")
    print(f"{'Total entregado':30} {entregado:12,.2f}")
    print(f"{'Total perdido por vencimiento':30} {perdido:12,.2f}")
    print(f"{'Total aun en almacen':30} {recibido - entregado - perdido:12,.2f}")
    if recibido > 0:
        print(f"{'Porcentaje de aprovechamiento':30} {entregado / recibido * 100:11.2f}%")
        print(f"{'Porcentaje de desperdicio':30} {perdido / recibido * 100:11.2f}%")


def donacionesPorTipoDonante():  # reporte adicional 1
    print("\n--- DONACIONES POR TIPO DE DONANTE ---")
    if acumulados["recibido"] == 0:
        print("No hay donaciones registradas.")
        return
    totales = {}
    for d in donaciones:
        tipo = donantes[d["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + d["cantidad"]
    for tipo in TIPOS_DONANTE:
        cantidad = totales.get(tipo, 0)
        print(f"{tipo:10} {cantidad:12,.2f} {cantidad / acumulados['recibido'] * 100:9.2f}%")


def resumenPorProducto():  # reporte adicional 2
    print("\n--- RECIBIDO, ENTREGADO Y PERDIDO POR PRODUCTO ---")
    recibido = totalizar(lotes.values(), "producto", "recibido")
    perdido = totalizar(lotes.values(), "producto", "perdido")
    entregado = totalizar(entregas, "producto", "cantidad")
    print(f"{'Producto':18} {'Unidad':8} {'Recibido':>10} {'Entregado':>10} {'Perdido':>9} {'Aprovech.':>10}")
    for codProducto, cantRecibida in recibido.items():
        p = productos[codProducto]
        cantEntregada = entregado.get(codProducto, 0)
        print(f"{p['nombre']:18} {p['unidad']:8} {cantRecibida:10.2f} {cantEntregada:10.2f} "
              f"{perdido[codProducto]:9.2f} {cantEntregada / cantRecibida * 100:9.2f}%")


# ============================================================
# MENUS
# ============================================================
def menuDonantes():
    menu("DONANTES", [("Registrar donante", registrarDonante), ("Listar donantes", listarDonantes),
                      ("Editar donante", editarDonante)], "Volver")


def menuBeneficiarios():
    menu("BENEFICIARIOS", [("Registrar organizacion", registrarBeneficiario),
                           ("Listar organizaciones", listarBeneficiarios),
                           ("Editar organizacion", editarBeneficiario)], "Volver")


def menuProductos():
    menu("PRODUCTOS", [("Registrar producto", registrarProducto),
                       ("Listar productos", listarProductos)], "Volver")


def menuEntregas():
    menu("ENTREGAS", [("Registrar entrega", registrarEntrega),
                      ("Detalle de entregas por beneficiario", detalleEntregas)], "Volver")


def menuStock():
    menu("STOCK Y VENCIMIENTOS", [("Stock disponible por categoria y producto", reporteStock),
                                  ("Ver todos los lotes y su estado", listarLotes),
                                  ("Lotes proximos a vencer", listarProximosAVencer),
                                  ("Registrar perdidas por vencimiento", registrarPerdidas),
                                  ("Cambiar fecha actual", cambiarFechaActual)], "Volver")


def menuReportes():
    menu("REPORTES", [("Stock disponible por categoria y producto", reporteStock),
                      ("Lotes proximos a vencer y cantidad comprometida", listarProximosAVencer),
                      ("Ranking de donantes", rankingDonantes),
                      ("Cantidad total entregada por organizacion", totalPorBeneficiario),
                      ("Acumulados, % de aprovechamiento y % de desperdicio", indicadoresGenerales),
                      ("Donaciones por tipo de donante (adicional)", donacionesPorTipoDonante),
                      ("Recibido / entregado / perdido por producto (adicional)", resumenPorProducto)],
         "Volver")


# Programa principal
print(f"{'SISTEMA DE GESTION DE BANCO DE ALIMENTOS':^50}")
sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
menu("MENU PRINCIPAL", [("Registrar / gestionar donantes", menuDonantes),
                        ("Registrar / gestionar beneficiarios", menuBeneficiarios),
                        ("Registrar productos", menuProductos),
                        ("Registrar donacion y lote", registrarDonacion),
                        ("Registrar entrega", menuEntregas),
                        ("Consultar stock y vencimientos", menuStock),
                        ("Generar reportes", menuReportes)], "Salir")
print("Gracias por usar el sistema. Hasta pronto!")
