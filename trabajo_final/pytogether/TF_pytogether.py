# AlimGest - Sistema de Gestion de Banco de Alimentos y Donaciones
# Programacion Orientada a Objetos (1ASI0781) - Trabajo Final
from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt

# Constantes: opciones y limites fijos del programa
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORG = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7
MAX_CANT = 1000000

# Archivo Excel con los datos y columnas de cada una de sus hojas
ARCHIVO = "AlimGest.xlsx"
COLS_DONANTE = ["codigo", "nombre", "tipo", "contacto"]
COLS_BENEF = ["codigo", "nombre", "tipo", "personas"]
COLS_PRODUCTO = ["codigo", "nombre", "categoria", "unidad"]
COLS_DONACION = ["codigo", "donante", "fecha"]
COLS_LOTE = ["codigo", "donacion", "producto", "ingreso", "vence", "recibido", "disponible", "perdido"]
COLS_ENTREGA = ["codigo", "beneficiario", "fecha", "lote", "cantidad"]

# Colores de los graficos: uno fijo por categoria, en el mismo orden que CATEGORIAS
COLORES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
COLOR_SERIE = "#2a78d6"
COLOR_GUIA = "#52514e"


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


# Pide un codigo que si exista (para donaciones, entregas, historiales y edicion)
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
    partes = str(fecha).split("-")
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


# Pide una fecha valida que no sea posterior a la fecha de operacion
def leerFechaHasta(mensaje, hoy):
    fecha = leerFecha(mensaje)
    while aDias(fecha) > aDias(hoy):
        print(f"Error: la fecha no puede ser posterior a hoy ({hoy}).")
        fecha = leerFecha(mensaje)
    return fecha


# Fecha actual del computador en formato AAAA-MM-DD (pandas la convierte a texto)
def fechaHoy():
    return str(pd.to_datetime("today"))[:10]


# Clase abstracta: todo registro que tiene codigo y nombre
class Entidad(ABC):
    def __init__(self, codigo, nombre):
        # Se asigna con las propiedades para que los datos pasen por sus validaciones
        self.codigo = codigo
        self.nombre = nombre

    @property
    def codigo(self):
        return self.__codigo

    @codigo.setter
    def codigo(self, codigo):
        codigo = str(codigo).strip().upper()
        if codigo == "":
            raise ValueError("el codigo no puede estar vacio")
        self.__codigo = codigo

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, nombre):
        nombre = str(nombre).strip().title()
        if nombre == "":
            raise ValueError("el nombre no puede estar vacio")
        self.__nombre = nombre

    # Cada clase hija decide que datos van en su fila del Excel
    @abstractmethod
    def aFila(self):
        pass


class Donante(Entidad):
    def __init__(self, codigo, nombre, tipo, contacto):
        super().__init__(codigo, nombre)
        self.tipo = tipo
        self.contacto = contacto

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, tipo):
        if tipo not in TIPOS_DONANTE:
            raise ValueError(f"tipo de donante no valido: {tipo}")
        self.__tipo = tipo

    @property
    def contacto(self):
        return self.__contacto

    @contacto.setter
    def contacto(self, contacto):
        contacto = str(contacto).strip()
        if contacto == "":
            raise ValueError("el contacto no puede estar vacio")
        self.__contacto = contacto

    def aFila(self):
        return {"codigo": self.codigo, "nombre": self.nombre,
                "tipo": self.__tipo, "contacto": self.__contacto}

    def __str__(self):
        return f"{self.codigo:8}{self.nombre:28}{self.__tipo:10}{self.__contacto}"


class Beneficiario(Entidad):
    def __init__(self, codigo, nombre, tipo, personas):
        super().__init__(codigo, nombre)
        self.tipo = tipo
        self.personas = personas

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, tipo):
        if tipo not in TIPOS_ORG:
            raise ValueError(f"tipo de organizacion no valido: {tipo}")
        self.__tipo = tipo

    @property
    def personas(self):
        return self.__personas

    @personas.setter
    def personas(self, personas):
        personas = int(personas)
        if personas <= 0:
            raise ValueError("las personas atendidas deben ser mas de cero")
        self.__personas = personas

    def aFila(self):
        return {"codigo": self.codigo, "nombre": self.nombre,
                "tipo": self.__tipo, "personas": self.__personas}

    def __str__(self):
        return f"{self.codigo:8}{self.nombre:28}{self.__tipo:18}{self.__personas}"


class Producto(Entidad):
    def __init__(self, codigo, nombre, categoria, unidad):
        super().__init__(codigo, nombre)
        self.categoria = categoria
        self.unidad = unidad

    @property
    def categoria(self):
        return self.__categoria

    @categoria.setter
    def categoria(self, categoria):
        if categoria not in CATEGORIAS:
            raise ValueError(f"categoria no valida: {categoria}")
        self.__categoria = categoria

    @property
    def unidad(self):
        return self.__unidad

    @unidad.setter
    def unidad(self, unidad):
        if unidad not in UNIDADES:
            raise ValueError(f"unidad no valida: {unidad}")
        self.__unidad = unidad

    def aFila(self):
        return {"codigo": self.codigo, "nombre": self.nombre,
                "categoria": self.__categoria, "unidad": self.__unidad}

    def __str__(self):
        return f"{self.codigo:8}{self.nombre:20}{self.__categoria:16}{self.__unidad}"


# Cantidad concreta de un producto que llega en una donacion
class Lote:
    def __init__(self, codigo, producto, ingreso, vence, recibido, disponible, perdido):
        recibido = float(recibido)
        disponible = float(disponible)
        perdido = float(perdido)
        if not isinstance(producto, Producto):
            raise ValueError("el producto del lote debe ser de tipo Producto")
        if not fechaValida(ingreso) or not fechaValida(vence):
            raise ValueError("fecha del lote no valida")
        if aDias(vence) < aDias(ingreso):
            raise ValueError("el lote no puede vencer antes de su ingreso")
        if not 0 < recibido <= MAX_CANT:
            raise ValueError("cantidad recibida no valida")
        if not (disponible >= 0 and perdido >= 0 and round(disponible + perdido, 2) <= recibido):
            raise ValueError("el saldo del lote no cuadra con lo recibido")
        self.__codigo = str(codigo).strip().upper()
        self.__producto = producto
        self.__ingreso = ingreso
        self.__vence = vence
        self.__recibido = recibido
        self.__disponible = disponible
        self.__perdido = perdido

    # Propiedades de solo lectura: el saldo cambia solo con descontar() y darDeBaja()
    @property
    def codigo(self):
        return self.__codigo

    @property
    def producto(self):
        return self.__producto

    @property
    def ingreso(self):
        return self.__ingreso

    @property
    def vence(self):
        return self.__vence

    @property
    def recibido(self):
        return self.__recibido

    @property
    def disponible(self):
        return self.__disponible

    @property
    def perdido(self):
        return self.__perdido

    # Lo entregado es lo recibido que ya no esta en almacen ni se perdio
    @property
    def entregado(self):
        return self.__recibido - self.__disponible - self.__perdido

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
        return {"codigo": self.__codigo, "producto": self.__producto.codigo,
                "ingreso": self.__ingreso, "vence": self.__vence, "recibido": self.__recibido,
                "disponible": self.__disponible, "perdido": self.__perdido}


# Clase abstracta: operacion registrada en una fecha (donacion o entrega)
class Movimiento(ABC):
    def __init__(self, codigo, fecha):
        if not fechaValida(fecha):
            raise ValueError(f"fecha no valida: {fecha}")
        self.__codigo = str(codigo).strip().upper()
        self.__fecha = fecha

    @property
    def codigo(self):
        return self.__codigo

    @property
    def fecha(self):
        return self.__fecha

    # Mes del movimiento (AAAA-MM), se usa en los indicadores mensuales
    @property
    def mes(self):
        return self.__fecha[:7]

    # Donacion devuelve su donante y Entrega su beneficiario
    @property
    @abstractmethod
    def persona(self):
        pass

    @abstractmethod
    def cantidadTotal(self):
        pass

    @abstractmethod
    def aFila(self):
        pass

    # Polimorfismo: persona y cantidadTotal() cambian segun la clase hija
    def __str__(self):
        return (f"{self.__codigo:6}{self.__fecha:12}{self.persona.nombre:28}"
                f"{self.cantidadTotal():10.2f}")


# Recepcion de uno o mas lotes entregados por un donante
class Donacion(Movimiento):
    def __init__(self, codigo, donante, fecha):
        super().__init__(codigo, fecha)
        if not isinstance(donante, Donante):
            raise ValueError("la donacion necesita un donante registrado")
        self.__donante = donante
        self.__lotes = []

    @property
    def persona(self):
        return self.__donante

    # Se devuelve una copia para que la lista solo cambie con agregarLote()
    @property
    def lotes(self):
        return self.__lotes[:]

    # Composicion: la donacion crea sus lotes; el ingreso es la fecha de la donacion
    def agregarLote(self, codigo, producto, vence, recibido, disponible, perdido):
        lote = Lote(codigo, producto, self.fecha, vence, recibido, disponible, perdido)
        self.__lotes.append(lote)
        return lote

    def cantidadTotal(self):
        total = 0.0
        for lote in self.__lotes:
            total += lote.recibido
        return total

    def aFila(self):
        return {"codigo": self.codigo, "donante": self.__donante.codigo, "fecha": self.fecha}

    # Filas de la hoja "lotes": cada lote indica a que donacion pertenece
    def filasLotes(self):
        filas = []
        for lote in self.__lotes:
            fila = lote.aFila()
            fila["donacion"] = self.codigo
            filas.append(fila)
        return filas

    def __str__(self):
        return super().__str__() + f"  {len(self.__lotes)} lote(s)"


# Salida de alimentos de un lote hacia un beneficiario
class Entrega(Movimiento):
    def __init__(self, codigo, beneficiario, fecha, lote, cantidad):
        super().__init__(codigo, fecha)
        cantidad = float(cantidad)
        if not isinstance(beneficiario, Beneficiario):
            raise ValueError("la entrega necesita un beneficiario registrado")
        if not isinstance(lote, Lote):
            raise ValueError("la entrega necesita un lote registrado")
        if not cantidad > 0:
            raise ValueError("la cantidad entregada debe ser mayor que cero")
        self.__beneficiario = beneficiario
        self.__lote = lote
        self.__cantidad = cantidad

    @property
    def persona(self):
        return self.__beneficiario

    @property
    def lote(self):
        return self.__lote

    @property
    def cantidad(self):
        return self.__cantidad

    def cantidadTotal(self):
        return self.__cantidad

    def aFila(self):
        return {"codigo": self.codigo, "beneficiario": self.__beneficiario.codigo,
                "fecha": self.fecha, "lote": self.__lote.codigo, "cantidad": self.__cantidad}

    def __str__(self):
        return super().__str__() + f"  {self.__lote.codigo:6}{self.__lote.producto.nombre}"


# Guarda todos los objetos del sistema y aplica las reglas del negocio
class BancoAlimentos:
    def __init__(self):
        self.__donantes = {}
        self.__beneficiarios = {}
        self.__productos = {}
        self.__donaciones = {}
        self.__lotes = {}
        self.__entregas = {}
        self.__hoy = fechaHoy()

    # Fecha de operacion: por defecto la del computador
    @property
    def hoy(self):
        return self.__hoy

    @hoy.setter
    def hoy(self, hoy):
        if not fechaValida(hoy):
            raise ValueError("fecha de operacion no valida")
        self.__hoy = hoy

    @property
    def donantes(self):
        return self.__donantes

    @property
    def beneficiarios(self):
        return self.__beneficiarios

    @property
    def productos(self):
        return self.__productos

    @property
    def donaciones(self):
        return self.__donaciones

    @property
    def lotes(self):
        return self.__lotes

    @property
    def entregas(self):
        return self.__entregas

    # Agregacion: los donantes, beneficiarios y productos se crean fuera del banco
    def agregarDonante(self, donante):
        if isinstance(donante, Donante):
            self.__donantes[donante.codigo] = donante
        else:
            print("El elemento debe ser de tipo Donante")

    def agregarBenef(self, beneficiario):
        if isinstance(beneficiario, Beneficiario):
            self.__beneficiarios[beneficiario.codigo] = beneficiario
        else:
            print("El elemento debe ser de tipo Beneficiario")

    def agregarProducto(self, producto):
        if isinstance(producto, Producto):
            self.__productos[producto.codigo] = producto
        else:
            print("El elemento debe ser de tipo Producto")

    def buscarDonante(self, codigo):
        return self.__donantes.get(codigo)

    def buscarBenef(self, codigo):
        return self.__beneficiarios.get(codigo)

    def buscarProducto(self, codigo):
        return self.__productos.get(codigo)

    def buscarDonacion(self, codigo):
        return self.__donaciones.get(codigo)

    def buscarLote(self, codigo):
        return self.__lotes.get(codigo)

    # Cambia la llave del diccionario y el codigo del objeto
    def cambiarCodDon(self, viejo, nuevo):
        donante = self.__donantes.pop(viejo)
        donante.codigo = nuevo
        self.__donantes[donante.codigo] = donante

    def cambiarCodBenef(self, viejo, nuevo):
        beneficiario = self.__beneficiarios.pop(viejo)
        beneficiario.codigo = nuevo
        self.__beneficiarios[beneficiario.codigo] = beneficiario

    # True si el producto ya tiene lotes (entonces no se cambia su unidad)
    def productoEnUso(self, producto):
        for lote in self.__lotes.values():
            if lote.producto == producto:
                return True
        return False

    def productosDeCat(self, categoria):
        lista = []
        for producto in self.__productos.values():
            if producto.categoria == categoria:
                lista.append(producto)
        return lista

    # Siguiente codigo libre con una letra: D1, D2... L1, L2... E1, E2...
    def __nuevoCodigo(self, letra, diccionario):
        numero = len(diccionario) + 1
        while f"{letra}{numero}" in diccionario:
            numero += 1
        return f"{letra}{numero}"

    # Composicion: el banco crea sus donaciones y entregas; cada donacion crea sus lotes
    def crearDonacion(self, codigo, donante, fecha):
        donacion = Donacion(codigo, donante, fecha)
        self.__donaciones[donacion.codigo] = donacion
        return donacion

    def agregarLote(self, donacion, codigo, producto, vence, recibido, disponible, perdido):
        if not isinstance(donacion, Donacion):
            raise ValueError("el lote debe pertenecer a una donacion registrada")
        lote = donacion.agregarLote(codigo, producto, vence, recibido, disponible, perdido)
        self.__lotes[lote.codigo] = lote
        return lote

    def crearEntrega(self, codigo, beneficiario, fecha, lote, cantidad):
        entrega = Entrega(codigo, beneficiario, fecha, lote, cantidad)
        self.__entregas[entrega.codigo] = entrega
        return entrega

    # Devuelve el codigo de un lote del mismo producto y vencimiento ("" si no hay)
    def loteDuplicado(self, producto, vence):
        for lote in self.__lotes.values():
            if lote.producto == producto and lote.vence == vence:
                return lote.codigo
        return ""

    # Registra la donacion; detalle es una lista de tuplas (producto, cantidad, vence)
    def regDonacion(self, donante, fecha, detalle):
        donacion = self.crearDonacion(self.__nuevoCodigo("D", self.__donaciones), donante, fecha)
        for producto, cantidad, vence in detalle:
            codigo = self.__nuevoCodigo("L", self.__lotes)
            self.agregarLote(donacion, codigo, producto, vence, cantidad, cantidad, 0.0)
        return donacion

    # Lotes del producto que se pueden entregar en esa fecha
    def lotesValidos(self, producto, fecha):
        validos = []
        for lote in self.__lotes.values():
            if lote.producto == producto and lote.sirveParaEntrega(fecha):
                validos.append(lote)
        return validos

    # Registra la entrega solo si el lote sirve y tiene stock suficiente (si no, None)
    def regEntrega(self, beneficiario, fecha, lote, cantidad):
        if not lote.sirveParaEntrega(fecha) or not lote.descontar(cantidad):
            return None
        codigo = self.__nuevoCodigo("E", self.__entregas)
        return self.crearEntrega(codigo, beneficiario, fecha, lote, cantidad)

    # Da de baja los lotes vencidos con saldo y devuelve (lote, cantidad)
    def regPerdidas(self):
        bajas = []
        for lote in self.__lotes.values():
            if lote.estado(self.__hoy) == "Vencido" and lote.disponible > 0:
                bajas.append((lote, lote.darDeBaja()))
        return bajas

    # Tablas de pandas (DataFrame) que usan los reportes y los graficos
    def tablaDonaciones(self):
        filas = []
        for donacion in self.__donaciones.values():
            donante = donacion.persona
            for lote in donacion.lotes:
                producto = lote.producto
                filas.append({"donacion": donacion.codigo, "codDon": donante.codigo,
                              "donante": donante.nombre, "tipo": donante.tipo,
                              "fecha": donacion.fecha, "mes": donacion.mes, "lote": lote.codigo,
                              "producto": producto.nombre, "categoria": producto.categoria,
                              "unidad": producto.unidad, "cantidad": lote.recibido})
        return pd.DataFrame(filas, columns=["donacion", "codDon", "donante", "tipo", "fecha", "mes",
                                            "lote", "producto", "categoria", "unidad", "cantidad"])

    def tablaEntregas(self):
        filas = []
        for entrega in self.__entregas.values():
            beneficiario = entrega.persona
            producto = entrega.lote.producto
            filas.append({"entrega": entrega.codigo, "codBenef": beneficiario.codigo,
                          "beneficiario": beneficiario.nombre, "fecha": entrega.fecha,
                          "mes": entrega.mes, "lote": entrega.lote.codigo,
                          "producto": producto.nombre, "categoria": producto.categoria,
                          "unidad": producto.unidad, "cantidad": entrega.cantidad})
        return pd.DataFrame(filas, columns=["entrega", "codBenef", "beneficiario", "fecha", "mes",
                                            "lote", "producto", "categoria", "unidad", "cantidad"])

    def tablaLotes(self):
        filas = []
        for lote in self.__lotes.values():
            producto = lote.producto
            filas.append({"lote": lote.codigo, "codProd": producto.codigo,
                          "producto": producto.nombre, "categoria": producto.categoria,
                          "unidad": producto.unidad, "ingreso": lote.ingreso, "vence": lote.vence,
                          "mesVence": lote.vence[:7], "dias": lote.diasParaVencer(self.__hoy),
                          "estado": lote.estado(self.__hoy), "recibido": lote.recibido,
                          "entregado": lote.entregado, "disponible": lote.disponible,
                          "perdido": lote.perdido})
        return pd.DataFrame(filas, columns=["lote", "codProd", "producto", "categoria", "unidad",
                                            "ingreso", "vence", "mesVence", "dias", "estado",
                                            "recibido", "entregado", "disponible", "perdido"])


# Lee y escribe los datos del banco en un archivo Excel (una hoja por tabla) con pandas
class GestorArchivos:
    def __init__(self, archivo):
        self.__archivo = archivo
        self.__omitidas = 0
        self.__sinExcel = False
        self.__origen = archivo

    @property
    def archivo(self):
        return self.__archivo

    # De donde se cargaron los datos: el libro de Excel o los archivos CSV
    @property
    def origen(self):
        return self.__origen

    # pandas necesita la libreria openpyxl para el Excel; si falta, se usan archivos CSV
    def __avisarCsv(self):
        if not self.__sinExcel:
            self.__sinExcel = True
            self.__origen = "archivos CSV"
            print("Aviso: pandas necesita la libreria openpyxl para usar el Excel (pip install openpyxl).")
            print("Los datos se guardaran en archivos CSV: donantes.csv, lotes.csv, entregas.csv, etc.")

    # Lee una tabla guardada en un archivo CSV (hoja.csv); si no existe devuelve una tabla vacia
    def __leerCsv(self, hoja, columnas):
        try:
            tabla = pd.read_csv(f"{hoja}.csv")
        except FileNotFoundError:
            return pd.DataFrame(columns=columnas)
        except ValueError:
            return pd.DataFrame(columns=columnas)
        self.__origen = "archivos CSV"
        return tabla

    # Lee una hoja del Excel (o su CSV); si la hoja o una columna no existen devuelve una tabla vacia
    def __leer(self, hoja, columnas):
        try:
            tabla = pd.read_excel(self.__archivo, sheet_name=hoja)
        except ImportError:
            self.__avisarCsv()
            tabla = self.__leerCsv(hoja, columnas)
        except FileNotFoundError:
            tabla = self.__leerCsv(hoja, columnas)
        except ValueError:
            return pd.DataFrame(columns=columnas)
        for columna in columnas:
            if columna not in tabla.columns:
                self.__omitidas += len(tabla)
                return pd.DataFrame(columns=columnas)
        # Las filas con celdas vacias (NaN) no se pueden cargar
        limpia = tabla.dropna()
        self.__omitidas += len(tabla) - len(limpia)
        return limpia

    # Crea los objetos a partir de las hojas; las filas con datos no validos se omiten
    def cargar(self, banco):
        self.__omitidas = 0
        tabla = self.__leer("donantes", COLS_DONANTE)
        for i in tabla.index:
            try:
                banco.agregarDonante(Donante(tabla.loc[i, "codigo"], tabla.loc[i, "nombre"],
                                             tabla.loc[i, "tipo"], tabla.loc[i, "contacto"]))
            except ValueError:
                self.__omitidas += 1
        tabla = self.__leer("beneficiarios", COLS_BENEF)
        for i in tabla.index:
            try:
                banco.agregarBenef(Beneficiario(tabla.loc[i, "codigo"], tabla.loc[i, "nombre"],
                                                tabla.loc[i, "tipo"], tabla.loc[i, "personas"]))
            except ValueError:
                self.__omitidas += 1
        tabla = self.__leer("productos", COLS_PRODUCTO)
        for i in tabla.index:
            try:
                banco.agregarProducto(Producto(tabla.loc[i, "codigo"], tabla.loc[i, "nombre"],
                                               tabla.loc[i, "categoria"], tabla.loc[i, "unidad"]))
            except ValueError:
                self.__omitidas += 1
        tabla = self.__leer("donaciones", COLS_DONACION)
        for i in tabla.index:
            try:
                donante = banco.buscarDonante(str(tabla.loc[i, "donante"]))
                banco.crearDonacion(tabla.loc[i, "codigo"], donante, str(tabla.loc[i, "fecha"])[:10])
            except ValueError:
                self.__omitidas += 1
        tabla = self.__leer("lotes", COLS_LOTE)
        for i in tabla.index:
            try:
                donacion = banco.buscarDonacion(str(tabla.loc[i, "donacion"]))
                producto = banco.buscarProducto(str(tabla.loc[i, "producto"]))
                banco.agregarLote(donacion, tabla.loc[i, "codigo"], producto,
                                  str(tabla.loc[i, "vence"])[:10], tabla.loc[i, "recibido"],
                                  tabla.loc[i, "disponible"], tabla.loc[i, "perdido"])
            except ValueError:
                self.__omitidas += 1
        tabla = self.__leer("entregas", COLS_ENTREGA)
        for i in tabla.index:
            try:
                benef = banco.buscarBenef(str(tabla.loc[i, "beneficiario"]))
                lote = banco.buscarLote(str(tabla.loc[i, "lote"]))
                banco.crearEntrega(tabla.loc[i, "codigo"], benef, str(tabla.loc[i, "fecha"])[:10],
                                   lote, tabla.loc[i, "cantidad"])
            except ValueError:
                self.__omitidas += 1
        return self.__omitidas

    # Polimorfismo: cada objeto sabe convertirse en fila con aFila()
    def __filas(self, objetos):
        filas = []
        for objeto in objetos:
            filas.append(objeto.aFila())
        return filas

    # Una tabla (DataFrame) por hoja, con las columnas en el orden de COLS_*
    def __tablas(self, banco):
        lotes = []
        for donacion in banco.donaciones.values():
            lotes += donacion.filasLotes()
        return {"donantes": pd.DataFrame(self.__filas(banco.donantes.values()), columns=COLS_DONANTE),
                "beneficiarios": pd.DataFrame(self.__filas(banco.beneficiarios.values()),
                                              columns=COLS_BENEF),
                "productos": pd.DataFrame(self.__filas(banco.productos.values()), columns=COLS_PRODUCTO),
                "donaciones": pd.DataFrame(self.__filas(banco.donaciones.values()),
                                           columns=COLS_DONACION),
                "lotes": pd.DataFrame(lotes, columns=COLS_LOTE),
                "entregas": pd.DataFrame(self.__filas(banco.entregas.values()), columns=COLS_ENTREGA)}

    # ExcelWriter guarda las seis hojas en un solo archivo; sin openpyxl se usa un CSV por tabla
    def guardar(self, banco):
        tablas = self.__tablas(banco)
        if not self.__sinExcel:
            try:
                excel = pd.ExcelWriter(self.__archivo)
                for hoja in tablas:
                    tablas[hoja].to_excel(excel, sheet_name=hoja, index=False)
                excel.close()
                return True
            except ImportError:
                self.__avisarCsv()
            except PermissionError:
                print(f"Error: no se pudo guardar {self.__archivo}; cierrelo si esta abierto en Excel.")
                return False
        for hoja in tablas:
            tablas[hoja].to_csv(f"{hoja}.csv", index=False)
        return True


# Calcula los reportes e indicadores con pandas y los muestra en consola
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

    def rankingDon(self):
        return self.__sumarPor(self.__banco.tablaDonaciones(), "donante", "cantidad")

    def rankingBenef(self):
        return self.__sumarPor(self.__banco.tablaEntregas(), "beneficiario", "cantidad")

    def porTipoDonante(self):
        return self.__sumarPor(self.__banco.tablaDonaciones(), "tipo", "cantidad")

    # Stock que todavia se puede entregar (sin lotes vencidos)
    def stockPorCat(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        return self.__sumarPor(tabla, "categoria", "disponible")

    def entregasPorCat(self):
        return self.__sumarPor(self.__banco.tablaEntregas(), "categoria", "cantidad")

    def perdidasPorCat(self):
        tabla = self.__banco.tablaLotes()
        return self.__sumarPor(tabla[tabla["perdido"] > 0], "categoria", "perdido")

    def totales(self):
        lotes = self.__banco.tablaLotes()
        return pd.Series({"Recibido": lotes["recibido"].sum(), "Entregado": lotes["entregado"].sum(),
                          "Perdido": lotes["perdido"].sum(), "En almacen": lotes["disponible"].sum()},
                         dtype=float)

    # Historiales: se filtra la tabla por el codigo y se ordena por fecha
    def historialDon(self, codigo):
        tabla = self.__banco.tablaDonaciones()
        return tabla[tabla["codDon"] == codigo].sort_values("fecha")

    def historialBenef(self, codigo):
        tabla = self.__banco.tablaEntregas()
        return tabla[tabla["codBenef"] == codigo].sort_values("fecha")

    # Lotes con saldo que vencen en DIAS_ALERTA dias o menos, ordenados por dias
    def lotesProximos(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] == "Proximo a vencer"]
        tabla = tabla[tabla["disponible"] > 0]
        return tabla.sort_values("dias")

    # Lotes vencidos que todavia tienen saldo (falta registrarlos como perdida)
    def vencidosSaldo(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] == "Vencido"]
        return tabla[tabla["disponible"] > 0]

    # Indicadores por mes: la perdida se cuenta en el mes en que vencio el lote
    def mensual(self):
        donaciones = self.__banco.tablaDonaciones()
        entregas = self.__banco.tablaEntregas()
        lotes = self.__banco.tablaLotes()
        lotes = lotes[lotes["perdido"] > 0]
        meses = []
        for mes in list(donaciones["mes"]) + list(entregas["mes"]) + list(lotes["mesVence"]):
            if mes not in meses:
                meses.append(mes)
        meses.sort()
        filas = []
        stock = 0.0
        for mes in meses:
            inicial = stock
            recibido = donaciones[donaciones["mes"] == mes]["cantidad"].sum()
            entregado = entregas[entregas["mes"] == mes]["cantidad"].sum()
            perdido = lotes[lotes["mesVence"] == mes]["perdido"].sum()
            stock = inicial + recibido - entregado - perdido
            # Aprovechamiento del periodo: entregado frente a lo que hubo para repartir
            manejado = inicial + recibido
            aprovechado = 0.0
            if manejado > 0:
                aprovechado = entregado / manejado * 100
            filas.append({"mes": mes, "inicial": inicial, "recibido": recibido,
                          "entregado": entregado, "perdido": perdido, "stock": stock,
                          "aprovechado": aprovechado})
        return pd.DataFrame(filas, columns=["mes", "inicial", "recibido", "entregado", "perdido",
                                            "stock", "aprovechado"])

    # Recibido, entregado, perdido y stock de cada categoria
    def porCategoria(self):
        lotes = self.__banco.tablaLotes()
        filas = []
        for categoria in CATEGORIAS:
            grupo = lotes[lotes["categoria"] == categoria]
            recibido = grupo["recibido"].sum()
            if recibido > 0:
                filas.append({"categoria": categoria, "recibido": recibido,
                              "entregado": grupo["entregado"].sum(), "perdido": grupo["perdido"].sum(),
                              "stock": grupo["disponible"].sum(),
                              "aprovechado": grupo["entregado"].sum() / recibido * 100})
        return pd.DataFrame(filas, columns=["categoria", "recibido", "entregado", "perdido",
                                            "stock", "aprovechado"])

    # Recibido, entregado, perdido y stock de cada producto
    def resumenProducto(self):
        lotes = self.__banco.tablaLotes()
        filas = []
        grupos = lotes.groupby("producto")
        for nombre in grupos.groups:
            grupo = grupos.get_group(nombre)
            filas.append({"producto": nombre, "unidad": grupo["unidad"].iloc[0],
                          "recibido": grupo["recibido"].sum(), "entregado": grupo["entregado"].sum(),
                          "perdido": grupo["perdido"].sum(), "stock": grupo["disponible"].sum()})
        tabla = pd.DataFrame(filas, columns=["producto", "unidad", "recibido", "entregado",
                                             "perdido", "stock"])
        return tabla.sort_values("recibido", ascending=False)

    def verStock(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        print(f"\n{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
        hayStock = False
        for categoria in CATEGORIAS:
            for producto in self.__banco.productosDeCat(categoria):
                stock = tabla[tabla["codProd"] == producto.codigo]["disponible"].sum()
                if stock > 0:
                    print(f"{categoria:16}{producto.nombre:20}{stock:10.2f}  {producto.unidad}")
                    hayStock = True
        if not hayStock:
            print("No hay stock disponible.")

    def verRankingDon(self):
        datos = self.rankingDon()
        if len(datos) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Puesto':8}{'Donante':28}{'Total donado':>12}")
        puesto = 1
        for nombre in datos.keys():
            print(f"{puesto:<8}{nombre:28}{datos[nombre]:12.2f}")
            puesto += 1

    def verRankingBen(self):
        datos = self.rankingBenef()
        if len(datos) == 0:
            print("No hay entregas registradas.")
            return
        print(f"\n{'Puesto':8}{'Beneficiario':28}{'Total recibido':>14}")
        puesto = 1
        for nombre in datos.keys():
            print(f"{puesto:<8}{nombre:28}{datos[nombre]:14.2f}")
            puesto += 1

    def verAprovecha(self):
        datos = self.totales()
        recibido = datos["Recibido"]
        if recibido == 0:
            print("No hay donaciones registradas.")
            return
        print("\nAPROVECHAMIENTO GENERAL")
        print(f"Recibido:   {recibido:10.2f}")
        print(f"Entregado:  {datos['Entregado']:10.2f}  "
              f"({datos['Entregado'] / recibido * 100:.2f}% aprovechado)")
        print(f"Perdido:    {datos['Perdido']:10.2f}  "
              f"({datos['Perdido'] / recibido * 100:.2f}% desperdiciado)")
        print(f"En almacen: {datos['En almacen']:10.2f}  "
              f"({datos['En almacen'] / recibido * 100:.2f}% por entregar)")
        tabla = self.mensual()
        print("\nAPROVECHAMIENTO POR PERIODO (stock inicial + recibido del mes)")
        print(f"{'Mes':10}{'Para repartir':>14}{'Entregado':>11}{'Aprovechado':>13}")
        for i in tabla.index:
            manejado = tabla.loc[i, "inicial"] + tabla.loc[i, "recibido"]
            print(f"{tabla.loc[i, 'mes']:10}{manejado:14.2f}{tabla.loc[i, 'entregado']:11.2f}"
                  f"{tabla.loc[i, 'aprovechado']:12.2f}%")

    def verMensual(self):
        tabla = self.mensual()
        if len(tabla) == 0:
            print("No hay movimientos registrados.")
            return
        print(f"\n{'Mes':10}{'Recibido':>10}{'Entregado':>11}{'Perdido':>9}{'Stock final':>13}")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'mes']:10}{tabla.loc[i, 'recibido']:10.2f}"
                  f"{tabla.loc[i, 'entregado']:11.2f}{tabla.loc[i, 'perdido']:9.2f}"
                  f"{tabla.loc[i, 'stock']:13.2f}")
        print(f"{'Total':10}{tabla['recibido'].sum():10.2f}{tabla['entregado'].sum():11.2f}"
              f"{tabla['perdido'].sum():9.2f}")

    # Compara las categorias y muestra cual tiene mayor donacion, entrega y desperdicio
    def verCategorias(self):
        tabla = self.porCategoria()
        if len(tabla) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Categoria':16}{'Recibido':>10}{'Entregado':>11}{'Perdido':>9}{'Stock':>9}"
              f"{'Aprovechado':>13}")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'categoria']:16}{tabla.loc[i, 'recibido']:10.2f}"
                  f"{tabla.loc[i, 'entregado']:11.2f}{tabla.loc[i, 'perdido']:9.2f}"
                  f"{tabla.loc[i, 'stock']:9.2f}{tabla.loc[i, 'aprovechado']:12.2f}%")
        for titulo, columna in (("Mayor donacion", "recibido"), ("Mayor entrega", "entregado"),
                                ("Mayor desperdicio", "perdido")):
            fila = tabla.sort_values(columna, ascending=False).iloc[0]
            if fila[columna] > 0:
                print(f"{titulo + ':':19}{fila['categoria']} ({fila[columna]:.2f})")
            else:
                print(f"{titulo + ':':19}ninguna")

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
        print(f"\n{'Producto':20}{'Unidad':10}{'Recibido':>10}{'Entregado':>11}{'Perdido':>9}"
              f"{'Stock':>9}")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'producto']:20}{tabla.loc[i, 'unidad']:10}"
                  f"{tabla.loc[i, 'recibido']:10.2f}{tabla.loc[i, 'entregado']:11.2f}"
                  f"{tabla.loc[i, 'perdido']:9.2f}{tabla.loc[i, 'stock']:9.2f}")


# Dibuja los graficos con matplotlib, los muestra y los guarda como imagen PNG
class Graficos:
    def __init__(self, reportes):
        self.__reportes = reportes

    def __mostrar(self, archivo):
        plt.tight_layout()
        plt.savefig(archivo)
        print(f"Grafico guardado en {archivo}")
        plt.show()
        plt.close()

    # Cada categoria conserva su color en todos los graficos
    def __colores(self, categorias):
        lista = []
        for categoria in categorias:
            lista.append(COLORES[CATEGORIAS.index(categoria)])
        return lista

    def __barras(self, serie, titulo, eje, archivo, colores):
        if len(serie) == 0:
            print("No hay datos para el grafico.")
            return
        plt.figure(figsize=(9, 5))
        plt.bar(list(serie.keys()), list(serie.values), color=colores)
        plt.title(titulo)
        plt.ylabel(eje)
        plt.xticks(rotation=15)
        plt.grid(axis="y", alpha=0.3)
        self.__mostrar(archivo)

    def __pastel(self, serie, titulo, archivo):
        if len(serie) == 0 or serie.sum() <= 0:
            print("No hay datos para el grafico.")
            return
        plt.figure(figsize=(7, 6))
        plt.pie(list(serie.values), labels=list(serie.keys()), autopct="%1.1f%%",
                colors=self.__colores(serie.keys()), startangle=90)
        plt.title(titulo)
        self.__mostrar(archivo)

    # Barras: total donado por cada donante
    def graficoDonantes(self):
        self.__barras(self.__reportes.rankingDon(), "Total donado por donante", "Cantidad donada",
                      "grafico_donantes.png", COLOR_SERIE)

    # Lineas: evolucion mensual de lo recibido y lo entregado
    def graficoMensual(self):
        tabla = self.__reportes.mensual()
        if len(tabla) == 0:
            print("No hay datos para el grafico.")
            return
        plt.figure(figsize=(9, 5))
        plt.plot(tabla["mes"], tabla["recibido"], marker="o", color=COLORES[0], label="Recibido")
        plt.plot(tabla["mes"], tabla["entregado"], marker="o", color=COLORES[1], label="Entregado")
        plt.title("Evolucion mensual de alimentos recibidos y entregados")
        plt.xlabel("Mes")
        plt.ylabel("Cantidad")
        plt.ylim(bottom=0)
        plt.legend()
        plt.grid(axis="y", alpha=0.3)
        self.__mostrar("grafico_mensual.png")

    # Pastel: distribucion del stock disponible por categoria
    def graficoStockCat(self):
        self.__pastel(self.__reportes.stockPorCat(), "Distribucion del stock disponible por categoria",
                      "grafico_stock.png")

    # Pastel: distribucion de las entregas por categoria
    def graficoEntCat(self):
        self.__pastel(self.__reportes.entregasPorCat(), "Distribucion de las entregas por categoria",
                      "grafico_entregas.png")

    # Barras: cantidad perdida por vencimiento en cada categoria
    def graficoPerdidas(self):
        serie = self.__reportes.perdidasPorCat()
        self.__barras(serie, "Perdidas por vencimiento segun categoria", "Cantidad perdida",
                      "grafico_perdidas.png", self.__colores(serie.keys()))

    # Barras por mes y una linea punteada con el aprovechamiento general
    def graficoAprovecha(self):
        tabla = self.__reportes.mensual()
        datos = self.__reportes.totales()
        if len(tabla) == 0 or datos["Recibido"] == 0:
            print("No hay datos para el grafico.")
            return
        general = datos["Entregado"] / datos["Recibido"] * 100
        plt.figure(figsize=(9, 5))
        plt.bar(tabla["mes"], tabla["aprovechado"], color=COLOR_SERIE, label="Aprovechamiento del mes")
        plt.plot(tabla["mes"], [general] * len(tabla), linestyle="--", color=COLOR_GUIA,
                 label=f"General: {general:.1f}%")
        plt.title("Aprovechamiento general y por periodo (%)")
        plt.xlabel("Mes")
        plt.ylabel("% entregado")
        plt.ylim(0, 100)
        plt.legend()
        plt.grid(axis="y", alpha=0.3)
        self.__mostrar("grafico_aprovechamiento.png")

    # Barras horizontales: ranking de beneficiarios (el primero arriba)
    def graficoBenef(self):
        serie = self.__reportes.rankingBenef()
        if len(serie) == 0:
            print("No hay datos para el grafico.")
            return
        plt.figure(figsize=(9, 5))
        plt.barh(list(serie.keys())[::-1], list(serie.values)[::-1], color=COLOR_SERIE)
        plt.title("Ranking de beneficiarios por cantidad recibida")
        plt.xlabel("Cantidad recibida")
        plt.grid(axis="x", alpha=0.3)
        self.__mostrar("grafico_beneficiarios.png")


# Interfaz de consola: menus y pantallas de registro
class Aplicacion:
    def __init__(self):
        self.__banco = BancoAlimentos()
        self.__archivos = GestorArchivos(ARCHIVO)
        self.__reportes = Reportes(self.__banco)
        self.__graficos = Graficos(self.__reportes)

    def __guardar(self):
        self.__archivos.guardar(self.__banco)

    def iniciar(self):
        print("===== AlimGest: Sistema de Gestion de Banco de Alimentos =====")
        omitidas = self.__archivos.cargar(self.__banco)
        print(f"Datos cargados de {self.__archivos.origen}: {len(self.__banco.donantes)} donantes, "
              f"{len(self.__banco.beneficiarios)} beneficiarios, {len(self.__banco.productos)} "
              f"productos,\n{len(self.__banco.donaciones)} donaciones ({len(self.__banco.lotes)} "
              f"lotes) y {len(self.__banco.entregas)} entregas.")
        if omitidas > 0:
            print(f"Aviso: se omitieron {omitidas} filas con datos incompletos o no validos.")
        print(f"Fecha de operacion: {self.__banco.hoy}")
        self.alertas()
        self.menuPrincipal()

    # Alertas automaticas que se calculan con los lotes guardados
    def alertas(self):
        proximos = self.__reportes.lotesProximos()
        vencidos = self.__reportes.vencidosSaldo()
        if len(proximos) == 0 and len(vencidos) == 0:
            print("Sin alertas: no hay lotes por vencer ni vencidos con saldo.")
            return
        if len(proximos) > 0:
            print(f"Advertencia: {len(proximos)} lote(s) vencen en {DIAS_ALERTA} dias o menos:")
            for i in proximos.index:
                print(f"  {proximos.loc[i, 'lote']:6}{proximos.loc[i, 'producto']:20}"
                      f"{proximos.loc[i, 'disponible']:8.2f} {proximos.loc[i, 'unidad']:9}"
                      f"vence {proximos.loc[i, 'vence']} ({proximos.loc[i, 'dias']} dias)")
        if len(vencidos) > 0:
            print(f"Advertencia: {len(vencidos)} lote(s) vencidos con saldo "
                  f"({vencidos['disponible'].sum():.2f}); registre la perdida en el menu 6.")

    def regDonante(self):
        codigo = leerCodNuevo(self.__banco.donantes, "Codigo: ")
        nombre = leerTexto("Nombre o razon social: ")
        tipo = elegir("Tipo de donante:", TIPOS_DONANTE)
        contacto = leerTexto("Contacto: ")
        self.__banco.agregarDonante(Donante(codigo, nombre, tipo, contacto))
        self.__guardar()
        print("Donante registrado.")

    def listDonantes(self):
        print(f"{'Codigo':8}{'Nombre':28}{'Tipo':10}Contacto")
        for donante in self.__banco.donantes.values():
            print(donante)

    def editDonante(self):
        donantes = self.__banco.donantes
        if len(donantes) == 0:
            print("No hay donantes registrados.")
            return
        codigo = leerCodExist(donantes, "Codigo del donante a editar: ")
        donante = donantes[codigo]
        print("Presione Enter para mantener el valor actual.")
        donante.nombre = mantener("Nombre", donante.nombre)
        donante.contacto = mantener("Contacto", donante.contacto)
        if confirmar(f"Cambiar tipo ({donante.tipo})?"):
            donante.tipo = elegir("Nuevo tipo:", TIPOS_DONANTE)
        nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
        if nuevo in donantes and nuevo != codigo:
            print("Error: ese codigo ya existe, se mantiene el anterior.")
        elif nuevo != "" and nuevo != codigo:
            self.__banco.cambiarCodDon(codigo, nuevo)
        self.__guardar()
        print("Donante actualizado.")

    def regBenef(self):
        codigo = leerCodNuevo(self.__banco.beneficiarios, "Codigo: ")
        nombre = leerTexto("Nombre: ")
        tipo = elegir("Tipo de organizacion:", TIPOS_ORG)
        personas = leerEntero("Personas atendidas: ")
        self.__banco.agregarBenef(Beneficiario(codigo, nombre, tipo, personas))
        self.__guardar()
        print("Beneficiario registrado.")

    def listBenef(self):
        print(f"{'Codigo':8}{'Nombre':28}{'Tipo':18}Personas")
        for beneficiario in self.__banco.beneficiarios.values():
            print(beneficiario)

    def editBenef(self):
        beneficiarios = self.__banco.beneficiarios
        if len(beneficiarios) == 0:
            print("No hay beneficiarios registrados.")
            return
        codigo = leerCodExist(beneficiarios, "Codigo del beneficiario a editar: ")
        benef = beneficiarios[codigo]
        print("Presione Enter para mantener el valor actual.")
        benef.nombre = mantener("Nombre", benef.nombre)
        if confirmar(f"Cambiar tipo ({benef.tipo})?"):
            benef.tipo = elegir("Nuevo tipo:", TIPOS_ORG)
        if confirmar(f"Cambiar personas ({benef.personas})?"):
            benef.personas = leerEntero("Personas atendidas: ")
        nuevo = input(f"Nuevo codigo [{codigo}]: ").strip().upper()
        if nuevo in beneficiarios and nuevo != codigo:
            print("Error: ese codigo ya existe, se mantiene el anterior.")
        elif nuevo != "" and nuevo != codigo:
            self.__banco.cambiarCodBenef(codigo, nuevo)
        self.__guardar()
        print("Beneficiario actualizado.")

    def regProducto(self):
        codigo = leerCodNuevo(self.__banco.productos, "Codigo: ")
        nombre = leerTexto("Nombre: ")
        categoria = elegir("Categoria:", CATEGORIAS)
        unidad = elegir("Unidad de medida:", UNIDADES)
        self.__banco.agregarProducto(Producto(codigo, nombre, categoria, unidad))
        self.__guardar()
        print("Producto registrado.")

    def listProductos(self):
        print(f"{'Codigo':8}{'Nombre':20}{'Categoria':16}Unidad")
        for producto in self.__banco.productos.values():
            print(producto)

    def editProducto(self):
        productos = self.__banco.productos
        if len(productos) == 0:
            print("No hay productos registrados.")
            return
        codigo = leerCodExist(productos, "Codigo del producto a editar: ")
        producto = productos[codigo]
        print("Presione Enter para mantener el valor actual.")
        producto.nombre = mantener("Nombre", producto.nombre)
        if confirmar(f"Cambiar categoria ({producto.categoria})?"):
            producto.categoria = elegir("Nueva categoria:", CATEGORIAS)
        if self.__banco.productoEnUso(producto):
            print(f"No se puede cambiar la unidad ({producto.unidad}) porque ya hay "
                  f"lotes registrados de este producto.")
        elif confirmar(f"Cambiar unidad ({producto.unidad})?"):
            producto.unidad = elegir("Nueva unidad:", UNIDADES)
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

    # Revisa si el lote ya vencio o se repite y pregunta si igual se registra
    def __aceptarLote(self, producto, vence, detalle):
        if aDias(vence) < aDias(self.__banco.hoy):
            print("Advertencia: Este lote ya se encuentra vencido.")
            if not confirmar("Desea registrarlo de todos modos?"):
                print("Lote descartado.")
                return False
        for item in detalle:
            if item[0] == producto and item[2] == vence:
                print("Aviso: ya agrego este producto con la misma fecha de vencimiento.")
                if not confirmar("Desea agregarlo como otro lote?"):
                    print("Lote descartado.")
                    return False
        codL = self.__banco.loteDuplicado(producto, vence)
        if codL != "":
            print(f"Aviso: ya existe el lote {codL} de este producto con la misma "
                  f"fecha de vencimiento.")
            if not confirmar("Desea registrar un lote nuevo?"):
                print("Lote descartado.")
                return False
        return True

    # Una donacion puede traer varios productos; cada uno se guarda como un lote
    def regDonacion(self):
        donantes = self.__banco.donantes
        productos = self.__banco.productos
        if len(donantes) == 0 or len(productos) == 0:
            print("Primero registre un donante y un producto.")
            return
        donante = donantes[leerCodExist(donantes, "Codigo del donante: ")]
        print(f"Donante seleccionado: {donante.nombre}")
        fecha = leerFechaHasta("Fecha de donacion (AAAA-MM-DD): ", self.__banco.hoy)
        detalle = []
        otro = True
        while otro:
            print(f"-- Lote {len(detalle) + 1} de la donacion --")
            producto = productos[leerCodExist(productos, "Codigo del producto: ")]
            unidad = producto.unidad
            print(f"Producto seleccionado: {producto.nombre} ({unidad})")
            cantidad = leerCantidad(f"Cantidad recibida ({unidad}): ")
            vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
            while aDias(vence) < aDias(fecha):
                print("Error: el vencimiento no puede ser antes de la donacion.")
                vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
            if self.__aceptarLote(producto, vence, detalle):
                detalle.append((producto, cantidad, vence))
            otro = confirmar("Desea agregar otro producto a esta donacion?")
        if len(detalle) == 0:
            print("Registro de donacion cancelado: no se agrego ningun lote.")
            return
        donacion = self.__banco.regDonacion(donante, fecha, detalle)
        self.__guardar()
        print(f"Donacion {donacion.codigo} registrada con {len(donacion.lotes)} lote(s):")
        for lote in donacion.lotes:
            print(f"  {lote.codigo:6}{lote.producto.nombre:20}{lote.recibido:10.2f} "
                  f"{lote.producto.unidad:9}{lote.estado(self.__banco.hoy)}")

    def listDonaciones(self):
        donaciones = self.__banco.donaciones
        if len(donaciones) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"{'Cod':6}{'Fecha':12}{'Donante':28}{'Cantidad':>10}  Lotes")
        for donacion in donaciones.values():
            print(donacion)

    # Historial de donaciones de un donante, lote por lote
    def histDonante(self):
        donantes = self.__banco.donantes
        if len(donantes) == 0:
            print("No hay donantes registrados.")
            return
        codigo = leerCodExist(donantes, "Codigo del donante: ")
        tabla = self.__reportes.historialDon(codigo)
        if len(tabla) == 0:
            print("Este donante todavia no tiene donaciones registradas.")
            return
        print(f"Historial de donaciones de {donantes[codigo].nombre}:")
        print(f"{'Donacion':10}{'Fecha':12}{'Lote':6}{'Producto':20}{'Cantidad':>10}  Unidad")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'donacion']:10}{tabla.loc[i, 'fecha']:12}{tabla.loc[i, 'lote']:6}"
                  f"{tabla.loc[i, 'producto']:20}{tabla.loc[i, 'cantidad']:10.2f}  "
                  f"{tabla.loc[i, 'unidad']}")
        numero = len(tabla.groupby("donacion").groups)
        print(f"Total: {numero} donacion(es), {len(tabla)} lote(s) y "
              f"{tabla['cantidad'].sum():.2f} recibidos.")

    def regEntrega(self):
        beneficiarios = self.__banco.beneficiarios
        productos = self.__banco.productos
        if len(beneficiarios) == 0 or len(self.__banco.lotes) == 0:
            print("Primero registre un beneficiario y una donacion.")
            return
        benef = beneficiarios[leerCodExist(beneficiarios, "Codigo del beneficiario: ")]
        print(f"Beneficiario seleccionado: {benef.nombre}")
        fecha = leerFechaHasta("Fecha de entrega (AAAA-MM-DD): ", self.__banco.hoy)
        producto = productos[leerCodExist(productos, "Codigo del producto: ")]
        validos = {}
        for lote in self.__banco.lotesValidos(producto, fecha):
            validos[lote.codigo] = lote
            print(f"  {lote.codigo}: {lote.disponible:.2f} disponibles, vence {lote.vence}")
        if len(validos) == 0:
            print("No hay lotes de ese producto con stock, sin vencer y recibidos hasta esa fecha.")
            return
        codLote = leerTexto("Codigo del lote: ").upper()
        while codLote not in validos:
            print("Error: lote no valido, sin stock, vencido o recibido despues de la entrega.")
            codLote = leerTexto("Codigo del lote: ").upper()
        lote = validos[codLote]
        cant = leerCantidad("Cantidad a entregar: ")
        while cant > lote.disponible:
            print(f"Error: solo hay {lote.disponible:.2f} disponibles.")
            cant = leerCantidad("Cantidad a entregar: ")
        entrega = self.__banco.regEntrega(benef, fecha, lote, cant)
        self.__guardar()
        print(f"Entrega {entrega.codigo} registrada. Quedan {lote.disponible:.2f} en el lote "
              f"{lote.codigo}.")

    def listEntregas(self):
        entregas = self.__banco.entregas
        if len(entregas) == 0:
            print("No hay entregas registradas.")
            return
        print(f"{'Cod':6}{'Fecha':12}{'Beneficiario':28}{'Cantidad':>10}  {'Lote':6}Producto")
        for entrega in entregas.values():
            print(entrega)

    # Historial de entregas de un beneficiario
    def histBenef(self):
        beneficiarios = self.__banco.beneficiarios
        if len(beneficiarios) == 0:
            print("No hay beneficiarios registrados.")
            return
        codigo = leerCodExist(beneficiarios, "Codigo del beneficiario: ")
        tabla = self.__reportes.historialBenef(codigo)
        if len(tabla) == 0:
            print("Este beneficiario todavia no tiene entregas registradas.")
            return
        print(f"Historial de entregas a {beneficiarios[codigo].nombre}:")
        print(f"{'Entrega':9}{'Fecha':12}{'Lote':6}{'Producto':20}{'Cantidad':>10}  Unidad")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'entrega']:9}{tabla.loc[i, 'fecha']:12}{tabla.loc[i, 'lote']:6}"
                  f"{tabla.loc[i, 'producto']:20}{tabla.loc[i, 'cantidad']:10.2f}  "
                  f"{tabla.loc[i, 'unidad']}")
        print(f"Total: {len(tabla)} entrega(s) y {tabla['cantidad'].sum():.2f} recibidos.")

    def listLotes(self):
        tabla = self.__banco.tablaLotes()
        if len(tabla) == 0:
            print("No hay lotes registrados.")
            return
        print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}{'Dias':>5}  Estado")
        for i in tabla.index:
            print(f"{tabla.loc[i, 'lote']:6}{tabla.loc[i, 'producto']:20}"
                  f"{tabla.loc[i, 'disponible']:10.2f}  {tabla.loc[i, 'vence']:12}"
                  f"{tabla.loc[i, 'dias']:5}  {tabla.loc[i, 'estado']}")

    def lotesProx(self):
        tabla = self.__reportes.lotesProximos()
        if len(tabla) == 0:
            print(f"No hay lotes con stock que venzan en {DIAS_ALERTA} dias o menos.")
            return
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
            print(f"Lote {lote.codigo}: se pierden {cantidad:.2f}")
            tot += cantidad
        if len(bajas) > 0:
            self.__guardar()
        print(f"Total registrado como perdida: {tot:.2f}")

    # Permite simular otra fecha para revisar alertas y vencimientos
    def cambiarFecha(self):
        print(f"Fecha de operacion actual: {self.__banco.hoy}")
        self.__banco.hoy = leerFecha("Nueva fecha de operacion (AAAA-MM-DD): ")
        print("Fecha de operacion actualizada.")
        self.alertas()

    def menuGraficos(self):
        while True:
            opcion = input("\n--- GRAFICOS ---\n1. Total donado por donante (barras)\n"
                           "2. Evolucion mensual recibido/entregado (lineas)\n"
                           "3. Stock por categoria (pastel)\n4. Entregas por categoria (pastel)\n"
                           "5. Perdidas por vencimiento segun categoria (barras)\n"
                           "6. Aprovechamiento general y por periodo\n"
                           "7. Ranking de beneficiarios\n8. Volver\nOpcion: ")
            if opcion == "1":
                self.__graficos.graficoDonantes()
            elif opcion == "2":
                self.__graficos.graficoMensual()
            elif opcion == "3":
                self.__graficos.graficoStockCat()
            elif opcion == "4":
                self.__graficos.graficoEntCat()
            elif opcion == "5":
                self.__graficos.graficoPerdidas()
            elif opcion == "6":
                self.__graficos.graficoAprovecha()
            elif opcion == "7":
                self.__graficos.graficoBenef()
            elif opcion == "8":
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
            opcion = input("\n--- DONACIONES ---\n1. Registrar donacion (uno o mas lotes)\n"
                           "2. Listar donaciones\n3. Historial por donante\n4. Volver\nOpcion: ")
            if opcion == "1":
                self.regDonacion()
            elif opcion == "2":
                self.listDonaciones()
            elif opcion == "3":
                self.histDonante()
            elif opcion == "4":
                break
            else:
                print("Opcion no valida.")

    def menuEntregas(self):
        while True:
            opcion = input("\n--- ENTREGAS ---\n1. Registrar entrega\n2. Listar entregas\n"
                           "3. Historial por beneficiario\n4. Volver\nOpcion: ")
            if opcion == "1":
                self.regEntrega()
            elif opcion == "2":
                self.listEntregas()
            elif opcion == "3":
                self.histBenef()
            elif opcion == "4":
                break
            else:
                print("Opcion no valida.")

    def menuStock(self):
        while True:
            opcion = input(f"\n--- STOCK Y VENCIMIENTOS (hoy: {self.__banco.hoy}) ---\n"
                           "1. Stock por categoria y producto\n2. Lotes y su estado\n"
                           "3. Lotes proximos a vencer\n4. Registrar perdidas por vencimiento\n"
                           "5. Cambiar fecha de operacion\n6. Volver\nOpcion: ")
            if opcion == "1":
                self.__reportes.verStock()
            elif opcion == "2":
                self.listLotes()
            elif opcion == "3":
                self.lotesProx()
            elif opcion == "4":
                self.regPerdidas()
            elif opcion == "5":
                self.cambiarFecha()
            elif opcion == "6":
                break
            else:
                print("Opcion no valida.")

    def menuReportes(self):
        while True:
            opcion = input("\n--- REPORTES ---\n1. Ranking de donantes\n2. Ranking de beneficiarios\n"
                           "3. Aprovechamiento general y por periodo\n4. Indicadores mensuales\n"
                           "5. Comparacion entre categorias\n6. Donaciones por tipo de donante\n"
                           "7. Resumen por producto\n8. Graficos\n9. Volver\nOpcion: ")
            if opcion == "1":
                self.__reportes.verRankingDon()
            elif opcion == "2":
                self.__reportes.verRankingBen()
            elif opcion == "3":
                self.__reportes.verAprovecha()
            elif opcion == "4":
                self.__reportes.verMensual()
            elif opcion == "5":
                self.__reportes.verCategorias()
            elif opcion == "6":
                self.__reportes.verTipos()
            elif opcion == "7":
                self.__reportes.verProductos()
            elif opcion == "8":
                self.menuGraficos()
            elif opcion == "9":
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


# Solo para editores en linea (PyTogether): si no hay datos guardados, crea los datos de prueba en CSV
DATOS_PRUEBA = {
    "donantes.csv": """codigo,nombre,tipo,contacto
DN01,Mercado Santa Rosa,Mercado,987654321
DN02,Distribuidora Andina,Empresa,914567890
DN03,Panaderia El Trigal,Empresa,956123478
DN04,Maria Lopez,Persona,923456781
DN05,Mercado Central,Mercado,945678123
""",
    "beneficiarios.csv": """codigo,nombre,tipo,personas
BF01,Comedor Santa Rosa,Comedor Popular,120
BF02,Albergue San Martin,Albergue,45
BF03,Olla Comun Los Olivos,Olla Comun,80
BF04,Comedor Virgen De Fatima,Comedor Popular,150
""",
    "productos.csv": """codigo,nombre,categoria,unidad
PR01,Arroz Extra,Granos,Kg
PR02,Leche Evaporada,Lacteos,Unidades
PR03,Atun En Conserva,Conservas,Unidades
PR04,Lentejas,Granos,Kg
PR05,Manzana,Frutas/Verduras,Kg
PR06,Yogurt,Lacteos,Litros
PR07,Aceite Vegetal,Otra,Litros
PR08,Papa Amarilla,Frutas/Verduras,Kg
""",
    "donaciones.csv": """codigo,donante,fecha
D1,DN01,2026-09-05
D2,DN02,2026-09-12
D3,DN05,2026-09-20
D4,DN03,2026-10-03
D5,DN04,2026-10-12
D6,DN02,2026-10-18
D7,DN05,2026-10-28
D8,DN01,2026-11-02
""",
    "lotes.csv": """codigo,donacion,producto,ingreso,vence,recibido,disponible,perdido
L1,D1,PR01,2026-09-05,2027-03-31,200,90,0
L2,D1,PR04,2026-09-05,2027-02-28,80,50,0
L3,D2,PR03,2026-09-12,2028-01-15,240,140,0
L4,D3,PR05,2026-09-20,2026-09-30,90,0,20
L5,D3,PR08,2026-09-20,2026-10-20,150,0,40
L6,D4,PR02,2026-10-03,2027-02-10,180,130,0
L7,D4,PR06,2026-10-03,2026-10-25,60,0,30
L8,D5,PR05,2026-10-12,2026-10-25,60,0,35
L9,D6,PR04,2026-10-18,2027-06-30,120,90,0
L10,D6,PR07,2026-10-18,2027-10-30,90,60,0
L11,D7,PR08,2026-10-28,2026-11-10,200,125,0
L12,D7,PR05,2026-10-28,2026-11-09,80,55,0
L13,D8,PR01,2026-11-02,2027-05-31,300,300,0
L14,D8,PR06,2026-11-02,2026-11-12,40,40,0
""",
    "entregas.csv": """codigo,beneficiario,fecha,lote,cantidad
E1,BF01,2026-09-08,L1,50
E2,BF02,2026-09-15,L3,60
E3,BF03,2026-09-22,L4,40
E4,BF04,2026-09-25,L5,60
E5,BF02,2026-09-28,L4,30
E6,BF01,2026-09-30,L2,30
E7,BF04,2026-10-06,L6,50
E8,BF03,2026-10-10,L5,50
E9,BF01,2026-10-14,L7,30
E10,BF04,2026-10-16,L8,25
E11,BF02,2026-10-20,L9,30
E12,BF03,2026-10-25,L3,40
E13,BF01,2026-10-30,L11,75
E14,BF04,2026-11-01,L10,30
E15,BF02,2026-11-03,L1,60
E16,BF03,2026-11-04,L12,25
""",
}


# Devuelve True si el archivo ya existe
def existe(nombre):
    try:
        archivo = open(nombre, encoding="utf-8")
        archivo.close()
        return True
    except FileNotFoundError:
        return False


if not existe(ARCHIVO) and not existe("donantes.csv"):
    for nombre in DATOS_PRUEBA:
        archivo = open(nombre, "w", encoding="utf-8")
        archivo.write(DATOS_PRUEBA[nombre])
        archivo.close()

# Programa principal
app = Aplicacion()
app.iniciar()
