donantes = {}
beneficiarios = {}
productos = {}
lotes = {}
donaciones = []
entregas = []
acumulados = {"recibido": 0, "entregado": 0, "perdido": 0}
sistema = {"hoy": ""}

TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORG = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7

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
            if numero > 0:
                return numero
            print("Error: ingrese un numero mayor que cero.")
        except ValueError:
            print("Error: ingrese un numero valido.")

def elegir(titulo, opciones):
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    numero = leerEntero("Opcion: ")
    while numero > len(opciones):
        print("Error: opcion no valida.")
        numero = leerEntero("Opcion: ")
    return opciones[numero - 1]

def leerCodNuevo(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print("Error: ese codigo ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo

def leerCodExist(diccionario, mensaje):
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

def fechaValida(fecha):
    partes = fecha.split("-")
    if len(partes) != 3 or not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return False
    mes, dia = int(partes[1]), int(partes[2])
    dias_mes = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return 1 <= mes <= 12 and 1 <= dia <= dias_mes[mes - 1]

def leerFecha(mensaje):
    fecha = input(mensaje).strip()
    while not fechaValida(fecha):
        print("Error: use el formato AAAA-MM-DD (ejemplo 2026-09-29).")
        fecha = input(mensaje).strip()
    return fecha

def aDias(fecha):
    partes = fecha.split("-")
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
    diasAntes = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    return anio * 365 + diasAntes[mes - 1] + dia

def fHoy():
    if sistema["hoy"] == "":
        sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
    return sistema["hoy"]

def dVencer(lote):
    return aDias(lotes[lote]["vence"]) - aDias(fHoy())

def estLote(lote):
    dias = dVencer(lote)
    if dias < 0:
        return "Vencido"
    elif dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    return "Disponible"

def impLote(lote):
    d = lotes[lote]
    p_nom = productos[d["producto"]]["nombre"]
    print(f"{lote:6}{p_nom:20}{d['disponible']:10.2f}  {d['vence']:12}{estLote(lote)}")

def regDonante():
    codigo = leerCodNuevo(donantes, "Codigo: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    tipo = elegir("Tipo de donante:", TIPOS_DONANTE)
    contacto = leerTexto("Contacto: ")
    donantes[codigo] = {"nombre": nombre, "tipo": tipo, "contacto": contacto}
    print("Donante registrado.")

def listDonantes():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':10}Contacto")
    for codigo, d in donantes.items():
        print(f"{codigo:8}{d['nombre']:25}{d['tipo']:10}{d['contacto']}")

def editDonante():
    if len(donantes) == 0:
        print("No hay donantes registrados.")
        return
    codigo = leerCodExist(donantes, "Codigo del donante a editar: ")
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

def regBenef():
    codigo = leerCodNuevo(beneficiarios, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    tipo = elegir("Tipo de organizacion:", TIPOS_ORG)
    personas = leerEntero("Personas atendidas: ")
    beneficiarios[codigo] = {"nombre": nombre, "tipo": tipo, "personas": personas}
    print("Beneficiario registrado.")

def listBenef():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':18}Personas")
    for codigo, b in beneficiarios.items():
        print(f"{codigo:8}{b['nombre']:25}{b['tipo']:18}{b['personas']}")

def editBenef():
    if len(beneficiarios) == 0:
        print("No hay beneficiarios registrados.")
        return
    codigo = leerCodExist(beneficiarios, "Codigo del beneficiario a editar: ")
    b = beneficiarios[codigo]
    print("Presione Enter para mantener el valor actual.")
    b["nombre"] = mantener("Nombre", b["nombre"]).title()
    if input(f"Cambiar tipo ({b['tipo']})? (s/n): ").lower() == "s":
        b["tipo"] = elegir("Nuevo tipo:", TIPOS_ORG)
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

def regProd():
    codigo = leerCodNuevo(productos, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    categoria = elegir("Categoria:", CATEGORIAS)
    unidad = elegir("Unidad de medida:", UNIDADES)
    productos[codigo] = {"nombre": nombre, "categoria": categoria, "unidad": unidad}
    print("Producto registrado.")

def listProd():
    print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
    for codigo, p in productos.items():
        print(f"{codigo:8}{p['nombre']:20}{p['categoria']:16}{p['unidad']}")

def regDonacion():
    if len(donantes) == 0 or len(productos) == 0:
        print("Primero registre un donante y un producto.")
        return
    donante = leerCodExist(donantes, "Codigo del donante: ")
    fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
    producto = leerCodExist(productos, "Codigo del producto: ")
    cantidad = leerCantidad(f"Cantidad recibida ({productos[producto]['unidad']}): ")
    vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
    while aDias(vence) < aDias(fecha):
        print("Error: el vencimiento no puede ser antes de la donacion.")
        vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")

    lote = f"L{len(lotes) + 1}"
    lotes[lote] = {"producto": producto, "disponible": cantidad, "perdido": 0, "vence": vence}
    donaciones.append({"donante": donante, "fecha": fecha, "producto": producto,
                       "lote": lote, "cantidad": cantidad})
    acumulados["recibido"] += cantidad
    print(f"Lote {lote} registrado. Estado: {estLote(lote)}")

def regiEntr():
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero registre un beneficiario y una donacion.")
        return
    cod_ben = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
    f_entr = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
    cod_prod = leerCodExist(productos, "Codigo del producto: ")

    validos = []
    for lote, d in lotes.items():
        if d["producto"] == cod_prod and d["disponible"] > 0 and aDias(d["vence"]) >= aDias(f_entr):
            validos.append(lote)
            print(f"  {lote}: {d['disponible']:.2f} disponibles, vence {d['vence']}")
    if len(validos) == 0:
        print("No hay lotes con stock y sin vencer de ese producto.")
        return

    cod_lote = leerTexto("Codigo del lote: ").upper()
    while cod_lote not in validos:
        print("Error: lote no valido, sin stock o vencido.")
        cod_lote = leerTexto("Codigo del lote: ").upper()
    cant = leerCantidad("Cantidad a entregar: ")
    while cant > lotes[cod_lote]["disponible"]:
        print(f"Error: solo hay {lotes[cod_lote]['disponible']:.2f} disponibles.")
        cant = leerCantidad("Cantidad a entregar: ")

    lotes[cod_lote]["disponible"] -= cant
    entregas.append({"beneficiario": cod_ben, "fecha": f_entr, "producto": cod_prod,
                     "lote": cod_lote, "cantidad": cant})
    acumulados["entregado"] += cant
    print("Entrega registrada.")

def detEntr():
    if len(beneficiarios) == 0:
        print("No hay beneficiarios registrados.")
        return
    cod_ben = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
    for e in entregas:
        if e["beneficiario"] == cod_ben:
            p_nom = productos[e["producto"]]["nombre"]
            print(f"{e['fecha']:12}{e['lote']:6}{p_nom:20}{e['cantidad']:10.2f}")

def repStock():
    print(f"{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
    for cat in CATEGORIAS:
        for cod_prod, p in productos.items():
            if p["categoria"] == cat:
                stk = 0
                for lote, d in lotes.items():
                    if d["producto"] == cod_prod and estLote(lote) != "Vencido":
                        stk += d["disponible"]
                print(f"{cat:16}{p['nombre']:20}{stk:10.2f}  {p['unidad']}")

def listLotes():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    for lote in lotes:
        impLote(lote)

def lotesProx():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    comp = 0
    for lote, d in lotes.items():
        if estLote(lote) == "Proximo a vencer" and d["disponible"] > 0:
            impLote(lote)
            comp += d["disponible"]
    print(f"Cantidad comprometida: {comp:.2f}")

def regiPerd():
    tot = 0
    for lote, d in lotes.items():
        if estLote(lote) == "Vencido" and d["disponible"] > 0:
            print(f"Lote {lote}: se pierden {d['disponible']:.2f}")
            tot += d["disponible"]
            d["perdido"] += d["disponible"]
            d["disponible"] = 0
    acumulados["perdido"] += tot
    print(f"Total registrado como perdida: {tot:.2f}")

def ordCant(llave_valor):
    return llave_valor[1]

def sumPor(lista, campo):
    totales = {}
    for registro in lista:
        totales[registro[campo]] = totales.get(registro[campo], 0) + registro["cantidad"]
    return dict(sorted(totales.items(), key=ordCant, reverse=True))

def rankDonantes():
    puesto = 1
    for codigo, total in sumPor(donaciones, "donante").items():
        print(f"{puesto}. {donantes[codigo]['nombre']:25}{total:10.2f}")
        puesto += 1

def totBenef():
    for codigo, total in sumPor(entregas, "beneficiario").items():
        print(f"{beneficiarios[codigo]['nombre']:25}{total:10.2f}")

def aprovecha():
    recibido = acumulados["recibido"]
    if recibido == 0:
        print("No hay donaciones registradas.")
        return
    print(f"Recibido:  {recibido:10.2f}")
    print(f"Entregado: {acumulados['entregado']:10.2f}  ({acumulados['entregado'] / recibido * 100:.2f}% aprovechado)")
    print(f"Perdido:   {acumulados['perdido']:10.2f}  ({acumulados['perdido'] / recibido * 100:.2f}% desperdiciado)")

def donacTipo():
    totales = {}
    for d in donaciones:
        tipo = donantes[d["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + d["cantidad"]
    for tipo, total in totales.items():
        print(f"{tipo:10}{total:10.2f}")

def resProd():
    entregado = sumPor(entregas, "producto")
    print(f"{'Producto':20}{'Recibido':>10}{'Entregado':>10}{'Perdido':>10}")
    for codigo, recibido in sumPor(donaciones, "producto").items():
        perdido = 0
        for d in lotes.values():
            if d["producto"] == codigo:
                perdido += d["perdido"]
        print(f"{productos[codigo]['nombre']:20}{recibido:10.2f}{entregado.get(codigo, 0):10.2f}{perdido:10.2f}")

def menuDonantes():
    while True:
        opcion = input("\n--- DONANTES ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
        if opcion == "1":
            regDonante()
        elif opcion == "2":
            listDonantes()
        elif opcion == "3":
            editDonante()
        elif opcion == "4":
            break

def menuBenef():
    while True:
        opcion = input("\n--- BENEFICIARIOS ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
        if opcion == "1":
            regBenef()
        elif opcion == "2":
            listBenef()
        elif opcion == "3":
            editBenef()
        elif opcion == "4":
            break

def menuProductos():
    while True:
        opcion = input("\n--- PRODUCTOS ---\n1. Registrar\n2. Listar\n3. Volver\nOpcion: ")
        if opcion == "1":
            regProd()
        elif opcion == "2":
            listProd()
        elif opcion == "3":
            break

def menuEntr():
    while True:
        opcion = input("\n--- ENTREGAS ---\n1. Registrar entrega\n2. Detalle por beneficiario\n3. Volver\nOpcion: ")
        if opcion == "1":
            regiEntr()
        elif opcion == "2":
            detEntr()
        elif opcion == "3":
            break

def menuStock():
    while True:
        opcion = input("\n--- STOCK Y VENCIMIENTOS ---\n1. Stock por categoria y producto\n2. Lotes y su estado\n3. Lotes proximos a vencer\n4. Registrar perdidas por vencimiento\n5. Volver\nOpcion: ")
        if opcion == "1":
            repStock()
        elif opcion == "2":
            listLotes()
        elif opcion == "3":
            lotesProx()
        elif opcion == "4":
            regiPerd()
        elif opcion == "5":
            break

def menuReportes():
    while True:
        opcion = input("\n--- REPORTES ---\n1. Stock por categoria y producto\n2. Lotes proximos a vencer\n3. Ranking de donantes\n4. Total entregado por beneficiario\n5. Aprovechamiento y perdidas\n6. Donaciones por tipo de donante\n7. Resumen por producto\n8. Volver\nOpcion: ")
        if opcion == "1":
            repStock()
        elif opcion == "2":
            lotesProx()
        elif opcion == "3":
            rankDonantes()
        elif opcion == "4":
            totBenef()
        elif opcion == "5":
            aprovecha()
        elif opcion == "6":
            donacTipo()
        elif opcion == "7":
            resProd()
        elif opcion == "8":
            break

def menuPrincipal():
    while True:
        opcion = input("\n===== BANCO DE ALIMENTOS =====\n1. Registrar / gestionar donantes\n2. Registrar / gestionar beneficiarios\n3. Registrar productos\n4. Registrar donacion y lote\n5. Registrar entrega\n6. Consultar stock y vencimientos\n7. Generar reportes\n8. Salir\nOpcion: ")
        if opcion == "1":
            menuDonantes()
        elif opcion == "2":
            menuBenef()
        elif opcion == "3":
            menuProductos()
        elif opcion == "4":
            regDonacion()
        elif opcion == "5":
            menuEntr()
        elif opcion == "6":
            menuStock()
        elif opcion == "7":
            menuReportes()
        elif opcion == "8":
            print("Hasta pronto!")
            break

menuPrincipal()
