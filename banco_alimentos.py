# ==============================================================
# CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
# Version basica: solo funciones, listas, tuplas y diccionarios
# ==============================================================

# Datos del sistema (todo se guarda en memoria)
donantes = {}
beneficiarios = {}
productos = {}
lotes = {}
donaciones = []
entregas = []
acumulados = {"recibido": 0, "entregado": 0, "perdido": 0}
sistema = {"hoy": ""}

# Constantes: opciones y limites fijos del programa
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORG = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7
MAX_CANT = 1000000

# Pide un texto y no deja que quede vacio
def leerTexto(mensaje):
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto

# Pide un numero entero mayor que cero
def leerEntero(mensaje):
    texto = input(mensaje).strip()
    while not texto.isdigit() or int(texto) == 0:
        print("Error: ingrese un numero entero mayor que cero.")
        texto = input(mensaje).strip()
    return int(texto)

# Pide una cantidad mayor que cero y que no pase de MAX_CANT
def leerCantidad(mensaje):
    while True:
        try:
            numero = float(input(mensaje))
            if numero > MAX_CANT:
                print(f"Error: la cantidad no puede ser mayor que {MAX_CANT}.")
            elif numero > 0:
                return numero
            else:
                print("Error: ingrese un numero mayor que cero.")
        except ValueError:
            print("Error: ingrese un numero valido.")

# Muestra las opciones de una tupla y devuelve la que elige el usuario
def elegir(titulo, opciones):
    print(titulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    numero = leerEntero("Opcion: ")
    while numero > len(opciones):
        print("Error: opcion no valida.")
        numero = leerEntero("Opcion: ")
    return opciones[numero - 1]

# Pide un codigo que todavia no exista (para registrar)
def leerCodNuevo(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print("Error: ese codigo ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo

# Pide un codigo que si exista (para donaciones, entregas y edicion)
def leerCodExist(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo not in diccionario:
        print("Error: ese codigo no existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo

# Al editar: si se presiona Enter se mantiene el valor actual
def mantener(campo, actual):
    texto = input(f"{campo} [{actual}]: ").strip()
    if texto == "":
        return actual
    return texto

# Revisa que la fecha tenga el formato AAAA-MM-DD y que el dia exista
def fechaValida(fecha):
    partes = fecha.split("-")
    if len(partes) != 3 or not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return False
    anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
    if mes < 1 or mes > 12:
        return False
    diasMes = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    maxDia = diasMes[mes - 1]
    # Bisiesto: divisible entre 4, salvo los divisibles entre 100 que no lo son entre 400
    # (x // 4 * 4 == x significa que x es divisible entre 4)
    esBisiesto = anio // 4 * 4 == anio and (anio // 100 * 100 != anio or anio // 400 * 400 == anio)
    if mes == 2 and esBisiesto:
        maxDia = 29
    return 1 <= dia <= maxDia

# Pide una fecha hasta que sea valida
def leerFecha(mensaje):
    fecha = input(mensaje).strip()
    while not fechaValida(fecha):
        print("Error: use el formato AAAA-MM-DD (ejemplo 2026-09-29).")
        fecha = input(mensaje).strip()
    return fecha

# Convierte una fecha en un numero de dias para poder restar dos fechas
def aDias(fecha):
    partes = fecha.split("-")
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
    # Dias del anio que ya pasaron antes de empezar cada mes (sin contar el 29 de febrero)
    diasAntes = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    # En enero y febrero el 29 de febrero de este anio todavia no ocurrio,
    # por eso solo se cuentan los bisiestos hasta el anio anterior
    anioBis = anio
    if mes <= 2:
        anioBis = anio - 1
    # Cantidad de 29 de febrero que ya pasaron: los divisibles entre 4,
    # menos los divisibles entre 100, mas los divisibles entre 400
    bisiestos = anioBis // 4 - anioBis // 100 + anioBis // 400
    return anio * 365 + bisiestos + diasAntes[mes - 1] + dia

# Devuelve la fecha de hoy; la pide solo la primera vez que se necesita
def fHoy():
    if sistema["hoy"] == "":
        sistema["hoy"] = leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): ")
    return sistema["hoy"]

# Dias que faltan para que venza un lote (negativo si ya vencio)
def dVencer(lote):
    return aDias(lotes[lote]["vence"]) - aDias(fHoy())

# Clasifica un lote segun los dias que le faltan para vencer
def estLote(lote):
    dias = dVencer(lote)
    # Menos de 0 dias: la fecha de vencimiento ya paso
    if dias < 0:
        return "Vencido"
    # De 0 a DIAS_ALERTA dias: hay que entregarlo pronto
    elif dias <= DIAS_ALERTA:
        return "Proximo a vencer"
    return "Disponible"

# Imprime una fila con los datos de un lote
def impLote(lote):
    d = lotes[lote]
    pNom = productos[d["producto"]]["nombre"]
    print(f"{lote:6}{pNom:20}{d['disponible']:10.2f}  {d['vence']:12}{estLote(lote)}")

# Registra un donante nuevo
def regDonante():
    codigo = leerCodNuevo(donantes, "Codigo: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    tipo = elegir("Tipo de donante:", TIPOS_DONANTE)
    contacto = leerTexto("Contacto: ")
    donantes[codigo] = {"nombre": nombre, "tipo": tipo, "contacto": contacto}
    print("Donante registrado.")

# Muestra todos los donantes
def listDonantes():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':10}Contacto")
    for codigo, d in donantes.items():
        print(f"{codigo:8}{d['nombre']:25}{d['tipo']:10}{d['contacto']}")

# Edita los datos de un donante (Enter mantiene el valor actual)
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

# Registra un beneficiario nuevo
def regBenef():
    codigo = leerCodNuevo(beneficiarios, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    tipo = elegir("Tipo de organizacion:", TIPOS_ORG)
    personas = leerEntero("Personas atendidas: ")
    beneficiarios[codigo] = {"nombre": nombre, "tipo": tipo, "personas": personas}
    print("Beneficiario registrado.")

# Muestra todos los beneficiarios
def listBenef():
    print(f"{'Codigo':8}{'Nombre':25}{'Tipo':18}Personas")
    for codigo, b in beneficiarios.items():
        print(f"{codigo:8}{b['nombre']:25}{b['tipo']:18}{b['personas']}")

# Edita los datos de un beneficiario (Enter mantiene el valor actual)
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

# Registra un producto nuevo
def regProd():
    codigo = leerCodNuevo(productos, "Codigo: ")
    nombre = leerTexto("Nombre: ").title()
    categoria = elegir("Categoria:", CATEGORIAS)
    unidad = elegir("Unidad de medida:", UNIDADES)
    productos[codigo] = {"nombre": nombre, "categoria": categoria, "unidad": unidad}
    print("Producto registrado.")

# Muestra todos los productos
def listProd():
    print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
    for codigo, p in productos.items():
        print(f"{codigo:8}{p['nombre']:20}{p['categoria']:16}{p['unidad']}")

# Registra una donacion y crea su lote con codigo L1, L2, L3...
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
    # "ingreso" guarda la fecha en que llego el lote, para validar las entregas
    lotes[lote] = {"producto": producto, "ingreso": fecha, "disponible": cantidad,
                   "perdido": 0, "vence": vence}
    donaciones.append({"donante": donante, "fecha": fecha, "producto": producto,
                       "lote": lote, "cantidad": cantidad})
    acumulados["recibido"] += cantidad
    print(f"Lote {lote} registrado. Estado: {estLote(lote)}")

# Registra una entrega a un beneficiario y descuenta el stock del lote
def regEntrega():
    if len(beneficiarios) == 0 or len(lotes) == 0:
        print("Primero registre un beneficiario y una donacion.")
        return
    codBen = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
    fEntr = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
    codProd = leerCodExist(productos, "Codigo del producto: ")

    # Se buscan los lotes que se pueden entregar en esa fecha
    diaEnt = aDias(fEntr)
    validos = []
    for lote, d in lotes.items():
        # El lote debe ser del producto y tener stock
        if d["producto"] == codProd and d["disponible"] > 0:
            # Ademas debe haber ingresado antes de la entrega y no estar vencido ese dia
            if aDias(d["ingreso"]) <= diaEnt and aDias(d["vence"]) >= diaEnt:
                validos.append(lote)
                print(f"  {lote}: {d['disponible']:.2f} disponibles, vence {d['vence']}")
    if len(validos) == 0:
        print("No hay lotes de ese producto con stock, sin vencer y recibidos hasta esa fecha.")
        return

    # Solo se acepta un lote de la lista de validos
    codLote = leerTexto("Codigo del lote: ").upper()
    while codLote not in validos:
        print("Error: lote no valido, sin stock, vencido o recibido despues de la entrega.")
        codLote = leerTexto("Codigo del lote: ").upper()
    # No se puede entregar mas de lo disponible (asi el stock nunca es negativo)
    cant = leerCantidad("Cantidad a entregar: ")
    while cant > lotes[codLote]["disponible"]:
        print(f"Error: solo hay {lotes[codLote]['disponible']:.2f} disponibles.")
        cant = leerCantidad("Cantidad a entregar: ")

    lotes[codLote]["disponible"] -= cant
    entregas.append({"beneficiario": codBen, "fecha": fEntr, "producto": codProd,
                     "lote": codLote, "cantidad": cant})
    acumulados["entregado"] += cant
    print("Entrega registrada.")

# Muestra todas las entregas hechas a un beneficiario
def detEntr():
    if len(beneficiarios) == 0:
        print("No hay beneficiarios registrados.")
        return
    codBen = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
    encontradas = 0
    for e in entregas:
        if e["beneficiario"] == codBen:
            pNom = productos[e["producto"]]["nombre"]
            print(f"{e['fecha']:12}{e['lote']:6}{pNom:20}{e['cantidad']:10.2f}")
            encontradas += 1
    if encontradas == 0:
        print("Este beneficiario todavia no tiene entregas registradas.")

# Muestra el stock por categoria y producto (sin contar lotes vencidos)
def repStock():
    print(f"{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
    for cat in CATEGORIAS:
        for codProd, p in productos.items():
            if p["categoria"] == cat:
                stk = 0
                for lote, d in lotes.items():
                    if d["producto"] == codProd and estLote(lote) != "Vencido":
                        stk += d["disponible"]
                print(f"{cat:16}{p['nombre']:20}{stk:10.2f}  {p['unidad']}")

# Muestra todos los lotes con su estado
def listLotes():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    for lote in lotes:
        impLote(lote)

# Muestra los lotes proximos a vencer y la cantidad comprometida
def lotesProx():
    print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}Estado")
    comp = 0
    for lote, d in lotes.items():
        if estLote(lote) == "Proximo a vencer" and d["disponible"] > 0:
            impLote(lote)
            comp += d["disponible"]
    print(f"Cantidad comprometida: {comp:.2f}")

# Pasa a perdida lo que quedo en los lotes vencidos
def regPerdida():
    tot = 0
    for lote, d in lotes.items():
        if estLote(lote) == "Vencido" and d["disponible"] > 0:
            print(f"Lote {lote}: se pierden {d['disponible']:.2f}")
            tot += d["disponible"]
            d["perdido"] += d["disponible"]
            d["disponible"] = 0
    acumulados["perdido"] += tot
    print(f"Total registrado como perdida: {tot:.2f}")

# Se usa en sorted(): devuelve la cantidad de cada par (llave, valor)
def ordCant(llaveValor):
    return llaveValor[1]

# Suma las cantidades de una lista agrupando por un campo, de mayor a menor
def sumPor(lista, campo):
    totales = {}
    for registro in lista:
        # get devuelve 0 si la llave todavia no existe en totales
        totales[registro[campo]] = totales.get(registro[campo], 0) + registro["cantidad"]
    # Se ordena por la cantidad (ordCant) de mayor a menor (reverse=True)
    return dict(sorted(totales.items(), key=ordCant, reverse=True))

# Ranking de donantes por cantidad donada
def rankDonantes():
    puesto = 1
    for codigo, total in sumPor(donaciones, "donante").items():
        print(f"{puesto}. {donantes[codigo]['nombre']:25}{total:10.2f}")
        puesto += 1

# Cantidad total entregada a cada beneficiario
def totBenef():
    for codigo, total in sumPor(entregas, "beneficiario").items():
        print(f"{beneficiarios[codigo]['nombre']:25}{total:10.2f}")

# Porcentaje de aprovechamiento y de desperdicio
def aprovecha():
    recibido = acumulados["recibido"]
    if recibido == 0:
        print("No hay donaciones registradas.")
        return
    print(f"Recibido:  {recibido:10.2f}")
    print(f"Entregado: {acumulados['entregado']:10.2f}  ({acumulados['entregado'] / recibido * 100:.2f}% aprovechado)")
    print(f"Perdido:   {acumulados['perdido']:10.2f}  ({acumulados['perdido'] / recibido * 100:.2f}% desperdiciado)")

# Reporte adicional: cantidad donada por tipo de donante
def donacTipo():
    totales = {}
    for d in donaciones:
        tipo = donantes[d["donante"]]["tipo"]
        totales[tipo] = totales.get(tipo, 0) + d["cantidad"]
    for tipo, total in totales.items():
        print(f"{tipo:10}{total:10.2f}")

# Reporte adicional: recibido, entregado y perdido de cada producto
def resProd():
    entregado = sumPor(entregas, "producto")
    print(f"{'Producto':20}{'Recibido':>10}{'Entregado':>10}{'Perdido':>10}")
    for codigo, recibido in sumPor(donaciones, "producto").items():
        perdido = 0
        for d in lotes.values():
            if d["producto"] == codigo:
                perdido += d["perdido"]
        print(f"{productos[codigo]['nombre']:20}{recibido:10.2f}{entregado.get(codigo, 0):10.2f}{perdido:10.2f}")

# Menu de la opcion 1: donantes
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
        else:
            print("Opcion no valida.")

# Menu de la opcion 2: beneficiarios
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
        else:
            print("Opcion no valida.")

# Menu de la opcion 3: productos
def menuProductos():
    while True:
        opcion = input("\n--- PRODUCTOS ---\n1. Registrar\n2. Listar\n3. Volver\nOpcion: ")
        if opcion == "1":
            regProd()
        elif opcion == "2":
            listProd()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")

# Menu de la opcion 5: entregas
def menuEntr():
    while True:
        opcion = input("\n--- ENTREGAS ---\n1. Registrar entrega\n2. Detalle por beneficiario\n3. Volver\nOpcion: ")
        if opcion == "1":
            regEntrega()
        elif opcion == "2":
            detEntr()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")

# Menu de la opcion 6: stock y vencimientos
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
            regPerdida()
        elif opcion == "5":
            break
        else:
            print("Opcion no valida.")

# Menu de la opcion 7: reportes
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
        else:
            print("Opcion no valida.")

# Menu principal del sistema (8 opciones)
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
        else:
            print("Opcion no valida.")

menuPrincipal()
