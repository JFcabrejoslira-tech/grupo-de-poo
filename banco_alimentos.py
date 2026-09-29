donantes = []
beneficiarios = []

TIPOS_DONANTE = ["empresa", "mercado", "persona"]
TIPOS_ORGANIZACION = ["comedor popular", "albergue", "olla comun", "asociacion", "otra"]


def buscar_por_codigo(lista, codigo):
    for elemento in lista:
        if elemento["codigo"] == codigo:
            return elemento
    return None


def elegir_opcion(titulo, opciones, permitir_vacio=False):
    print(titulo)
    for i in range(len(opciones)):
        print(f"   {i + 1}. {opciones[i]}")
    while True:
        texto = input("  Seleccione una opcion: ").strip()
        if texto == "" and permitir_vacio:
            return None
        if texto.isdigit() and 1 <= int(texto) <= len(opciones):
            return opciones[int(texto) - 1]
        print(f"  Error: elija un numero entre 1 y {len(opciones)}.")


# ------------------------------------------------------------
# 1. REGISTRAR / GESTIONAR DONANTES
# ------------------------------------------------------------
def registrar_donante():
    print("\n--- REGISTRAR DONANTE ---")
    codigo = input("Codigo del donante: ").strip().upper()
    while codigo == "" or buscar_por_codigo(donantes, codigo) is not None:
        print("  Error: codigo vacio o ya registrado.")
        codigo = input("Codigo del donante: ").strip().upper()

    nombre = input("Nombre o razon social: ").strip()
    while nombre == "":
        print("  Error: el nombre no puede estar vacio.")
        nombre = input("Nombre o razon social: ").strip()

    tipo = elegir_opcion("Tipo de donante:", TIPOS_DONANTE)

    contacto = input("Contacto (telefono o correo): ").strip()
    while contacto == "":
        print("  Error: el contacto no puede estar vacio.")
        contacto = input("Contacto (telefono o correo): ").strip()

    donantes.append({"codigo": codigo, "nombre": nombre, "tipo": tipo, "contacto": contacto})
    print(f"Donante {codigo} registrado correctamente.")


def listar_donantes():
    print("\n--- LISTA DE DONANTES ---")
    if len(donantes) == 0:
        print("No hay donantes registrados.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE / RAZON SOCIAL':<30}{'TIPO':<12}{'CONTACTO':<25}")
    for d in donantes:
        print(f"{d['codigo']:<10}{d['nombre']:<30}{d['tipo']:<12}{d['contacto']:<25}")


def editar_donante():
    print("\n--- EDITAR DONANTE ---")
    codigo = input("Codigo del donante a editar: ").strip().upper()
    d = buscar_por_codigo(donantes, codigo)
    if d is None:
        print(f"No existe un donante con codigo {codigo}.")
        return

    print("Deje el campo vacio (Enter) para mantener el valor actual.")

    nuevo_codigo = input(f"Codigo [{d['codigo']}]: ").strip().upper()
    if nuevo_codigo != "" and nuevo_codigo != d["codigo"]:
        if buscar_por_codigo(donantes, nuevo_codigo) is not None:
            print(f"  Error: el codigo {nuevo_codigo} ya esta registrado. Se mantiene {d['codigo']}.")
        else:
            d["codigo"] = nuevo_codigo

    nombre = input(f"Nombre o razon social [{d['nombre']}]: ").strip()
    if nombre != "":
        d["nombre"] = nombre

    tipo = elegir_opcion(f"Tipo de donante [{d['tipo']}]:", TIPOS_DONANTE, True)
    if tipo is not None:
        d["tipo"] = tipo

    contacto = input(f"Contacto [{d['contacto']}]: ").strip()
    if contacto != "":
        d["contacto"] = contacto

    print(f"Donante {d['codigo']} actualizado correctamente.")


# ------------------------------------------------------------
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ------------------------------------------------------------
def registrar_beneficiario():
    print("\n--- REGISTRAR ORGANIZACION BENEFICIARIA ---")
    codigo = input("Codigo de la organizacion: ").strip().upper()
    while codigo == "" or buscar_por_codigo(beneficiarios, codigo) is not None:
        print("  Error: codigo vacio o ya registrado.")
        codigo = input("Codigo de la organizacion: ").strip().upper()

    nombre = input("Nombre de la organizacion: ").strip()
    while nombre == "":
        print("  Error: el nombre no puede estar vacio.")
        nombre = input("Nombre de la organizacion: ").strip()

    tipo = elegir_opcion("Tipo de organizacion:", TIPOS_ORGANIZACION)

    personas = input("Cantidad estimada de personas atendidas: ").strip()
    while not personas.isdigit() or int(personas) <= 0:
        print("  Error: ingrese un numero entero mayor que cero.")
        personas = input("Cantidad estimada de personas atendidas: ").strip()

    beneficiarios.append({"codigo": codigo, "nombre": nombre, "tipo": tipo, "personas": int(personas)})
    print(f"Organizacion beneficiaria {codigo} registrada correctamente.")


def listar_beneficiarios():
    print("\n--- LISTA DE ORGANIZACIONES BENEFICIARIAS ---")
    if len(beneficiarios) == 0:
        print("No hay organizaciones beneficiarias registradas.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE':<30}{'TIPO':<18}{'PERSONAS':>10}")
    for b in beneficiarios:
        print(f"{b['codigo']:<10}{b['nombre']:<30}{b['tipo']:<18}{b['personas']:>10}")


def editar_beneficiario():
    print("\n--- EDITAR ORGANIZACION BENEFICIARIA ---")
    codigo = input("Codigo de la organizacion a editar: ").strip().upper()
    b = buscar_por_codigo(beneficiarios, codigo)
    if b is None:
        print(f"No existe una organizacion con codigo {codigo}.")
        return

    print("Deje el campo vacio (Enter) para mantener el valor actual.")

    nuevo_codigo = input(f"Codigo [{b['codigo']}]: ").strip().upper()
    if nuevo_codigo != "" and nuevo_codigo != b["codigo"]:
        if buscar_por_codigo(beneficiarios, nuevo_codigo) is not None:
            print(f"  Error: el codigo {nuevo_codigo} ya esta registrado. Se mantiene {b['codigo']}.")
        else:
            b["codigo"] = nuevo_codigo

    nombre = input(f"Nombre [{b['nombre']}]: ").strip()
    if nombre != "":
        b["nombre"] = nombre

    tipo = elegir_opcion(f"Tipo de organizacion [{b['tipo']}]:", TIPOS_ORGANIZACION, True)
    if tipo is not None:
        b["tipo"] = tipo

    personas = input(f"Personas atendidas [{b['personas']}]: ").strip()
    while personas != "" and (not personas.isdigit() or int(personas) <= 0):
        print("  Error: ingrese un numero entero mayor que cero.")
        personas = input(f"Personas atendidas [{b['personas']}]: ").strip()
    if personas != "":
        b["personas"] = int(personas)

    print(f"Organizacion {b['codigo']} actualizada correctamente.")
