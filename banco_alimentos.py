# Diccionarios: la llave es el codigo (las llaves son unicas)
# donantes     = {codigo: {"nombre": ..., "tipo": ..., "contacto": ...}}
# beneficiarios = {codigo: {"nombre": ..., "tipo": ..., "personas": ...}}
donantes = {}
beneficiarios = {}

# Tuplas con las opciones validas definidas por el programa
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORGANIZACION = ("Comedor Popular", "Albergue", "Olla Comun", "Asociacion", "Otra")


# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------
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


def elegirTipo(tipos):
    for i in range(len(tipos)):
        print(f"  {i + 1}. {tipos[i]}")
    while True:
        try:
            opcion = int(input("Elija una opcion: "))
            if 1 <= opcion <= len(tipos):
                return tipos[opcion - 1]
            print(f"Error: elija un numero entre 1 y {len(tipos)}.")
        except ValueError:
            print("Error: debe ingresar un numero.")


def leerCodigoNuevo(diccionario, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in diccionario:
        print(f"Error: el codigo {codigo} ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


# ------------------------------------------------------------
# 1. REGISTRAR / GESTIONAR DONANTES
# ------------------------------------------------------------
def registrarDonante():
    print("\n--- REGISTRAR DONANTE ---")
    codigo = leerCodigoNuevo(donantes, "Codigo del donante: ")
    nombre = leerTexto("Nombre o razon social: ").title()
    print("Tipo de donante:")
    tipo = elegirTipo(TIPOS_DONANTE)
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
        datos["tipo"] = elegirTipo(TIPOS_DONANTE)

    contacto = input(f"Contacto [{datos['contacto']}]: ").strip()
    if contacto != "":
        datos["contacto"] = contacto

    nuevoCodigo = input(f"Codigo [{codigo}]: ").strip().upper()
    if nuevoCodigo != "" and nuevoCodigo != codigo:
        if nuevoCodigo in donantes:
            print(f"Error: el codigo {nuevoCodigo} ya existe. Se mantiene {codigo}.")
        else:
            donantes[nuevoCodigo] = donantes.pop(codigo)
            codigo = nuevoCodigo

    print(f"Donante {codigo} actualizado correctamente.")


# ------------------------------------------------------------
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ------------------------------------------------------------
def registrarBeneficiario():
    print("\n--- REGISTRAR ORGANIZACION BENEFICIARIA ---")
    codigo = leerCodigoNuevo(beneficiarios, "Codigo de la organizacion: ")
    nombre = leerTexto("Nombre de la organizacion: ").title()
    print("Tipo de organizacion:")
    tipo = elegirTipo(TIPOS_ORGANIZACION)
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
        datos["tipo"] = elegirTipo(TIPOS_ORGANIZACION)

    cambiar = input(f"Personas atendidas: {datos['personas']}. Desea cambiarlo? (s/n): ").strip().lower()
    if cambiar == "s":
        datos["personas"] = leerEntero("Nueva cantidad de personas atendidas: ")

    nuevoCodigo = input(f"Codigo [{codigo}]: ").strip().upper()
    if nuevoCodigo != "" and nuevoCodigo != codigo:
        if nuevoCodigo in beneficiarios:
            print(f"Error: el codigo {nuevoCodigo} ya existe. Se mantiene {codigo}.")
        else:
            beneficiarios[nuevoCodigo] = beneficiarios.pop(codigo)
            codigo = nuevoCodigo

    print(f"Organizacion {codigo} actualizada correctamente.")
