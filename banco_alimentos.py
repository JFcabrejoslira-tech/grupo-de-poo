"""
CASO 3: SISTEMA DE GESTION DE BANCO DE ALIMENTOS Y DONACIONES
Version basica (sin POO): programacion estructurada con funciones,
listas y diccionarios.

Modulos implementados:
    1. Registrar / gestionar donantes
    2. Registrar / gestionar beneficiarios
"""

# ============================================================
# ALMACENAMIENTO EN MEMORIA (listas de diccionarios)
# ============================================================
donantes = []        # cada donante: {"codigo", "nombre", "tipo", "contacto"}
beneficiarios = []   # cada beneficiario: {"codigo", "nombre", "tipo", "personas"}

# ============================================================
# OPCIONES DEFINIDAS POR EL PROGRAMA
# ============================================================
TIPOS_DONANTE = ["empresa", "mercado", "persona"]
TIPOS_ORGANIZACION = ["comedor popular", "albergue", "olla comun",
                      "asociacion", "otra"]


# ============================================================
# FUNCIONES AUXILIARES DE LECTURA Y VALIDACION
# ============================================================
def leer_texto(mensaje, permitir_vacio=False):
    """Lee un texto no vacio (o vacio si permitir_vacio es True)."""
    while True:
        texto = input(mensaje).strip()
        if texto != "" or permitir_vacio:
            return texto
        print("  Error: el campo no puede estar vacio.")


def leer_entero_positivo(mensaje, permitir_vacio=False):
    """Lee un entero mayor que cero. Si permitir_vacio, retorna None al dejarlo vacio."""
    while True:
        texto = input(mensaje).strip()
        if texto == "" and permitir_vacio:
            return None
        if texto.isdigit() and int(texto) > 0:
            return int(texto)
        print("  Error: ingrese un numero entero mayor que cero.")


def elegir_opcion(titulo, opciones, permitir_vacio=False):
    """Muestra una lista de opciones y retorna la elegida.
    Si permitir_vacio, retorna None al presionar Enter sin elegir."""
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


def buscar_por_codigo(lista, codigo):
    """Retorna el diccionario con el codigo indicado, o None si no existe."""
    for elemento in lista:
        if elemento["codigo"] == codigo:
            return elemento
    return None


def leer_codigo_nuevo(lista, mensaje):
    """Lee un codigo que no exista aun en la lista (sin duplicados)."""
    while True:
        codigo = leer_texto(mensaje).upper()
        if buscar_por_codigo(lista, codigo) is None:
            return codigo
        print(f"  Error: el codigo {codigo} ya esta registrado.")


def pausar():
    input("\nPresione Enter para continuar...")


# ============================================================
# 1. GESTION DE DONANTES
# ============================================================
def registrar_donante():
    print("\n--- REGISTRAR DONANTE ---")
    codigo = leer_codigo_nuevo(donantes, "Codigo del donante: ")
    nombre = leer_texto("Nombre o razon social: ")
    tipo = elegir_opcion("Tipo de donante:", TIPOS_DONANTE)
    contacto = leer_texto("Contacto (telefono o correo): ")

    donante = {
        "codigo": codigo,
        "nombre": nombre,
        "tipo": tipo,
        "contacto": contacto,
    }
    donantes.append(donante)
    print(f"\nDonante {codigo} registrado correctamente.")


def mostrar_donante(d):
    print(f"{d['codigo']:<10}{d['nombre']:<30}{d['tipo']:<12}{d['contacto']:<25}")


def listar_donantes():
    print("\n--- LISTA DE DONANTES ---")
    if len(donantes) == 0:
        print("No hay donantes registrados.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE / RAZON SOCIAL':<30}{'TIPO':<12}{'CONTACTO':<25}")
    print("-" * 77)
    for d in donantes:
        mostrar_donante(d)
    print(f"\nTotal de donantes: {len(donantes)}")


def buscar_donante():
    print("\n--- BUSCAR DONANTE ---")
    codigo = leer_texto("Codigo del donante: ").upper()
    d = buscar_por_codigo(donantes, codigo)
    if d is None:
        print(f"No existe un donante con codigo {codigo}.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE / RAZON SOCIAL':<30}{'TIPO':<12}{'CONTACTO':<25}")
    mostrar_donante(d)


def editar_donante():
    print("\n--- EDITAR DONANTE ---")
    codigo = leer_texto("Codigo del donante a editar: ").upper()
    d = buscar_por_codigo(donantes, codigo)
    if d is None:
        print(f"No existe un donante con codigo {codigo}.")
        return

    print("Deje el campo vacio (Enter) para mantener el valor actual.")

    nuevo_codigo = leer_texto(f"Codigo [{d['codigo']}]: ", True).upper()
    if nuevo_codigo != "" and nuevo_codigo != d["codigo"]:
        if buscar_por_codigo(donantes, nuevo_codigo) is not None:
            print(f"  Error: el codigo {nuevo_codigo} ya esta registrado. Se mantiene {d['codigo']}.")
        else:
            d["codigo"] = nuevo_codigo

    nombre = leer_texto(f"Nombre o razon social [{d['nombre']}]: ", True)
    if nombre != "":
        d["nombre"] = nombre

    tipo = elegir_opcion(f"Tipo de donante [{d['tipo']}]:", TIPOS_DONANTE, True)
    if tipo is not None:
        d["tipo"] = tipo

    contacto = leer_texto(f"Contacto [{d['contacto']}]: ", True)
    if contacto != "":
        d["contacto"] = contacto

    print(f"\nDonante {d['codigo']} actualizado correctamente.")


def menu_donantes():
    while True:
        print("\n========== GESTION DE DONANTES ==========")
        print("1. Registrar donante")
        print("2. Listar donantes")
        print("3. Buscar donante por codigo")
        print("4. Editar donante")
        print("5. Volver al menu principal")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            registrar_donante()
        elif opcion == "2":
            listar_donantes()
        elif opcion == "3":
            buscar_donante()
        elif opcion == "4":
            editar_donante()
        elif opcion == "5":
            break
        else:
            print("Opcion no valida.")
        pausar()


# ============================================================
# 2. GESTION DE BENEFICIARIOS
# ============================================================
def registrar_beneficiario():
    print("\n--- REGISTRAR ORGANIZACION BENEFICIARIA ---")
    codigo = leer_codigo_nuevo(beneficiarios, "Codigo de la organizacion: ")
    nombre = leer_texto("Nombre de la organizacion: ")
    tipo = elegir_opcion("Tipo de organizacion:", TIPOS_ORGANIZACION)
    personas = leer_entero_positivo("Cantidad estimada de personas atendidas: ")

    beneficiario = {
        "codigo": codigo,
        "nombre": nombre,
        "tipo": tipo,
        "personas": personas,
    }
    beneficiarios.append(beneficiario)
    print(f"\nOrganizacion beneficiaria {codigo} registrada correctamente.")


def mostrar_beneficiario(b):
    print(f"{b['codigo']:<10}{b['nombre']:<30}{b['tipo']:<18}{b['personas']:>10}")


def listar_beneficiarios():
    print("\n--- LISTA DE ORGANIZACIONES BENEFICIARIAS ---")
    if len(beneficiarios) == 0:
        print("No hay organizaciones beneficiarias registradas.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE':<30}{'TIPO':<18}{'PERSONAS':>10}")
    print("-" * 68)
    total_personas = 0
    for b in beneficiarios:
        mostrar_beneficiario(b)
        total_personas += b["personas"]
    print(f"\nTotal de organizaciones: {len(beneficiarios)}")
    print(f"Total estimado de personas atendidas: {total_personas}")


def buscar_beneficiario():
    print("\n--- BUSCAR ORGANIZACION BENEFICIARIA ---")
    codigo = leer_texto("Codigo de la organizacion: ").upper()
    b = buscar_por_codigo(beneficiarios, codigo)
    if b is None:
        print(f"No existe una organizacion con codigo {codigo}.")
        return
    print(f"{'CODIGO':<10}{'NOMBRE':<30}{'TIPO':<18}{'PERSONAS':>10}")
    mostrar_beneficiario(b)


def editar_beneficiario():
    print("\n--- EDITAR ORGANIZACION BENEFICIARIA ---")
    codigo = leer_texto("Codigo de la organizacion a editar: ").upper()
    b = buscar_por_codigo(beneficiarios, codigo)
    if b is None:
        print(f"No existe una organizacion con codigo {codigo}.")
        return

    print("Deje el campo vacio (Enter) para mantener el valor actual.")

    nuevo_codigo = leer_texto(f"Codigo [{b['codigo']}]: ", True).upper()
    if nuevo_codigo != "" and nuevo_codigo != b["codigo"]:
        if buscar_por_codigo(beneficiarios, nuevo_codigo) is not None:
            print(f"  Error: el codigo {nuevo_codigo} ya esta registrado. Se mantiene {b['codigo']}.")
        else:
            b["codigo"] = nuevo_codigo

    nombre = leer_texto(f"Nombre [{b['nombre']}]: ", True)
    if nombre != "":
        b["nombre"] = nombre

    tipo = elegir_opcion(f"Tipo de organizacion [{b['tipo']}]:", TIPOS_ORGANIZACION, True)
    if tipo is not None:
        b["tipo"] = tipo

    personas = leer_entero_positivo(f"Personas atendidas [{b['personas']}]: ", True)
    if personas is not None:
        b["personas"] = personas

    print(f"\nOrganizacion {b['codigo']} actualizada correctamente.")


def menu_beneficiarios():
    while True:
        print("\n======= GESTION DE BENEFICIARIOS =======")
        print("1. Registrar organizacion beneficiaria")
        print("2. Listar organizaciones beneficiarias")
        print("3. Buscar organizacion por codigo")
        print("4. Editar organizacion beneficiaria")
        print("5. Volver al menu principal")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            registrar_beneficiario()
        elif opcion == "2":
            listar_beneficiarios()
        elif opcion == "3":
            buscar_beneficiario()
        elif opcion == "4":
            editar_beneficiario()
        elif opcion == "5":
            break
        else:
            print("Opcion no valida.")
        pausar()


# ============================================================
# MENU PRINCIPAL
# ============================================================
def menu_principal():
    while True:
        print("\n==================================================")
        print("   SISTEMA DE GESTION DE BANCO DE ALIMENTOS")
        print("==================================================")
        print("1. Registrar / gestionar donantes")
        print("2. Registrar / gestionar beneficiarios")
        print("3. Salir")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            menu_donantes()
        elif opcion == "2":
            menu_beneficiarios()
        elif opcion == "3":
            print("Gracias por usar el sistema. Hasta pronto!")
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    menu_principal()
