donantes = []
beneficiarios = []

TIPOS_DONANTE = ["empresa", "mercado", "persona"]
TIPOS_ORGANIZACION = ["comedor popular", "albergue", "olla comun", "asociacion", "otra"]


# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------
def buscar(lista, codigo):
    for e in lista:
        if e["codigo"] == codigo:
            return e
    return None


def leer(mensaje, actual=None):
    """Lee un texto no vacio. En edicion (actual) Enter mantiene el valor."""
    while True:
        t = input(mensaje).strip()
        if t != "":
            return t
        if actual is not None:
            return actual
        print("  Error: el campo no puede estar vacio.")


def leer_entero(mensaje, actual=None):
    while True:
        t = leer(mensaje, actual)
        if str(t).isdigit() and int(t) > 0:
            return int(t)
        print("  Error: ingrese un numero entero mayor que cero.")


def elegir(mensaje, opciones, actual=None):
    for i in range(len(opciones)):
        print(f"   {i + 1}. {opciones[i]}")
    while True:
        t = leer(mensaje, actual)
        if t in opciones:
            return t
        if t.isdigit() and 1 <= int(t) <= len(opciones):
            return opciones[int(t) - 1]
        print(f"  Error: elija un numero entre 1 y {len(opciones)}.")


def leer_codigo(lista, mensaje, actual=None):
    """Lee un codigo que no se repita en la lista."""
    while True:
        c = leer(mensaje, actual).upper()
        if c == actual or buscar(lista, c) is None:
            return c
        print(f"  Error: el codigo {c} ya esta registrado.")


# ------------------------------------------------------------
# 1. REGISTRAR / GESTIONAR DONANTES
# ------------------------------------------------------------
def registrar_donante():
    donantes.append({
        "codigo": leer_codigo(donantes, "Codigo del donante: "),
        "nombre": leer("Nombre o razon social: "),
        "tipo": elegir("Tipo de donante: ", TIPOS_DONANTE),
        "contacto": leer("Contacto: "),
    })
    print("Donante registrado correctamente.")


def listar_donantes():
    if not donantes:
        print("No hay donantes registrados.")
    for d in donantes:
        print(f"{d['codigo']:<8}{d['nombre']:<30}{d['tipo']:<10}{d['contacto']}")


def editar_donante():
    d = buscar(donantes, input("Codigo del donante a editar: ").strip().upper())
    if d is None:
        print("No existe ese donante.")
        return
    print("Presione Enter para mantener el valor actual.")
    d["codigo"] = leer_codigo(donantes, f"Codigo [{d['codigo']}]: ", d["codigo"])
    d["nombre"] = leer(f"Nombre [{d['nombre']}]: ", d["nombre"])
    d["tipo"] = elegir(f"Tipo [{d['tipo']}]: ", TIPOS_DONANTE, d["tipo"])
    d["contacto"] = leer(f"Contacto [{d['contacto']}]: ", d["contacto"])
    print("Donante actualizado correctamente.")


# ------------------------------------------------------------
# 2. REGISTRAR / GESTIONAR BENEFICIARIOS
# ------------------------------------------------------------
def registrar_beneficiario():
    beneficiarios.append({
        "codigo": leer_codigo(beneficiarios, "Codigo de la organizacion: "),
        "nombre": leer("Nombre de la organizacion: "),
        "tipo": elegir("Tipo de organizacion: ", TIPOS_ORGANIZACION),
        "personas": leer_entero("Personas atendidas: "),
    })
    print("Organizacion registrada correctamente.")


def listar_beneficiarios():
    if not beneficiarios:
        print("No hay organizaciones registradas.")
    for b in beneficiarios:
        print(f"{b['codigo']:<8}{b['nombre']:<30}{b['tipo']:<18}{b['personas']}")


def editar_beneficiario():
    b = buscar(beneficiarios, input("Codigo de la organizacion a editar: ").strip().upper())
    if b is None:
        print("No existe esa organizacion.")
        return
    print("Presione Enter para mantener el valor actual.")
    b["codigo"] = leer_codigo(beneficiarios, f"Codigo [{b['codigo']}]: ", b["codigo"])
    b["nombre"] = leer(f"Nombre [{b['nombre']}]: ", b["nombre"])
    b["tipo"] = elegir(f"Tipo [{b['tipo']}]: ", TIPOS_ORGANIZACION, b["tipo"])
    b["personas"] = leer_entero(f"Personas atendidas [{b['personas']}]: ", b["personas"])
    print("Organizacion actualizada correctamente.")
