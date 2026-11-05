# AlimGest - Sistema de Gestion de Banco de Alimentos y Donaciones
# Programacion Orientada a Objetos (1ASI0781) - Trabajo Final
from abc import ABC, abstractmethod
import pandas as pd

# Constantes: opciones y limites fijos del programa
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORG = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7
MAX_CANT = 1000000
ANCHO_GRAF = 40
BARRA = "█"

# Columnas de cada archivo CSV
COLS_DONANTE = ["codigo", "nombre", "tipo", "contacto"]
COLS_BENEF = ["codigo", "nombre", "tipo", "personas"]
COLS_PRODUCTO = ["codigo", "nombre", "categoria", "unidad"]
COLS_LOTE = ["codigo", "producto", "ingreso", "vence", "recibido", "disponible", "perdido"]
COLS_DONACION = ["donante", "fecha", "producto", "lote", "cantidad"]
COLS_ENTREGA = ["beneficiario", "fecha", "producto", "lote", "cantidad"]


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


# Devuelve True si el usuario responde "s"
def confirmar(mensaje):
    return input(f"{mensaje} (s/n): ").strip().lower() == "s"


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
    diasAntes = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    # En enero y febrero solo se cuentan los bisiestos hasta el anio anterior
    anioBis = anio
    if mes <= 2:
        anioBis = anio - 1
    bisiestos = anioBis // 4 - anioBis // 100 + anioBis // 400
    return anio * 365 + bisiestos + diasAntes[mes - 1] + dia


# Clase abstracta: todo registro con codigo y nombre
class Entidad(ABC):
    def __init__(self, codigo, nombre):
        self.__codigo = codigo
        self.__nombre = nombre

    def getCodigo(self):
        return self.__codigo

    def setCodigo(self, codigo):
        self.__codigo = codigo

    def getNombre(self):
        return self.__nombre

    def setNombre(self, nombre):
        self.__nombre = nombre

    # Cada clase hija decide que datos van en su fila del CSV
    @abstractmethod
    def aFila(self):
        pass


class Donante(Entidad):
    def __init__(self, codigo, nombre, tipo, contacto):
        super().__init__(codigo, nombre)
        self.__tipo = tipo
        self.__contacto = contacto

    def getTipo(self):
        return self.__tipo

    def setTipo(self, tipo):
        self.__tipo = tipo

    def getContacto(self):
        return self.__contacto

    def setContacto(self, contacto):
        self.__contacto = contacto

    def aFila(self):
        return {"codigo": self.getCodigo(), "nombre": self.getNombre(),
                "tipo": self.__tipo, "contacto": self.__contacto}

    def __str__(self):
        return f"{self.getCodigo():8}{self.getNombre():28}{self.__tipo:10}{self.__contacto}"


class Beneficiario(Entidad):
    def __init__(self, codigo, nombre, tipo, personas):
        super().__init__(codigo, nombre)
        self.__tipo = tipo
        self.__personas = personas

    def getTipo(self):
        return self.__tipo

    def setTipo(self, tipo):
        self.__tipo = tipo

    def getPersonas(self):
        return self.__personas

    def setPersonas(self, personas):
        self.__personas = personas

    def aFila(self):
        return {"codigo": self.getCodigo(), "nombre": self.getNombre(),
                "tipo": self.__tipo, "personas": self.__personas}

    def __str__(self):
        return f"{self.getCodigo():8}{self.getNombre():28}{self.__tipo:18}{self.__personas}"


class Producto(Entidad):
    def __init__(self, codigo, nombre, categoria, unidad):
        super().__init__(codigo, nombre)
        self.__categoria = categoria
        self.__unidad = unidad

    def getCategoria(self):
        return self.__categoria

    def setCategoria(self, categoria):
        self.__categoria = categoria

    def getUnidad(self):
        return self.__unidad

    def setUnidad(self, unidad):
        self.__unidad = unidad

    def aFila(self):
        return {"codigo": self.getCodigo(), "nombre": self.getNombre(),
                "categoria": self.__categoria, "unidad": self.__unidad}

    def __str__(self):
        return f"{self.getCodigo():8}{self.getNombre():20}{self.__categoria:16}{self.__unidad}"


# Cantidad de un producto recibida en una donacion
class Lote:
    def __init__(self, codigo, producto, ingreso, vence, recibido, disponible, perdido):
        self.__codigo = codigo
        self.__producto = producto
        self.__ingreso = ingreso
        self.__vence = vence
        self.__recibido = recibido
        self.__disponible = disponible
        self.__perdido = perdido

    def getCodigo(self):
        return self.__codigo

    def getProducto(self):
        return self.__producto

    def getIngreso(self):
        return self.__ingreso

    def getVence(self):
        return self.__vence

    def getRecibido(self):
        return self.__recibido

    def getDisponible(self):
        return self.__disponible

    def getPerdido(self):
        return self.__perdido

    # Dias que faltan para que venza (negativo si ya vencio)
    def diasParaVencer(self, hoy):
        return aDias(self.__vence) - aDias(hoy)

    # Clasifica el lote segun los dias que le faltan para vencer
    def estado(self, hoy):
        dias = self.diasParaVencer(hoy)
        if dias < 0:
            return "Vencido"
        elif dias <= DIAS_ALERTA:
            return "Proximo a vencer"
        return "Disponible"

    # Sirve si tiene stock, ya ingreso y no esta vencido en esa fecha
    def sirveParaEntrega(self, fecha):
        dia = aDias(fecha)
        return self.__disponible > 0 and aDias(self.__ingreso) <= dia <= aDias(self.__vence)

    # Descuenta una entrega sin dejar el stock en negativo
    def descontar(self, cantidad):
        if cantidad <= 0 or cantidad > self.__disponible:
            return False
        self.__disponible -= cantidad
        return True

    # Pasa lo que queda del lote a perdida y devuelve esa cantidad
    def darDeBaja(self):
        resto = self.__disponible
        self.__perdido += resto
        self.__disponible = 0.0
        return resto

    def aFila(self):
        return {"codigo": self.__codigo, "producto": self.__producto.getCodigo(),
                "ingreso": self.__ingreso, "vence": self.__vence, "recibido": self.__recibido,
                "disponible": self.__disponible, "perdido": self.__perdido}


# Clase abstracta: operacion que mueve alimentos de un lote
class Movimiento(ABC):
    def __init__(self, fecha, lote, cantidad):
        self.__fecha = fecha
        self.__lote = lote
        self.__cantidad = cantidad

    def getFecha(self):
        return self.__fecha

    def getLote(self):
        return self.__lote

    def getCantidad(self):
        return self.__cantidad

    def getProducto(self):
        return self.__lote.getProducto()

    # Donacion devuelve el donante y Entrega el beneficiario
    @abstractmethod
    def getPersona(self):
        pass

    @abstractmethod
    def aFila(self):
        pass

    # Polimorfismo: getPersona() cambia segun la clase hija
    def __str__(self):
        return (f"{self.__fecha:12}{self.getPersona().getNombre():28}"
                f"{self.getProducto().getNombre():20}{self.__lote.getCodigo():6}{self.__cantidad:10.2f}")


class Donacion(Movimiento):
    def __init__(self, donante, fecha, lote, cantidad):
        super().__init__(fecha, lote, cantidad)
        self.__donante = donante

    def getPersona(self):
        return self.__donante

    def aFila(self):
        return {"donante": self.__donante.getCodigo(), "fecha": self.getFecha(),
                "producto": self.getProducto().getCodigo(),
                "lote": self.getLote().getCodigo(), "cantidad": self.getCantidad()}


class Entrega(Movimiento):
    def __init__(self, beneficiario, fecha, lote, cantidad):
        super().__init__(fecha, lote, cantidad)
        self.__beneficiario = beneficiario

    def getPersona(self):
        return self.__beneficiario

    def aFila(self):
        return {"beneficiario": self.__beneficiario.getCodigo(), "fecha": self.getFecha(),
                "producto": self.getProducto().getCodigo(),
                "lote": self.getLote().getCodigo(), "cantidad": self.getCantidad()}


# Guarda todos los objetos del sistema y aplica las reglas del negocio
class BancoAlimentos:
    def __init__(self):
        self.__donantes = {}
        self.__beneficiarios = {}
        self.__productos = {}
        self.__lotes = {}
        self.__donaciones = []
        self.__entregas = []
        self.__hoy = ""

    def getHoy(self):
        return self.__hoy

    def setHoy(self, hoy):
        self.__hoy = hoy

    # Agregacion: los donantes, beneficiarios y productos se crean fuera del banco
    def agregarDonante(self, donante):
        if isinstance(donante, Donante):
            self.__donantes[donante.getCodigo()] = donante
        else:
            print("El elemento debe ser de tipo Donante")

    def getDonantes(self):
        return self.__donantes

    def getDonante(self, codigo):
        return self.__donantes.get(codigo)

    # Cambia la llave del diccionario y el codigo del objeto
    def cambiarCodDon(self, viejo, nuevo):
        donante = self.__donantes.pop(viejo)
        donante.setCodigo(nuevo)
        self.__donantes[nuevo] = donante

    def agregarBenef(self, beneficiario):
        if isinstance(beneficiario, Beneficiario):
            self.__beneficiarios[beneficiario.getCodigo()] = beneficiario
        else:
            print("El elemento debe ser de tipo Beneficiario")

    def getBeneficiarios(self):
        return self.__beneficiarios

    def getBeneficiario(self, codigo):
        return self.__beneficiarios.get(codigo)

    def cambiarCodBenef(self, viejo, nuevo):
        beneficiario = self.__beneficiarios.pop(viejo)
        beneficiario.setCodigo(nuevo)
        self.__beneficiarios[nuevo] = beneficiario

    def agregarProducto(self, producto):
        if isinstance(producto, Producto):
            self.__productos[producto.getCodigo()] = producto
        else:
            print("El elemento debe ser de tipo Producto")

    def getProductos(self):
        return self.__productos

    def getProducto(self, codigo):
        return self.__productos.get(codigo)

    # True si el producto ya tiene lotes (entonces no se cambia su unidad)
    def productoEnUso(self, codigo):
        for lote in self.__lotes.values():
            if lote.getProducto().getCodigo() == codigo:
                return True
        return False

    def productosDeCat(self, categoria):
        lista = []
        for producto in self.__productos.values():
            if producto.getCategoria() == categoria:
                lista.append(producto)
        return lista

    # Composicion: el banco crea sus propios lotes, donaciones y entregas
    def agregarLote(self, codigo, producto, ingreso, vence, recibido, disponible, perdido):
        lote = Lote(codigo, producto, ingreso, vence, recibido, disponible, perdido)
        self.__lotes[codigo] = lote
        return lote

    def agregarDonacion(self, donante, fecha, lote, cantidad):
        self.__donaciones.append(Donacion(donante, fecha, lote, cantidad))

    def agregarEntrega(self, beneficiario, fecha, lote, cantidad):
        self.__entregas.append(Entrega(beneficiario, fecha, lote, cantidad))

    def getLotes(self):
        return self.__lotes

    def getLote(self, codigo):
        return self.__lotes.get(codigo)

    def getDonaciones(self):
        return self.__donaciones

    def getEntregas(self):
        return self.__entregas

    # Devuelve el codigo de un lote del mismo producto y vencimiento ("" si no hay)
    def loteDuplicado(self, producto, vence):
        for lote in self.__lotes.values():
            if lote.getProducto() == producto and lote.getVence() == vence:
                return lote.getCodigo()
        return ""

    # Crea el lote L1, L2, L3... y guarda la donacion
    def regDonacion(self, donante, fecha, producto, cantidad, vence):
        codigo = f"L{len(self.__lotes) + 1}"
        lote = self.agregarLote(codigo, producto, fecha, vence, cantidad, cantidad, 0.0)
        self.agregarDonacion(donante, fecha, lote, cantidad)
        return lote

    # Lotes del producto que se pueden entregar en esa fecha
    def lotesValidos(self, producto, fecha):
        validos = []
        for lote in self.__lotes.values():
            if lote.getProducto() == producto and lote.sirveParaEntrega(fecha):
                validos.append(lote)
        return validos

    # Registra la entrega solo si el lote sirve y tiene stock suficiente
    def regEntrega(self, beneficiario, fecha, lote, cantidad):
        if not lote.sirveParaEntrega(fecha) or not lote.descontar(cantidad):
            return False
        self.agregarEntrega(beneficiario, fecha, lote, cantidad)
        return True

    # Da de baja los lotes vencidos con saldo y devuelve (lote, cantidad)
    def regPerdidas(self):
        bajas = []
        for lote in self.__lotes.values():
            if lote.estado(self.__hoy) == "Vencido" and lote.getDisponible() > 0:
                bajas.append((lote, lote.darDeBaja()))
        return bajas

    # Tablas de pandas (DataFrame) para los reportes
    def tablaDonaciones(self):
        filas = []
        for donacion in self.__donaciones:
            donante = donacion.getPersona()
            filas.append({"donante": donante.getNombre(), "tipo": donante.getTipo(),
                          "producto": donacion.getProducto().getNombre(),
                          "cantidad": donacion.getCantidad()})
        return pd.DataFrame(filas, columns=["donante", "tipo", "producto", "cantidad"])

    def tablaEntregas(self):
        filas = []
        for entrega in self.__entregas:
            beneficiario = entrega.getPersona()
            filas.append({"codBenef": beneficiario.getCodigo(),
                          "beneficiario": beneficiario.getNombre(), "fecha": entrega.getFecha(),
                          "lote": entrega.getLote().getCodigo(),
                          "producto": entrega.getProducto().getNombre(),
                          "cantidad": entrega.getCantidad()})
        return pd.DataFrame(filas, columns=["codBenef", "beneficiario", "fecha", "lote",
                                            "producto", "cantidad"])

    def tablaLotes(self):
        filas = []
        for lote in self.__lotes.values():
            producto = lote.getProducto()
            filas.append({"lote": lote.getCodigo(), "codProd": producto.getCodigo(),
                          "producto": producto.getNombre(), "categoria": producto.getCategoria(),
                          "vence": lote.getVence(), "dias": lote.diasParaVencer(self.__hoy),
                          "estado": lote.estado(self.__hoy), "recibido": lote.getRecibido(),
                          "disponible": lote.getDisponible(), "perdido": lote.getPerdido()})
        return pd.DataFrame(filas, columns=["lote", "codProd", "producto", "categoria", "vence",
                                            "dias", "estado", "recibido", "disponible", "perdido"])


# Lee y escribe los datos del banco en archivos CSV con pandas
class GestorArchivos:
    # Lee un CSV; si todavia no existe devuelve una tabla vacia
    def __leer(self, nombre):
        try:
            return pd.read_csv(nombre + ".csv")
        except FileNotFoundError:
            return pd.DataFrame()

    # Polimorfismo: cada objeto sabe convertirse en fila con aFila()
    def __escribir(self, nombre, objetos, columnas):
        filas = []
        for objeto in objetos:
            filas.append(objeto.aFila())
        tabla = pd.DataFrame(filas, columns=columnas)
        tabla.to_csv(nombre + ".csv", sep=",", index=False)

    # Crea los objetos a partir de los CSV; devuelve cuantas filas no se pudieron cargar
    def cargar(self, banco):
        omitidas = 0
        tabla = self.__leer("donantes")
        for i in range(len(tabla)):
            banco.agregarDonante(Donante(str(tabla.loc[i, "codigo"]), str(tabla.loc[i, "nombre"]),
                                         str(tabla.loc[i, "tipo"]), str(tabla.loc[i, "contacto"])))
        tabla = self.__leer("beneficiarios")
        for i in range(len(tabla)):
            banco.agregarBenef(Beneficiario(str(tabla.loc[i, "codigo"]), str(tabla.loc[i, "nombre"]),
                                            str(tabla.loc[i, "tipo"]), int(tabla.loc[i, "personas"])))
        tabla = self.__leer("productos")
        for i in range(len(tabla)):
            banco.agregarProducto(Producto(str(tabla.loc[i, "codigo"]), str(tabla.loc[i, "nombre"]),
                                           str(tabla.loc[i, "categoria"]), str(tabla.loc[i, "unidad"])))
        tabla = self.__leer("lotes")
        for i in range(len(tabla)):
            producto = banco.getProducto(str(tabla.loc[i, "producto"]))
            if producto is None:
                omitidas += 1
            else:
                banco.agregarLote(str(tabla.loc[i, "codigo"]), producto, str(tabla.loc[i, "ingreso"]),
                                  str(tabla.loc[i, "vence"]), float(tabla.loc[i, "recibido"]),
                                  float(tabla.loc[i, "disponible"]), float(tabla.loc[i, "perdido"]))
        tabla = self.__leer("donaciones")
        for i in range(len(tabla)):
            donante = banco.getDonante(str(tabla.loc[i, "donante"]))
            lote = banco.getLote(str(tabla.loc[i, "lote"]))
            if donante is None or lote is None:
                omitidas += 1
            else:
                banco.agregarDonacion(donante, str(tabla.loc[i, "fecha"]), lote,
                                      float(tabla.loc[i, "cantidad"]))
        tabla = self.__leer("entregas")
        for i in range(len(tabla)):
            beneficiario = banco.getBeneficiario(str(tabla.loc[i, "beneficiario"]))
            lote = banco.getLote(str(tabla.loc[i, "lote"]))
            if beneficiario is None or lote is None:
                omitidas += 1
            else:
                banco.agregarEntrega(beneficiario, str(tabla.loc[i, "fecha"]), lote,
                                     float(tabla.loc[i, "cantidad"]))
        return omitidas

    def guardar(self, banco):
        self.__escribir("donantes", banco.getDonantes().values(), COLS_DONANTE)
        self.__escribir("beneficiarios", banco.getBeneficiarios().values(), COLS_BENEF)
        self.__escribir("productos", banco.getProductos().values(), COLS_PRODUCTO)
        self.__escribir("lotes", banco.getLotes().values(), COLS_LOTE)
        self.__escribir("donaciones", banco.getDonaciones(), COLS_DONACION)
        self.__escribir("entregas", banco.getEntregas(), COLS_ENTREGA)


# Calcula los reportes con pandas y los muestra en consola
class Reportes:
    def __init__(self, banco):
        self.__banco = banco

    # Agrupa la tabla con groupby y suma una columna; devuelve una Serie de mayor a menor
    def __sumarPor(self, tabla, campo, columna):
        totales = {}
        grupos = tabla.groupby(campo)
        for clave in grupos.groups:
            totales[clave] = grupos.get_group(clave)[columna].sum()
        return pd.Series(totales, dtype=float).sort_values(ascending=False)

    def ranking(self):
        return self.__sumarPor(self.__banco.tablaDonaciones(), "donante", "cantidad")

    def porBeneficiario(self):
        return self.__sumarPor(self.__banco.tablaEntregas(), "beneficiario", "cantidad")

    def porTipoDonante(self):
        return self.__sumarPor(self.__banco.tablaDonaciones(), "tipo", "cantidad")

    # Stock que todavia se puede entregar (sin lotes vencidos)
    def stockPorCat(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        return self.__sumarPor(tabla, "categoria", "disponible")

    def totales(self):
        lotes = self.__banco.tablaLotes()
        entregas = self.__banco.tablaEntregas()
        return pd.Series({"Recibido": lotes["recibido"].sum(), "Entregado": entregas["cantidad"].sum(),
                          "Perdido": lotes["perdido"].sum(), "En almacen": lotes["disponible"].sum()},
                         dtype=float)

    # Recibido, entregado, perdido y stock de cada producto
    def resumenProducto(self):
        lotes = self.__banco.tablaLotes()
        filas = []
        grupos = lotes.groupby("producto")
        for nombre in grupos.groups:
            grupo = grupos.get_group(nombre)
            recibido = grupo["recibido"].sum()
            perdido = grupo["perdido"].sum()
            stock = grupo["disponible"].sum()
            filas.append({"producto": nombre, "recibido": recibido,
                          "entregado": recibido - perdido - stock, "perdido": perdido, "stock": stock})
        tabla = pd.DataFrame(filas, columns=["producto", "recibido", "entregado", "perdido", "stock"])
        return tabla.sort_values("recibido", ascending=False)

    def verStock(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        print(f"\n{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
        hayStock = False
        for categoria in CATEGORIAS:
            for producto in self.__banco.productosDeCat(categoria):
                stock = tabla[tabla["codProd"] == producto.getCodigo()]["disponible"].sum()
                if stock > 0:
                    print(f"{categoria:16}{producto.getNombre():20}{stock:10.2f}  {producto.getUnidad()}")
                    hayStock = True
        if not hayStock:
            print("No hay stock disponible.")

    def verRanking(self):
        datos = self.ranking()
        if len(datos) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Puesto':8}{'Donante':28}{'Total':>10}")
        puesto = 1
        for nombre in datos.keys():
            print(f"{puesto:<8}{nombre:28}{datos[nombre]:10.2f}")
            puesto += 1

    def verBeneficiarios(self):
        datos = self.porBeneficiario()
        if len(datos) == 0:
            print("No hay entregas registradas.")
            return
        print(f"\n{'Beneficiario':28}{'Total':>10}")
        for nombre in datos.keys():
            print(f"{nombre:28}{datos[nombre]:10.2f}")

    def verAprovecha(self):
        datos = self.totales()
        recibido = datos["Recibido"]
        if recibido == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\nRecibido:   {recibido:10.2f}")
        print(f"Entregado:  {datos['Entregado']:10.2f}  "
              f"({datos['Entregado'] / recibido * 100:.2f}% aprovechado)")
        print(f"Perdido:    {datos['Perdido']:10.2f}  "
              f"({datos['Perdido'] / recibido * 100:.2f}% desperdiciado)")
        print(f"En almacen: {datos['En almacen']:10.2f}")

    def verTipos(self):
        datos = self.porTipoDonante()
        if len(datos) == 0:
            print("No hay donaciones registradas.")
            return
        total = datos.sum()
        print(f"\n{'Tipo':12}{'Cantidad':>10}{'Porcentaje':>12}")
        for tipo in datos.keys():
            print(f"{tipo:12}{datos[tipo]:10.2f}{datos[tipo] / total * 100:11.2f}%")

    def verProductos(self):
        tabla = self.resumenProducto()
        if len(tabla) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Producto':20}{'Recibido':>10}{'Entregado':>11}{'Perdido':>9}{'Stock':>9}")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'producto']:20}{tabla.loc[i, 'recibido']:10.2f}"
                  f"{tabla.loc[i, 'entregado']:11.2f}{tabla.loc[i, 'perdido']:9.2f}"
                  f"{tabla.loc[i, 'stock']:9.2f}")


# Dibuja los reportes como graficos de barras en la consola
class Graficos:
    def __init__(self, reportes):
        self.__reportes = reportes

    # Una barra por cada dato; la mas larga corresponde al valor maximo
    def __barras(self, serie, titulo):
        print(f"\n{titulo}")
        if len(serie) == 0 or serie.max() <= 0:
            print("No hay datos para el grafico.")
            return
        maximo = serie.max()
        for clave in serie.keys():
            largo = int(serie[clave] / maximo * ANCHO_GRAF)
            print(f"{clave:26}|{BARRA * largo} {serie[clave]:.2f}")

    # Una barra por cada dato; el largo representa el porcentaje del total
    def __porcentajes(self, serie, titulo):
        print(f"\n{titulo}")
        total = serie.sum()
        if len(serie) == 0 or total <= 0:
            print("No hay datos para el grafico.")
            return
        for clave in serie.keys():
            largo = int(serie[clave] / total * ANCHO_GRAF)
            print(f"{clave:26}|{BARRA * largo} {serie[clave] / total * 100:.1f}%")

    def graficoRanking(self):
        self.__barras(self.__reportes.ranking(), "RANKING DE DONANTES (cantidad donada)")

    def graficoBenef(self):
        self.__barras(self.__reportes.porBeneficiario(), "TOTAL ENTREGADO POR BENEFICIARIO")

    def graficoAprovecha(self):
        datos = self.__reportes.totales()
        partes = pd.Series({"Entregado": datos["Entregado"], "Perdido": datos["Perdido"],
                            "En almacen": datos["En almacen"]})
        self.__porcentajes(partes, "APROVECHAMIENTO Y PERDIDAS (% de lo recibido)")

    def graficoTipos(self):
        self.__porcentajes(self.__reportes.porTipoDonante(), "DONACIONES POR TIPO DE DONANTE")

    def graficoStock(self):
        self.__barras(self.__reportes.stockPorCat(), "STOCK DISPONIBLE POR CATEGORIA")

    # Tres barras por producto: R = recibido, E = entregado, P = perdido
    def graficoProductos(self):
        tabla = self.__reportes.resumenProducto()
        print("\nRECIBIDO (R), ENTREGADO (E) Y PERDIDO (P) POR PRODUCTO")
        if len(tabla) == 0:
            print("No hay datos para el grafico.")
            return
        maximo = tabla["recibido"].max()
        for i in tabla.index:
            print(tabla.loc[i, "producto"])
            for letra, columna in (("R", "recibido"), ("E", "entregado"), ("P", "perdido")):
                valor = tabla.loc[i, columna]
                print(f"  {letra} |{BARRA * int(valor / maximo * ANCHO_GRAF)} {valor:.2f}")


# Interfaz de consola: menus y pantallas de registro
class Aplicacion:
    def __init__(self):
        self.__banco = BancoAlimentos()
        self.__archivos = GestorArchivos()
        self.__reportes = Reportes(self.__banco)
        self.__graficos = Graficos(self.__reportes)

    def __guardar(self):
        self.__archivos.guardar(self.__banco)

    # Devuelve la fecha de hoy; la pide solo la primera vez que se necesita
    def __fechaHoy(self):
        if self.__banco.getHoy() == "":
            self.__banco.setHoy(leerFecha("Ingrese la fecha de hoy (AAAA-MM-DD): "))
        return self.__banco.getHoy()

    def iniciar(self):
        omitidas = self.__archivos.cargar(self.__banco)
        print("===== AlimGest: Sistema de Gestion de Banco de Alimentos =====")
        print(f"Datos cargados: {len(self.__banco.getDonantes())} donantes, "
              f"{len(self.__banco.getBeneficiarios())} beneficiarios, "
              f"{len(self.__banco.getProductos())} productos y "
              f"{len(self.__banco.getLotes())} lotes.")
        if omitidas > 0:
            print(f"Aviso: se omitieron {omitidas} filas con datos inconsistentes.")
        self.menuPrincipal()

    def regDonante(self):
        codigo = leerCodNuevo(self.__banco.getDonantes(), "Codigo: ")
        nombre = leerTexto("Nombre o razon social: ").title()
        tipo = elegir("Tipo de donante:", TIPOS_DONANTE)
        contacto = leerTexto("Contacto: ")
        self.__banco.agregarDonante(Donante(codigo, nombre, tipo, contacto))
        self.__guardar()
        print("Donante registrado.")

    def listDonantes(self):
        print(f"{'Codigo':8}{'Nombre':28}{'Tipo':10}Contacto")
        for donante in self.__banco.getDonantes().values():
            print(donante)

    def editDonante(self):
        donantes = self.__banco.getDonantes()
        if len(donantes) == 0:
            print("No hay donantes registrados.")
            return
        codigo = leerCodExist(donantes, "Codigo del donante a editar: ")
        donante = donantes[codigo]
        print("Presione Enter para mantener el valor actual.")
        donante.setNombre(mantener("Nombre", donante.getNombre()).title())
        donante.setContacto(mantener("Contacto", donante.getContacto()))
        if confirmar(f"Cambiar tipo ({donante.getTipo()})?"):
            donante.setTipo(elegir("Nuevo tipo:", TIPOS_DONANTE))
        nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
        if nuevo in donantes and nuevo != codigo:
            print("Error: ese codigo ya existe, se mantiene el anterior.")
        elif nuevo != "" and nuevo != codigo:
            self.__banco.cambiarCodDon(codigo, nuevo)
        self.__guardar()
        print("Donante actualizado.")

    def regBenef(self):
        codigo = leerCodNuevo(self.__banco.getBeneficiarios(), "Codigo: ")
        nombre = leerTexto("Nombre: ").title()
        tipo = elegir("Tipo de organizacion:", TIPOS_ORG)
        personas = leerEntero("Personas atendidas: ")
        self.__banco.agregarBenef(Beneficiario(codigo, nombre, tipo, personas))
        self.__guardar()
        print("Beneficiario registrado.")

    def listBenef(self):
        print(f"{'Codigo':8}{'Nombre':28}{'Tipo':18}Personas")
        for beneficiario in self.__banco.getBeneficiarios().values():
            print(beneficiario)

    def editBenef(self):
        beneficiarios = self.__banco.getBeneficiarios()
        if len(beneficiarios) == 0:
            print("No hay beneficiarios registrados.")
            return
        codigo = leerCodExist(beneficiarios, "Codigo del beneficiario a editar: ")
        benef = beneficiarios[codigo]
        print("Presione Enter para mantener el valor actual.")
        benef.setNombre(mantener("Nombre", benef.getNombre()).title())
        if confirmar(f"Cambiar tipo ({benef.getTipo()})?"):
            benef.setTipo(elegir("Nuevo tipo:", TIPOS_ORG))
        if confirmar(f"Cambiar personas ({benef.getPersonas()})?"):
            benef.setPersonas(leerEntero("Personas atendidas: "))
        nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
        if nuevo in beneficiarios and nuevo != codigo:
            print("Error: ese codigo ya existe, se mantiene el anterior.")
        elif nuevo != "" and nuevo != codigo:
            self.__banco.cambiarCodBenef(codigo, nuevo)
        self.__guardar()
        print("Beneficiario actualizado.")

    def regProducto(self):
        codigo = leerCodNuevo(self.__banco.getProductos(), "Codigo: ")
        nombre = leerTexto("Nombre: ").title()
        categoria = elegir("Categoria:", CATEGORIAS)
        unidad = elegir("Unidad de medida:", UNIDADES)
        self.__banco.agregarProducto(Producto(codigo, nombre, categoria, unidad))
        self.__guardar()
        print("Producto registrado.")

    def listProductos(self):
        print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
        for producto in self.__banco.getProductos().values():
            print(producto)

    def editProducto(self):
        productos = self.__banco.getProductos()
        if len(productos) == 0:
            print("No hay productos registrados.")
            return
        codigo = leerCodExist(productos, "Codigo del producto a editar: ")
        producto = productos[codigo]
        print("Presione Enter para mantener el valor actual.")
        producto.setNombre(mantener("Nombre", producto.getNombre()).title())
        if confirmar(f"Cambiar categoria ({producto.getCategoria()})?"):
            producto.setCategoria(elegir("Nueva categoria:", CATEGORIAS))
        if self.__banco.productoEnUso(codigo):
            print(f"No se puede cambiar la unidad ({producto.getUnidad()}) porque ya hay "
                  f"lotes registrados de este producto.")
        elif confirmar(f"Cambiar unidad ({producto.getUnidad()})?"):
            producto.setUnidad(elegir("Nueva unidad:", UNIDADES))
        self.__guardar()
        print("Producto actualizado.")

    def buscarCategoria(self):
        categoria = elegir("Seleccione categoria:", CATEGORIAS)
        encontrados = self.__banco.productosDeCat(categoria)
        if len(encontrados) == 0:
            print("No hay productos registrados en esta categoria.")
            return
        print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
        for producto in encontrados:
            print(producto)

    def regDonacion(self):
        donantes = self.__banco.getDonantes()
        productos = self.__banco.getProductos()
        if len(donantes) == 0 or len(productos) == 0:
            print("Primero registre un donante y un producto.")
            return
        hoy = self.__fechaHoy()
        donante = donantes[leerCodExist(donantes, "Codigo del donante: ")]
        print(f"Donante seleccionado: {donante.getNombre()}")
        fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
        while aDias(fecha) > aDias(hoy):
            print("Error: la fecha de donacion no puede ser posterior a hoy.")
            fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
        producto = productos[leerCodExist(productos, "Codigo del producto: ")]
        unidad = producto.getUnidad()
        print(f"Producto seleccionado: {producto.getNombre()} ({unidad})")
        cantidad = leerCantidad(f"Cantidad recibida ({unidad}): ")
        vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
        while aDias(vence) < aDias(fecha):
            print("Error: el vencimiento no puede ser antes de la donacion.")
            vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
        if aDias(vence) < aDias(hoy):
            print("Advertencia: Este lote ya se encuentra vencido.")
            if not confirmar("Desea registrarlo de todos modos?"):
                print("Registro de donacion cancelado.")
                return
        codL = self.__banco.loteDuplicado(producto, vence)
        if codL != "":
            print(f"Aviso: ya existe el lote {codL} de este producto con la misma "
                  f"fecha de vencimiento.")
            if not confirmar("Desea registrar un lote nuevo?"):
                print("Registro de donacion cancelado.")
                return
        lote = self.__banco.regDonacion(donante, fecha, producto, cantidad, vence)
        self.__guardar()
        print(f"Lote {lote.getCodigo()} registrado. Estado: {lote.estado(hoy)}")

    def listDonaciones(self):
        donaciones = self.__banco.getDonaciones()
        if len(donaciones) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"{'Fecha':12}{'Donante':28}{'Producto':20}{'Lote':6}{'Cantidad':>10}")
        for donacion in donaciones:
            print(donacion)

    def regEntrega(self):
        beneficiarios = self.__banco.getBeneficiarios()
        productos = self.__banco.getProductos()
        if len(beneficiarios) == 0 or len(self.__banco.getLotes()) == 0:
            print("Primero registre un beneficiario y una donacion.")
            return
        hoy = self.__fechaHoy()
        benef = beneficiarios[leerCodExist(beneficiarios, "Codigo del beneficiario: ")]
        print(f"Beneficiario seleccionado: {benef.getNombre()}")
        fecha = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
        while aDias(fecha) > aDias(hoy):
            print("Error: la fecha de entrega no puede ser posterior a hoy.")
            fecha = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
        producto = productos[leerCodExist(productos, "Codigo del producto: ")]
        validos = {}
        for lote in self.__banco.lotesValidos(producto, fecha):
            validos[lote.getCodigo()] = lote
            print(f"  {lote.getCodigo()}: {lote.getDisponible():.2f} disponibles, "
                  f"vence {lote.getVence()}")
        if len(validos) == 0:
            print("No hay lotes de ese producto con stock, sin vencer y recibidos hasta esa fecha.")
            return
        codLote = leerTexto("Codigo del lote: ").upper()
        while codLote not in validos:
            print("Error: lote no valido, sin stock, vencido o recibido despues de la entrega.")
            codLote = leerTexto("Codigo del lote: ").upper()
        lote = validos[codLote]
        cant = leerCantidad("Cantidad a entregar: ")
        while cant > lote.getDisponible():
            print(f"Error: solo hay {lote.getDisponible():.2f} disponibles.")
            cant = leerCantidad("Cantidad a entregar: ")
        self.__banco.regEntrega(benef, fecha, lote, cant)
        self.__guardar()
        print("Entrega registrada.")

    # Filtra la tabla de entregas por el codigo del beneficiario
    def detEntregas(self):
        beneficiarios = self.__banco.getBeneficiarios()
        if len(beneficiarios) == 0:
            print("No hay beneficiarios registrados.")
            return
        codigo = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
        tabla = self.__banco.tablaEntregas()
        propias = tabla[tabla["codBenef"] == codigo]
        if len(propias) == 0:
            print("Este beneficiario todavia no tiene entregas registradas.")
            return
        print(f"Entregas a {beneficiarios[codigo].getNombre()}:")
        print(f"{'Fecha':12}{'Lote':6}{'Producto':20}{'Cantidad':>10}")
        for i in propias.index:
            print(f"{propias.loc[i, 'fecha']:12}{propias.loc[i, 'lote']:6}"
                  f"{propias.loc[i, 'producto']:20}{propias.loc[i, 'cantidad']:10.2f}")
        print(f"Total entregado: {propias['cantidad'].sum():.2f}")

    def listLotes(self):
        tabla = self.__banco.tablaLotes()
        print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}{'Dias':>5}  Estado")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'lote']:6}{tabla.loc[i, 'producto']:20}"
                  f"{tabla.loc[i, 'disponible']:10.2f}  {tabla.loc[i, 'vence']:12}"
                  f"{tabla.loc[i, 'dias']:5}  {tabla.loc[i, 'estado']}")

    # Lotes con saldo que vencen en DIAS_ALERTA dias o menos, ordenados por dias
    def lotesProx(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] == "Proximo a vencer"]
        tabla = tabla[tabla["disponible"] > 0]
        tabla = tabla.sort_values("dias")
        print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}{'Dias':>5}")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'lote']:6}{tabla.loc[i, 'producto']:20}"
                  f"{tabla.loc[i, 'disponible']:10.2f}  {tabla.loc[i, 'vence']:12}"
                  f"{tabla.loc[i, 'dias']:5}")
        print(f"Cantidad comprometida: {tabla['disponible'].sum():.2f}")

    def regPerdidas(self):
        bajas = self.__banco.regPerdidas()
        tot = 0
        for lote, cantidad in bajas:
            print(f"Lote {lote.getCodigo()}: se pierden {cantidad:.2f}")
            tot += cantidad
        if len(bajas) > 0:
            self.__guardar()
        print(f"Total registrado como perdida: {tot:.2f}")

    def menuGraficos(self):
        while True:
            opcion = input("\n--- GRAFICOS ---\n1. Ranking de donantes\n2. Total entregado por "
                           "beneficiario\n3. Aprovechamiento y perdidas\n4. Donaciones por tipo "
                           "de donante\n5. Recibido, entregado y perdido por producto\n"
                           "6. Stock por categoria\n7. Volver\nOpcion: ")
            if opcion == "1":
                self.__graficos.graficoRanking()
            elif opcion == "2":
                self.__graficos.graficoBenef()
            elif opcion == "3":
                self.__graficos.graficoAprovecha()
            elif opcion == "4":
                self.__graficos.graficoTipos()
            elif opcion == "5":
                self.__graficos.graficoProductos()
            elif opcion == "6":
                self.__graficos.graficoStock()
            elif opcion == "7":
                break
            else:
                print("Opcion no valida.")

    def menuDonantes(self):
        while True:
            opcion = input("\n--- DONANTES ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
            if opcion == "1":
                self.regDonante()
            elif opcion == "2":
                self.listDonantes()
            elif opcion == "3":
                self.editDonante()
            elif opcion == "4":
                break
            else:
                print("Opcion no valida.")

    def menuBenef(self):
        while True:
            opcion = input("\n--- BENEFICIARIOS ---\n1. Registrar\n2. Listar\n3. Editar\n4. Volver\nOpcion: ")
            if opcion == "1":
                self.regBenef()
            elif opcion == "2":
                self.listBenef()
            elif opcion == "3":
                self.editBenef()
            elif opcion == "4":
                break
            else:
                print("Opcion no valida.")

    def menuProductos(self):
        while True:
            opcion = input("\n--- PRODUCTOS ---\n1. Registrar\n2. Listar\n3. Editar\n"
                           "4. Buscar por categoria\n5. Volver\nOpcion: ")
            if opcion == "1":
                self.regProducto()
            elif opcion == "2":
                self.listProductos()
            elif opcion == "3":
                self.editProducto()
            elif opcion == "4":
                self.buscarCategoria()
            elif opcion == "5":
                break
            else:
                print("Opcion no valida.")

    def menuDonaciones(self):
        while True:
            opcion = input("\n--- DONACIONES ---\n1. Registrar donacion y lote\n"
                           "2. Listar donaciones\n3. Volver\nOpcion: ")
            if opcion == "1":
                self.regDonacion()
            elif opcion == "2":
                self.listDonaciones()
            elif opcion == "3":
                break
            else:
                print("Opcion no valida.")

    def menuEntregas(self):
        while True:
            opcion = input("\n--- ENTREGAS ---\n1. Registrar entrega\n2. Detalle por beneficiario\n"
                           "3. Volver\nOpcion: ")
            if opcion == "1":
                self.regEntrega()
            elif opcion == "2":
                self.detEntregas()
            elif opcion == "3":
                break
            else:
                print("Opcion no valida.")

    def menuStock(self):
        self.__fechaHoy()
        while True:
            opcion = input("\n--- STOCK Y VENCIMIENTOS ---\n1. Stock por categoria y producto\n"
                           "2. Lotes y su estado\n3. Lotes proximos a vencer\n"
                           "4. Registrar perdidas por vencimiento\n5. Volver\nOpcion: ")
            if opcion == "1":
                self.__reportes.verStock()
            elif opcion == "2":
                self.listLotes()
            elif opcion == "3":
                self.lotesProx()
            elif opcion == "4":
                self.regPerdidas()
            elif opcion == "5":
                break
            else:
                print("Opcion no valida.")

    def menuReportes(self):
        self.__fechaHoy()
        while True:
            opcion = input("\n--- REPORTES ---\n1. Ranking de donantes\n2. Total entregado por "
                           "beneficiario\n3. Aprovechamiento y perdidas\n4. Donaciones por tipo "
                           "de donante\n5. Resumen por producto\n6. Graficos\n7. Volver\nOpcion: ")
            if opcion == "1":
                self.__reportes.verRanking()
            elif opcion == "2":
                self.__reportes.verBeneficiarios()
            elif opcion == "3":
                self.__reportes.verAprovecha()
            elif opcion == "4":
                self.__reportes.verTipos()
            elif opcion == "5":
                self.__reportes.verProductos()
            elif opcion == "6":
                self.menuGraficos()
            elif opcion == "7":
                break
            else:
                print("Opcion no valida.")

    def menuPrincipal(self):
        while True:
            opcion = input("\n===== BANCO DE ALIMENTOS =====\n1. Registrar / gestionar donantes\n"
                           "2. Registrar / gestionar beneficiarios\n3. Registrar / gestionar "
                           "productos\n4. Registrar / gestionar donaciones\n5. Registrar entrega\n"
                           "6. Consultar stock y vencimientos\n7. Generar reportes\n8. Salir\n"
                           "Opcion: ")
            if opcion == "1":
                self.menuDonantes()
            elif opcion == "2":
                self.menuBenef()
            elif opcion == "3":
                self.menuProductos()
            elif opcion == "4":
                self.menuDonaciones()
            elif opcion == "5":
                self.menuEntregas()
            elif opcion == "6":
                self.menuStock()
            elif opcion == "7":
                self.menuReportes()
            elif opcion == "8":
                self.__guardar()
                print("Datos guardados. Hasta pronto!")
                break
            else:
                print("Opcion no valida.")


# Programa principal
app = Aplicacion()
app.iniciar()
