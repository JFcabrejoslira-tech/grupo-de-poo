# CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
# Version basica (sin POO): funciones, listas, tuplas y diccionarios

# ---------------- DATOS ----------------
donantes = {}       # {codigo: {"nombre", "tipo", "contacto"}}
beneficiarios = {}  # {codigo: {"nombre", "tipo", "personas"}}
productos = {}      # {codigo: {"nombre", "categoria", "unidad"}}
lotes = {}          # {codigo: {"producto", "disponible", "perdido", "vence"}}
donaciones = []     # [{"donante", "fecha", "producto", "lote", "cantidad"}]
entregas = []       # [{"beneficiario", "fecha", "producto", "lote", "cantidad"}]
acumulados = {"recibido": 0, "entregado": 0, "perdido": 0}
sistema = {"hoy": ""}  # la fecha de hoy se pide la primera vez que se necesita

TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORGANIZACION = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7  # proximo a vencer = 7 dias o menos


# ---------------- LECTURA Y VALIDACION ----------------
def leerTexto(mensaje):
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto


def leerEntero(mensaje):
    texto = input(mensaje).strip()
    while not texto.isdigit() or int(texto) == 0:
        print("Error: ingrese un numero entero mayor que cero.")
        texto = input(mensaje).strip()
    return int(texto)


def leerCantidad(mensaje):
    while True:
        try:
            numero = float(input(mensaje))
        except ValueError:
            numero = 0
        if numero > 0:
            return numero
        print("Error: ingrese un numero mayor que cero.")


def elegir(titulo, opciones):
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    numero = leerEntero("Opcion: ")
    while numero > len(opciones):
        print("Error: opcion no valida.")
        numero = leerEntero("Opcion: ")
    return opciones[numero - 1]


def leerCodigoNuevo(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print("Error: ese codigo ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def leerCodigoExistente(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo not in diccionario:
        print("Error: ese codigo no existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


def mantener(campo, actual):
    texto = input(f"{campo} [{actual}]: ").strip()
    if texto == "":
        return actual
    return texto


# ---------------- FECHAS (AAAA-MM-DD) ----------------
def fechaValida(fecha):
    partes = fecha.split("-")
    if len(partes) != 3 or not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return False
    mes, dia = int(partes[1]), int(partes[2])
    diasMes = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return 1 <= mes <= 12 and 1 <= dia <= diasMes[mes - 1]


def leerFecha(mensaje):
    fecha = input(mensaje).strip()
    while not fechaValida(fecha):
        print("Error: use el formato AAAA-MM-DD (ejemplo 2026-09-29).")
        fecha = input(mensaje).strip()
    return fecha


def aDias(fecha):
    """Convierte una fecha en numero de dias para poder restar fechas."""
    partes = fecha.split("-")
    anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
    diasAntes = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    if mes <= 2:
        anio -= 1  # el 29 de febrero se cuenta desde marzo
    return int(partes[0]) * 365 + anio // 4 - anio // 100 + anio // 400 + diasAntes[mes - 1] + dia


def fechaHoy():
    if sistema["hoy"] == "":
        sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
    return sistema["hoy"]


def diasParaVencer(lote):
    return aDias(lotes[lote]["vence"]) - aDias(fechaHoy())


def estado(lote):
    dias = diasParaVencer(lote)
    if dias < 0:
        return "Vencido"
    elif dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    return "Disponible"


# ---------------- 1. DONANTES ----------------
def registrarDonante():
    codigo = leerCodigoNuevo(donantes, "Codigo: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    tipo = elegir("Tipo de donante:", TIPOS_DONANTE)
    contacto = leerTexto("Contacto: ")
    donantes[codigo] = {"nombre": nombre, "tipo": tipo, "contacto": contacto}
    print("Donante registrado.")


def listarDonantes():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':10}Contacto")
    for codigo, d in donantes.items():
        print(f"{codigo:8}{d['nombre']:25}{d['tipo']:10}{d['contacto']}")


def editarDonante():
    if len(donantes) == 0:
        print("No hay donantes registrados.")
        return
    codigo = leerCodigoExistente(donantes, "Codigo del donante a editar: ")
    d = donantes[codigo]
    print("Presione Enter para mantener el valor actual.")
    d["nombre"] = mantener("Nombre", d["nombre"]).title()
    d["contacto"] = mantener("Contacto", d["contacto"])
    if input(f"Cambiar tipo ({d['tipo']})? (s/n): ").lower() == "s":
        d["tipo"] = elegir("Nuevo tipo:", TIPOS_DONANTE)
    nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
    if nuevo in donantes and nuevo != codigo:
        print("Error: ese codigo ya existe, se mantiene el anterior.")
    elif nuevo != "":
        donantes[nuevo] = donantes.pop(codigo)
        for donacion in donaciones:
            if donacion["donante"] == codigo:
                donacion["donante"] = nuevo
    print("Donante actualizado.")


# ---------------- 2. BENEFICIARIOS ----------------
def registrarBeneficiario():
    codigo = leerCodigoNuevo(beneficiarios, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    tipo = elegir("Tipo de organizacion:", TIPOS_ORGANIZACION)
    personas = leerEntero("Personas atendidas: ")
    beneficiarios[codigo] = {"nombre": nombre, "tipo": tipo, "personas": personas}
    print("Beneficiario registrado.")


def listarBeneficiarios():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':18}Personas")
    for codigo, b in beneficiarios.items():
        print(f"{codigo:8}{b['nombre']:25}{b['tipo']:18}{b['personas']}")


def editarBeneficiario():
    if len(beneficiarios) == 0:
        print("No hay beneficiarios registrados.")
        return
    codigo = leerCodigoExistente(beneficiarios, "Codigo del beneficiario a editar: ")
    b = beneficiarios[codigo]
    print("Presione Enter para mantener el valor actual.")
    b["nombre"] = mantener("Nombre", b["nombre"]).title()
    if input(f"Cambiar tipo ({b['tipo']})? (s/n): ").lower() == "s":
        b["tipo"] = elegir("Nuevo tipo:", TIPOS_ORGANIZACION)
    if input(f"Cambiar personas ({b['personas']})? (s/n): ").lower() == "s":
        b["personas"] = leerEntero("Personas atendidas: ")
    nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
    if nuevo in beneficiarios and nuevo != codigo:
        print("Error: ese codigo ya existe, se mantiene el anterior.")
    elif nuevo != "":
        beneficiarios[nuevo] = beneficiarios.pop(codigo)
        for entrega in entregas:
            if entrega["beneficiario"] == codigo:
                entrega["beneficiario"] = nuevo
    print("Beneficiario actualizado.")


# ---------------- 3. PRODUCTOS ----------------
def registrarProducto():
    codigo = leerCodigoNuevo(productos, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    categoria = elegir("Categoria:", CATEGORIAS)
    unidad = elegir("Unidad de medida:", UNIDADES)
    productos[codigo] = {"nombre": nombre, "categoria": categoria, "unidad": unidad}
    print("Producto registrado.")


def listarProductos():
    print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
    for codigo, p in productos.items():
        print(f"{codigo:8}{p['nombre']:20}{p['categoria']:16}{p['unidad']}")


# ---------------- 4. DONACION Y LOTE ----------------
def registrarDonacion():
    if len(donantes) == 0 or len(productos) == 0:
        print("Primero registre un donante y un producto.")
        return
    donante = leerCodigoExistente(donantes, "Codigo del donante: ")
    fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
    producto = leerCodigoExistente(productos, "Codigo del producto: ")
    cantidad = leerCantidad(f"Cantidad recibida ({productos[producto]['unidad']}): ")
    vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
    while aDias(vence) < aDias(fecha):
        print("Error: el vencimiento no puede ser antes de la donacion.")
        vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")

    lote = f"L{len(lotes) + 1}"  # codigo unico de lote: L1, L2, L3...
    lotes[lote] = {"producto": producto, "disponible": cantidad, "perdido": 0, "vence": vence}
    donaciones.append({"donante": donante, "fecha": fecha, "producto": producto,
                       "lote": lote, "cantidad": cantidad})
    acumulados["recibido"] += cantidad
    print(f"Lote {lote} registrado. Estado: {estado(lote)}")


# ---------------- 5. ENTREGAS ----------------
def registrarEntrega():
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero registre un beneficiario y una donacion.")
        return
    beneficiario = leerCodigoExistente(beneficiarios, "Codigo del beneficiario: ")
    fecha = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
    producto = leerCodigoExistente(productos, "Codigo del producto: ")

    validos = []  # lotes del producto, con stock y sin vencer
    for lote, d in lotes.items():
        if d["producto"] == producto and d["disponible"] > 0 and aDias(d["vence"]) >= aDias(fecha):
            validos.append(lote)
            print(f"  {lote}: {d['disponible']:.2f} disponibles, vence {d['vence']}")
    if len(validos) == 0:
        print("No hay lotes con stock y sin vencer de ese producto.")
        return

    lote = leerTexto("Codigo del lote: ").upper()
    while lote not in validos:
        print("Error: lote no valido, sin stock o vencido.")
        lote = leerTexto("Codigo del lote: ").upper()
    cantidad = leerCantidad("Cantidad a entregar: ")
    while cantidad > lotes[lote]["disponible"]:
        print(f"Error: solo hay {lotes[lote]['disponible']:.2f} disponibles.")
        cantidad = leerCantidad("Cantidad a entregar: ")

    lotes[lote]["disponible"] -= cantidad  # se descuenta del stock
    entregas.append({"beneficiario": beneficiario, "fecha": fecha, "producto": producto,
                     "lote": lote, "cantidad": cantidad})
    acumulados["entregado"] += cantidad
    print("Entrega registrada.")


def detalleEntregas():
    if len(beneficiarios) == 0:
        print("No hay beneficiarios registrados.")
        return
    codigo = leerCodigoExistente(beneficiarios, "Codigo del beneficiario: ")
    for e in entregas:
        if e["beneficiario"] == codigo:
            print(f"{e['fecha']:12}{e['lote']:6}{productos[e['producto']]['nombre']:20}{e['cantidad']:10.2f}")


# ---------------- 6. STOCK Y VENCIMIENTOS ----------------
def reporteStock():
    print(f"{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
    for categoria in CATEGORIAS:
        for codigo, p in productos.items():
            if p["categoria"] == categoria:
                stock = 0
                for lote, d in lotes.items():
                    if d["producto"] == codigo and estado(lote) != "Vencido":
                        stock += d["disponible"]
                print(f"{categoria:16}{p['nombre']:20}{stock:10.2f}  {p['unidad']}")


def imprimirLote(lote):
    d = lotes[lote]
    print(f"{lote:6}{productos[d['producto']]['nombre']:20}{d['disponible']:10.2f}  "
          f"{d['vence']:12}{estado(lote)}")


def listarLotes():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    for lote in lotes:
        imprimirLote(lote)


def lotesProximos():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    comprometido = 0
    for lote, d in lotes.items():
        if estado(lote) == "Proximo a vencer" and d["disponible"] > 0:
            imprimirLote(lote)
            comprometido += d["disponible"]
    print(f"Cantidad comprometida: {comprometido:.2f}")


def registrarPerdidas():
    total = 0
    for lote, d in lotes.items():
        if estado(lote) == "Vencido" and d["disponible"] > 0:
            print(f"Lote {lote}: se pierden {d['disponible']:.2f}")
            total += d["disponible"]
            d["perdido"] += d["disponible"]
            d["disponible"] = 0
    acumulados["perdido"] += total
    print(f"Total registrado como perdida: {total:.2f}")


# ---------------- 7. REPORTES ----------------
def ordenaPorCantidad(llaveValor):
    return llaveValor[1]


def sumarPor(lista, campo):
    """Suma las cantidades de la lista agrupando por campo, de mayor a menor."""
    totales = {}
    for registro in lista:
        totales[registro[campo]] = totales.get(registro[campo], 0) + registro["cantidad"]
    return dict(sorted(totales.items(), key=ordenaPorCantidad, reverse=True))


def rankingDonantes():
    puesto = 1
    for codigo, total in sumarPor(donaciones, "donante").items():
        print(f"{puesto}. {donantes[codigo]['nombre']:25}{total:10.2f}")
        puesto += 1


def totalPorBeneficiario():
    for codigo, total in sumarPor(entregas, "beneficiario").items():
        print(f"{beneficiarios[codigo]['nombre']:25}{total:10.2f}")


def aprovechamientoYPerdidas():
    recibido = acumulados["recibido"]
    if recibido == 0:
        print("No hay donaciones registradas.")
        return
    print(f"Recibido:  {recibido:10.2f}")
    print(f"Entregado: {acumulados['entregado']:10.2f}  ({acumulados['entregado'] / recibido * 100:.2f}% aprovechado)")
    print(f"Perdido:   {acumulados['perdido']:10.2f}  ({acumulados['perdido'] / recibido * 100:.2f}% desperdiciado)")


def donacionesPorTipo():  # reporte adicional 1
    totales = {}
    for d in donaciones:
        tipo = donantes[d["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + d["cantidad"]
    for tipo, total in totales.items():
        print(f"{tipo:10}{total:10.2f}")


def resumenPorProducto():  # reporte adicional 2
    entregado = sumarPor(entregas, "producto")
    print(f"{'Producto':20}{'Recibido':>10}{'Entregado':>10}{'Perdido':>10}")
    for codigo, recibido in sumarPor(donaciones, "producto").items():
        perdido = 0
        for d in lotes.values():
            if d["producto"] == codigo:
                perdido += d["perdido"]
        print(f"{productos[codigo]['nombre']:20}{recibido:10.2f}{entregado.get(codigo, 0):10.2f}{perdido:10.2f}")


# ---------------- MENUS ----------------
def menuDonantes():
    while True:
        opcion = input("\n--- DONANTES ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
        if opcion == "1":
            registrarDonante()
        elif opcion == "2":
            listarDonantes()
        elif opcion == "3":
            editarDonante()
        elif opcion == "4":
            break


def menuBeneficiarios():
    while True:
        opcion = input("\n--- BENEFICIARIOS ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
        if opcion == "1":
            registrarBeneficiario()
        elif opcion == "2":
            listarBeneficiarios()
        elif opcion == "3":
            editarBeneficiario()
        elif opcion == "4":
            break


def menuProductos():
    while True:
        opcion = input("\n--- PRODUCTOS ---\n1. Registrar\n2. Listar\n3. Volver\nOpcion: ")
        if opcion == "1":
            registrarProducto()
        elif opcion == "2":
            listarProductos()
        elif opcion == "3":
            break


def menuEntregas():
    while True:
        opcion = input("\n--- ENTREGAS ---\n1. Registrar entrega\n2. Detalle por beneficiario\n3. Volver\nOpcion: ")
        if opcion == "1":
            registrarEntrega()
        elif opcion == "2":
            detalleEntregas()
        elif opcion == "3":
            break


def menuStock():
    while True:
        opcion = input("\n--- STOCK Y VENCIMIENTOS ---\n1. Stock por categoria y producto\n2. Lotes y su estado\n"
                       "3. Lotes proximos a vencer\n4. Registrar perdidas por vencimiento\n5. Volver\nOpcion: ")
        if opcion == "1":
            reporteStock()
        elif opcion == "2":
            listarLotes()
        elif opcion == "3":
            lotesProximos()
        elif opcion == "4":
            registrarPerdidas()
        elif opcion == "5":
            break


def menuReportes():
    while True:
        opcion = input("\n--- REPORTES ---\n1. Stock por categoria y producto\n2. Lotes proximos a vencer\n"
                       "3. Ranking de donantes\n4. Total entregado por beneficiario\n"
                       "5. Aprovechamiento y perdidas\n6. Donaciones por tipo de donante\n"
                       "7. Resumen por producto\n8. Volver\nOpcion: ")
        if opcion == "1":
            reporteStock()
        elif opcion == "2":
            lotesProximos()
        elif opcion == "3":
            rankingDonantes()
        elif opcion == "4":
            totalPorBeneficiario()
        elif opcion == "5":
            aprovechamientoYPerdidas()
        elif opcion == "6":
            donacionesPorTipo()
        elif opcion == "7":
            resumenPorProducto()
        elif opcion == "8":
            break


def menuPrincipal():
    while True:
        opcion = input("\n===== BANCO DE ALIMENTOS =====\n1. Registrar / gestionar donantes\n"
                       "2. Registrar / gestionar beneficiarios\n3. Registrar productos\n"
                       "4. Registrar donacion y lote\n5. Registrar entrega\n"
                       "6. Consultar stock y vencimientos\n7. Generar reportes\n8. Salir\nOpcion: ")
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
            print("Hasta pronto!")
            break


menuPrincipal()
