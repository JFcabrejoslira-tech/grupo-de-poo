# ==================================================================
# AlimGest - Sistema de Gestion de Banco de Alimentos y Donaciones
# Trabajo Final (primer hito) - 1ASI0781 Programacion Orientada a Objetos
#
# Version orientada a objetos:
#   - Clases con atributos privados, constructores, getters y setters
#   - Herencia: Entidad -> Donante, Beneficiario, Producto
#               Movimiento -> Donacion, Entrega
#   - Persistencia en archivos CSV con pandas (carpeta "datos")
#   - Graficos con matplotlib (carpeta "graficos")
#
# Requisitos: pip install pandas matplotlib
# ==================================================================
import os
from datetime import date

import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# CONSTANTES
# ------------------------------------------------------------------
TIPOS_DONANTE = ("Empresa", "Mercado", "Persona")
TIPOS_ORG = ("Comedor Popular", "Albergue", "Olla Comun", "Otra")
CATEGORIAS = ("Granos", "Conservas", "Lacteos", "Frutas/Verduras", "Otra")
UNIDADES = ("Kg", "Litros", "Unidades")
DIAS_ALERTA = 7
MAX_CANTIDAD = 1000000
CARPETA_DATOS = "datos"
CARPETA_GRAF = "graficos"
COLORES = ("#2E7D4F", "#F28C28", "#5B9BD5", "#F6C453", "#8FA89A", "#C2441F")

# Columnas de cada archivo CSV
COLS_DONANTE = ("codigo", "nombre", "tipo", "contacto")
COLS_BENEF = ("codigo", "nombre", "tipo", "personas")
COLS_PRODUCTO = ("codigo", "nombre", "categoria", "unidad")
COLS_LOTE = ("codigo", "producto", "ingreso", "vence", "recibido", "disponible", "perdido")
COLS_DONACION = ("donante", "fecha", "producto", "lote", "cantidad")
COLS_ENTREGA = ("beneficiario", "fecha", "producto", "lote", "cantidad")


# ------------------------------------------------------------------
# FUNCIONES DE LECTURA Y VALIDACION (consola)
# ------------------------------------------------------------------
# Pide un texto y no deja que quede vacio
def leerTexto(mensaje):
    texto = input(mensaje).strip()
    while texto == "":
        print("Error: no puede estar vacio.")
        texto = input(mensaje).strip()
    return texto


# Pide un numero entero mayor que cero
def leerEntero(mensaje):
    while True:
        try:
            numero = int(input(mensaje))
            if numero > 0:
                return numero
            print("Error: ingrese un numero entero mayor que cero.")
        except ValueError:
            print("Error: ingrese un numero entero mayor que cero.")


# Pide una cantidad mayor que cero y que no pase de MAX_CANTIDAD
def leerCantidad(mensaje):
    while True:
        try:
            numero = float(input(mensaje))
            if numero > MAX_CANTIDAD:
                print(f"Error: la cantidad no puede ser mayor que {MAX_CANTIDAD}.")
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


# Pide un codigo que todavia no exista en el diccionario
def leerCodNuevo(existentes, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo in existentes:
        print("Error: ese codigo ya existe.")
        codigo = leerTexto(mensaje).upper()
    return codigo


# Pide un codigo que si exista en el diccionario
def leerCodExist(existentes, mensaje):
    codigo = leerTexto(mensaje).upper()
    while codigo not in existentes:
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


# Convierte un texto AAAA-MM-DD en un objeto date (None si no es valido)
def textoAFecha(texto):
    partes = texto.strip().split("-")
    if len(partes) != 3:
        return None
    try:
        return date(int(partes[0]), int(partes[1]), int(partes[2]))
    except ValueError:
        return None


# Pide una fecha valida (date controla los meses y los anios bisiestos)
def leerFecha(mensaje):
    fecha = textoAFecha(input(mensaje))
    while fecha is None:
        print("Error: use el formato AAAA-MM-DD (ejemplo 2026-09-29).")
        fecha = textoAFecha(input(mensaje))
    return fecha


# ==================================================================
# CLASES DEL DOMINIO
# ==================================================================
class Entidad:
    """Clase base de todo registro que tiene codigo y nombre."""

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


class Donante(Entidad):
    """Empresa, mercado o persona que dona alimentos."""

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

    # Devuelve los datos como diccionario (una fila del CSV)
    def aFila(self):
        return {"codigo": self.getCodigo(), "nombre": self.getNombre(),
                "tipo": self.__tipo, "contacto": self.__contacto}

    def __str__(self):
        return f"{self.getCodigo():8}{self.getNombre():28}{self.__tipo:10}{self.__contacto}"


class Beneficiario(Entidad):
    """Organizacion que recibe alimentos (comedor, albergue, olla comun)."""

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
    """Alimento del catalogo, con su categoria y unidad de medida."""

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


class Lote:
    """Cantidad de un producto recibida en una donacion, con su vencimiento."""

    def __init__(self, codigo, producto, ingreso, vence, recibido, disponible, perdido):
        self.__codigo = codigo
        self.__producto = producto        # objeto Producto
        self.__ingreso = ingreso          # date
        self.__vence = vence              # date
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

    # Dias que faltan para vencer (negativo si ya vencio)
    def diasParaVencer(self, hoy):
        return (self.__vence - hoy).days

    # Clasifica el lote segun los dias que le faltan para vencer
    def estado(self, hoy):
        dias = self.diasParaVencer(hoy)
        if dias < 0:
            return "Vencido"
        elif dias <= DIAS_ALERTA:
            return "Proximo a vencer"
        return "Disponible"

    # El lote sirve si tiene stock, ya ingreso y no vence antes de la fecha
    def sirveParaEntrega(self, fecha):
        return self.__disponible > 0 and self.__ingreso <= fecha <= self.__vence

    # Descuenta una entrega; no permite dejar el stock en negativo
    def descontar(self, cantidad):
        if cantidad <= 0 or cantidad > self.__disponible:
            return False
        self.__disponible -= cantidad
        return True

    # Pasa lo que queda del lote a perdida y devuelve esa cantidad
    def darDeBaja(self):
        remanente = self.__disponible
        self.__perdido += remanente
        self.__disponible = 0.0
        return remanente

    def aFila(self):
        return {"codigo": self.__codigo, "producto": self.__producto.getCodigo(),
                "ingreso": self.__ingreso.isoformat(), "vence": self.__vence.isoformat(),
                "recibido": self.__recibido, "disponible": self.__disponible,
                "perdido": self.__perdido}


class Movimiento:
    """Clase base de las operaciones que mueven alimentos de un lote."""

    def __init__(self, fecha, lote, cantidad):
        self.__fecha = fecha          # date
        self.__lote = lote            # objeto Lote
        self.__cantidad = cantidad

    def getFecha(self):
        return self.__fecha

    def getLote(self):
        return self.__lote

    def getCantidad(self):
        return self.__cantidad

    def getProducto(self):
        return self.__lote.getProducto()


class Donacion(Movimiento):
    """Ingreso de alimentos: un donante entrega un lote."""

    def __init__(self, donante, fecha, lote, cantidad):
        super().__init__(fecha, lote, cantidad)
        self.__donante = donante      # objeto Donante

    def getDonante(self):
        return self.__donante

    def aFila(self):
        return {"donante": self.__donante.getCodigo(), "fecha": self.getFecha().isoformat(),
                "producto": self.getProducto().getCodigo(),
                "lote": self.getLote().getCodigo(), "cantidad": self.getCantidad()}


class Entrega(Movimiento):
    """Salida de alimentos: un lote se entrega a un beneficiario."""

    def __init__(self, beneficiario, fecha, lote, cantidad):
        super().__init__(fecha, lote, cantidad)
        self.__beneficiario = beneficiario    # objeto Beneficiario

    def getBeneficiario(self):
        return self.__beneficiario

    def aFila(self):
        return {"beneficiario": self.__beneficiario.getCodigo(),
                "fecha": self.getFecha().isoformat(),
                "producto": self.getProducto().getCodigo(),
                "lote": self.getLote().getCodigo(), "cantidad": self.getCantidad()}


# ==================================================================
# CLASE PRINCIPAL DEL NEGOCIO
# ==================================================================
class BancoAlimentos:
    """Guarda todos los objetos del sistema y aplica sus reglas."""

    def __init__(self):
        self.__donantes = {}          # codigo -> Donante
        self.__beneficiarios = {}     # codigo -> Beneficiario
        self.__productos = {}         # codigo -> Producto
        self.__lotes = {}             # codigo -> Lote
        self.__donaciones = []        # lista de Donacion
        self.__entregas = []          # lista de Entrega
        self.__hoy = date.today()     # fecha de operacion

    # ---------- fecha de operacion ----------
    def getHoy(self):
        return self.__hoy

    def setHoy(self, hoy):
        self.__hoy = hoy

    # ---------- donantes ----------
    def getDonantes(self):
        return dict(self.__donantes)

    def getDonante(self, codigo):
        return self.__donantes.get(codigo)

    def agregarDonante(self, donante):
        self.__donantes[donante.getCodigo()] = donante

    # Cambia la llave del diccionario y el codigo del objeto
    def cambiarCodDon(self, viejo, nuevo):
        donante = self.__donantes.pop(viejo)
        donante.setCodigo(nuevo)
        self.__donantes[nuevo] = donante

    # ---------- beneficiarios ----------
    def getBeneficiarios(self):
        return dict(self.__beneficiarios)

    def getBeneficiario(self, codigo):
        return self.__beneficiarios.get(codigo)

    def agregarBenef(self, beneficiario):
        self.__beneficiarios[beneficiario.getCodigo()] = beneficiario

    def cambiarCodBenef(self, viejo, nuevo):
        beneficiario = self.__beneficiarios.pop(viejo)
        beneficiario.setCodigo(nuevo)
        self.__beneficiarios[nuevo] = beneficiario

    # ---------- productos ----------
    def getProductos(self):
        return dict(self.__productos)

    def getProducto(self, codigo):
        return self.__productos.get(codigo)

    def agregarProducto(self, producto):
        self.__productos[producto.getCodigo()] = producto

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

    # ---------- lotes y donaciones ----------
    def getLotes(self):
        return dict(self.__lotes)

    def getLote(self, codigo):
        return self.__lotes.get(codigo)

    def agregarLote(self, lote):
        self.__lotes[lote.getCodigo()] = lote

    def agregarDonacion(self, donacion):
        self.__donaciones.append(donacion)

    def getDonaciones(self):
        return list(self.__donaciones)

    # Devuelve el codigo de un lote del mismo producto y vencimiento ("" si no hay)
    def loteDuplicado(self, producto, vence):
        for lote in self.__lotes.values():
            if lote.getProducto() == producto and lote.getVence() == vence:
                return lote.getCodigo()
        return ""

    # Crea el lote (L1, L2, L3...) y guarda la donacion en el historial
    def regDonacion(self, donante, fecha, producto, cantidad, vence):
        codigo = f"L{len(self.__lotes) + 1}"
        lote = Lote(codigo, producto, fecha, vence, cantidad, cantidad, 0.0)
        self.__lotes[codigo] = lote
        self.__donaciones.append(Donacion(donante, fecha, lote, cantidad))
        return lote

    # ---------- entregas ----------
    def agregarEntrega(self, entrega):
        self.__entregas.append(entrega)

    def getEntregas(self):
        return list(self.__entregas)

    # Lotes del producto que se pueden entregar en esa fecha
    def lotesValidos(self, producto, fecha):
        validos = []
        for lote in self.__lotes.values():
            if lote.getProducto() == producto and lote.sirveParaEntrega(fecha):
                validos.append(lote)
        return validos

    # Registra la entrega solo si el lote sirve y hay stock suficiente
    def regEntrega(self, beneficiario, fecha, lote, cantidad):
        if not lote.sirveParaEntrega(fecha):
            return False
        if not lote.descontar(cantidad):
            return False
        self.__entregas.append(Entrega(beneficiario, fecha, lote, cantidad))
        return True

    def entregasDe(self, beneficiario):
        lista = []
        for entrega in self.__entregas:
            if entrega.getBeneficiario() == beneficiario:
                lista.append(entrega)
        return lista

    # ---------- vencimientos y perdidas ----------
    def lotesProximos(self):
        lista = []
        for lote in self.__lotes.values():
            if lote.estado(self.__hoy) == "Proximo a vencer" and lote.getDisponible() > 0:
                lista.append(lote)
        lista.sort(key=Lote.getVence)
        return lista

    # Da de baja los lotes vencidos con saldo y devuelve (lote, cantidad)
    def regPerdidas(self):
        bajas = []
        for lote in self.__lotes.values():
            if lote.estado(self.__hoy) == "Vencido" and lote.getDisponible() > 0:
                bajas.append((lote, lote.darDeBaja()))
        return bajas

    # ---------- totales ----------
    def totalRecibido(self):
        total = 0
        for lote in self.__lotes.values():
            total += lote.getRecibido()
        return total

    def totalEntregado(self):
        total = 0
        for entrega in self.__entregas:
            total += entrega.getCantidad()
        return total

    def totalPerdido(self):
        total = 0
        for lote in self.__lotes.values():
            total += lote.getPerdido()
        return total

    def totalEnStock(self):
        total = 0
        for lote in self.__lotes.values():
            total += lote.getDisponible()
        return total

    # ---------- tablas de pandas para los reportes ----------
    def tablaDonaciones(self):
        filas = []
        for donacion in self.__donaciones:
            producto = donacion.getProducto()
            filas.append({"donante": donacion.getDonante().getNombre(),
                          "tipo": donacion.getDonante().getTipo(),
                          "producto": producto.getNombre(),
                          "unidad": producto.getUnidad(),
                          "fecha": donacion.getFecha().isoformat(),
                          "lote": donacion.getLote().getCodigo(),
                          "cantidad": donacion.getCantidad()})
        return pd.DataFrame(filas, columns=["donante", "tipo", "producto", "unidad",
                                            "fecha", "lote", "cantidad"])

    def tablaEntregas(self):
        filas = []
        for entrega in self.__entregas:
            filas.append({"beneficiario": entrega.getBeneficiario().getNombre(),
                          "producto": entrega.getProducto().getNombre(),
                          "fecha": entrega.getFecha().isoformat(),
                          "lote": entrega.getLote().getCodigo(),
                          "cantidad": entrega.getCantidad()})
        return pd.DataFrame(filas, columns=["beneficiario", "producto", "fecha",
                                            "lote", "cantidad"])

    def tablaLotes(self):
        filas = []
        for lote in self.__lotes.values():
            producto = lote.getProducto()
            filas.append({"lote": lote.getCodigo(), "producto": producto.getNombre(),
                          "categoria": producto.getCategoria(),
                          "unidad": producto.getUnidad(),
                          "estado": lote.estado(self.__hoy),
                          "disponible": lote.getDisponible(),
                          "perdido": lote.getPerdido()})
        return pd.DataFrame(filas, columns=["lote", "producto", "categoria", "unidad",
                                            "estado", "disponible", "perdido"])


# ==================================================================
# PERSISTENCIA EN ARCHIVOS CSV (pandas)
# ==================================================================
class GestorArchivos:
    """Lee y escribe los datos del banco en archivos CSV."""

    def __init__(self, carpeta):
        self.__carpeta = carpeta

    def __ruta(self, nombre):
        return os.path.join(self.__carpeta, nombre + ".csv")

    # Lee un CSV como texto; devuelve una lista de filas (diccionarios)
    def __leer(self, nombre):
        ruta = self.__ruta(nombre)
        if not os.path.exists(ruta):
            return []
        tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        return tabla.to_dict("records")

    def __escribir(self, nombre, objetos, columnas):
        filas = []
        for objeto in objetos:
            filas.append(objeto.aFila())
        tabla = pd.DataFrame(filas, columns=list(columnas))
        tabla.to_csv(self.__ruta(nombre), index=False, encoding="utf-8-sig")

    # Carga los objetos en el banco; devuelve la cantidad de filas omitidas
    def cargar(self, banco):
        omitidas = 0
        for fila in self.__leer("donantes"):
            banco.agregarDonante(Donante(fila["codigo"], fila["nombre"],
                                         fila["tipo"], fila["contacto"]))
        for fila in self.__leer("beneficiarios"):
            banco.agregarBenef(Beneficiario(fila["codigo"], fila["nombre"],
                                            fila["tipo"], int(fila["personas"])))
        for fila in self.__leer("productos"):
            banco.agregarProducto(Producto(fila["codigo"], fila["nombre"],
                                           fila["categoria"], fila["unidad"]))
        for fila in self.__leer("lotes"):
            producto = banco.getProducto(fila["producto"])
            if producto is None:
                omitidas += 1
            else:
                banco.agregarLote(Lote(fila["codigo"], producto,
                                       textoAFecha(fila["ingreso"]),
                                       textoAFecha(fila["vence"]),
                                       float(fila["recibido"]), float(fila["disponible"]),
                                       float(fila["perdido"])))
        for fila in self.__leer("donaciones"):
            donante = banco.getDonante(fila["donante"])
            lote = banco.getLote(fila["lote"])
            if donante is None or lote is None:
                omitidas += 1
            else:
                banco.agregarDonacion(Donacion(donante, textoAFecha(fila["fecha"]),
                                               lote, float(fila["cantidad"])))
        for fila in self.__leer("entregas"):
            beneficiario = banco.getBeneficiario(fila["beneficiario"])
            lote = banco.getLote(fila["lote"])
            if beneficiario is None or lote is None:
                omitidas += 1
            else:
                banco.agregarEntrega(Entrega(beneficiario, textoAFecha(fila["fecha"]),
                                             lote, float(fila["cantidad"])))
        return omitidas

    # Guarda todos los objetos del banco en sus archivos CSV
    def guardar(self, banco):
        os.makedirs(self.__carpeta, exist_ok=True)
        self.__escribir("donantes", banco.getDonantes().values(), COLS_DONANTE)
        self.__escribir("beneficiarios", banco.getBeneficiarios().values(), COLS_BENEF)
        self.__escribir("productos", banco.getProductos().values(), COLS_PRODUCTO)
        self.__escribir("lotes", banco.getLotes().values(), COLS_LOTE)
        self.__escribir("donaciones", banco.getDonaciones(), COLS_DONACION)
        self.__escribir("entregas", banco.getEntregas(), COLS_ENTREGA)


# ==================================================================
# REPORTES (pandas) Y GRAFICOS (matplotlib)
# ==================================================================
class Reportes:
    """Calcula los reportes con pandas y los muestra en consola."""

    def __init__(self, banco):
        self.__banco = banco

    # ---------- calculos ----------
    def ranking(self):
        tabla = self.__banco.tablaDonaciones()
        return tabla.groupby("donante")["cantidad"].sum().sort_values(ascending=False)

    def porBeneficiario(self):
        tabla = self.__banco.tablaEntregas()
        return tabla.groupby("beneficiario")["cantidad"].sum().sort_values(ascending=False)

    def porTipoDonante(self):
        tabla = self.__banco.tablaDonaciones()
        return tabla.groupby("tipo")["cantidad"].sum().sort_values(ascending=False)

    def resumenProducto(self):
        recibido = self.__banco.tablaDonaciones().groupby("producto")["cantidad"].sum()
        entregado = self.__banco.tablaEntregas().groupby("producto")["cantidad"].sum()
        perdido = self.__banco.tablaLotes().groupby("producto")["perdido"].sum()
        resumen = pd.DataFrame({"recibido": recibido, "entregado": entregado,
                                "perdido": perdido}).fillna(0)
        resumen["stock"] = resumen["recibido"] - resumen["entregado"] - resumen["perdido"]
        return resumen.sort_values("recibido", ascending=False)

    def stockPorCat(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        return tabla.groupby("categoria")["disponible"].sum()

    # ---------- reportes en consola ----------
    def verStock(self):
        tabla = self.__banco.tablaLotes()
        tabla = tabla[tabla["estado"] != "Vencido"]
        stock = tabla.groupby(["categoria", "producto", "unidad"])["disponible"].sum()
        print(f"\n{'Categoria':16}{'Producto':20}{'Stock':>10}  Unidad")
        if len(stock) == 0:
            print("No hay stock disponible.")
        for categoria in CATEGORIAS:
            for clave, cantidad in stock.items():
                if clave[0] == categoria:
                    print(f"{categoria:16}{clave[1]:20}{cantidad:10.2f}  {clave[2]}")

    def verRanking(self):
        datos = self.ranking()
        if len(datos) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Puesto':8}{'Donante':28}{'Total':>10}")
        puesto = 1
        for nombre, total in datos.items():
            print(f"{puesto:<8}{nombre:28}{total:10.2f}")
            puesto += 1

    def verBeneficiarios(self):
        datos = self.porBeneficiario()
        if len(datos) == 0:
            print("No hay entregas registradas.")
            return
        print(f"\n{'Beneficiario':28}{'Total':>10}")
        for nombre, total in datos.items():
            print(f"{nombre:28}{total:10.2f}")

    def verAprovecha(self):
        recibido = self.__banco.totalRecibido()
        if recibido == 0:
            print("No hay donaciones registradas.")
            return
        entregado = self.__banco.totalEntregado()
        perdido = self.__banco.totalPerdido()
        print(f"\nRecibido:   {recibido:10.2f}")
        print(f"Entregado:  {entregado:10.2f}  ({entregado / recibido * 100:.2f}% aprovechado)")
        print(f"Perdido:    {perdido:10.2f}  ({perdido / recibido * 100:.2f}% desperdiciado)")
        print(f"En almacen: {self.__banco.totalEnStock():10.2f}")

    def verTipos(self):
        datos = self.porTipoDonante()
        if len(datos) == 0:
            print("No hay donaciones registradas.")
            return
        total = datos.sum()
        print(f"\n{'Tipo':12}{'Cantidad':>10}{'Porcentaje':>12}")
        for tipo, cantidad in datos.items():
            print(f"{tipo:12}{cantidad:10.2f}{cantidad / total * 100:11.2f}%")

    def verProductos(self):
        resumen = self.resumenProducto()
        if len(resumen) == 0:
            print("No hay donaciones registradas.")
            return
        print(f"\n{'Producto':20}{'Recibido':>10}{'Entregado':>11}{'Perdido':>9}{'Stock':>9}")
        for nombre, fila in resumen.iterrows():
            print(f"{nombre:20}{fila['recibido']:10.2f}{fila['entregado']:11.2f}"
                  f"{fila['perdido']:9.2f}{fila['stock']:9.2f}")


class Graficos:
    """Dibuja los reportes con matplotlib y los guarda como imagen PNG."""

    def __init__(self, reportes, banco, carpeta):
        self.__reportes = reportes
        self.__banco = banco
        self.__carpeta = carpeta

    # Guarda la figura actual, la muestra y devuelve la ruta del archivo
    def __guardar(self, nombre):
        os.makedirs(self.__carpeta, exist_ok=True)
        ruta = os.path.join(self.__carpeta, nombre + ".png")
        plt.tight_layout()
        plt.savefig(ruta, dpi=150)
        plt.show()
        plt.close()
        print(f"Grafico guardado en {ruta}")
        return ruta

    def __barras(self, datos, titulo, etiqueta, nombre, horizontal):
        if len(datos) == 0:
            print("No hay datos para el grafico.")
            return ""
        figura, eje = plt.subplots(figsize=(9, 5))
        if horizontal:
            barras = eje.barh(list(datos.index), list(datos.values), color=COLORES[0])
            eje.invert_yaxis()
            eje.set_xlabel(etiqueta)
        else:
            barras = eje.bar(list(datos.index), list(datos.values), color=COLORES[0])
            eje.set_ylabel(etiqueta)
            plt.xticks(rotation=15, ha="right")
        eje.bar_label(barras, fmt="%.0f", padding=3)
        eje.set_title(titulo, fontsize=14, fontweight="bold")
        eje.spines["top"].set_visible(False)
        eje.spines["right"].set_visible(False)
        return self.__guardar(nombre)

    def __torta(self, valores, etiquetas, titulo, nombre):
        if sum(valores) == 0:
            print("No hay datos para el grafico.")
            return ""
        figura, eje = plt.subplots(figsize=(7, 6))
        eje.pie(valores, labels=etiquetas, autopct="%1.1f%%", startangle=90,
                colors=COLORES[:len(valores)], wedgeprops={"edgecolor": "white"})
        eje.set_title(titulo, fontsize=14, fontweight="bold")
        return self.__guardar(nombre)

    def graficoRanking(self):
        return self.__barras(self.__reportes.ranking(), "Ranking de donantes",
                             "Cantidad donada", "ranking_donantes", False)

    def graficoBenef(self):
        return self.__barras(self.__reportes.porBeneficiario(),
                             "Total entregado por beneficiario", "Cantidad entregada",
                             "entregas_beneficiario", True)

    def graficoAprovecha(self):
        valores = [self.__banco.totalEntregado(), self.__banco.totalPerdido(),
                   self.__banco.totalEnStock()]
        return self.__torta(valores, ["Entregado", "Perdido", "En almacen"],
                            "Aprovechamiento y perdidas", "aprovechamiento")

    def graficoTipos(self):
        datos = self.__reportes.porTipoDonante()
        return self.__torta(list(datos.values), list(datos.index),
                            "Donaciones por tipo de donante", "tipos_donante")

    def graficoStock(self):
        return self.__barras(self.__reportes.stockPorCat(),
                             "Stock disponible por categoria", "Cantidad en stock",
                             "stock_categoria", False)

    def graficoProductos(self):
        resumen = self.__reportes.resumenProducto()
        if len(resumen) == 0:
            print("No hay datos para el grafico.")
            return ""
        figura, eje = plt.subplots(figsize=(10, 5))
        resumen[["recibido", "entregado", "perdido"]].plot(
            kind="bar", ax=eje, color=[COLORES[2], COLORES[0], COLORES[1]], width=0.8)
        eje.set_title("Recibido, entregado y perdido por producto", fontsize=14,
                      fontweight="bold")
        eje.set_xlabel("")
        eje.set_ylabel("Cantidad")
        eje.legend(["Recibido", "Entregado", "Perdido"])
        plt.xticks(rotation=20, ha="right")
        eje.spines["top"].set_visible(False)
        eje.spines["right"].set_visible(False)
        return self.__guardar("resumen_productos")


# ==================================================================
# INTERFAZ DE CONSOLA (menus)
# ==================================================================
class Aplicacion:
    """Muestra los menus, pide los datos y usa las demas clases."""

    def __init__(self):
        self.__banco = BancoAlimentos()
        self.__archivos = GestorArchivos(CARPETA_DATOS)
        self.__reportes = Reportes(self.__banco)
        self.__graficos = Graficos(self.__reportes, self.__banco, CARPETA_GRAF)

    def __guardar(self):
        self.__archivos.guardar(self.__banco)

    # Carga los CSV y abre el menu principal
    # (la fecha de operacion se toma del sistema con date.today())
    def iniciar(self):
        omitidas = self.__archivos.cargar(self.__banco)
        print("===== AlimGest: Sistema de Gestion de Banco de Alimentos =====")
        print(f"Datos cargados: {len(self.__banco.getDonantes())} donantes, "
              f"{len(self.__banco.getBeneficiarios())} beneficiarios, "
              f"{len(self.__banco.getProductos())} productos y "
              f"{len(self.__banco.getLotes())} lotes.")
        if omitidas > 0:
            print(f"Aviso: se omitieron {omitidas} filas con datos inconsistentes.")
        print(f"Fecha de operacion: {self.__banco.getHoy().isoformat()}")
        self.menuPrincipal()

    # ---------------- 1. Donantes ----------------
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

    # ---------------- 2. Beneficiarios ----------------
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

    # ---------------- 3. Productos ----------------
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

    # ---------------- 4. Donaciones ----------------
    def regDonacion(self):
        donantes = self.__banco.getDonantes()
        productos = self.__banco.getProductos()
        if len(donantes) == 0 or len(productos) == 0:
            print("Primero registre un donante y un producto.")
            return
        hoy = self.__banco.getHoy()
        donante = donantes[leerCodExist(donantes, "Codigo del donante: ")]
        print(f"Donante seleccionado: {donante.getNombre()}")
        fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
        while fecha > hoy:
            print("Error: la fecha de donacion no puede ser posterior a hoy.")
            fecha = leerFecha("Fecha de donacion (AAAA-MM-DD): ")
        producto = productos[leerCodExist(productos, "Codigo del producto: ")]
        unidad = producto.getUnidad()
        print(f"Producto seleccionado: {producto.getNombre()} ({unidad})")
        cantidad = leerCantidad(f"Cantidad recibida ({unidad}): ")
        vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
        while vence < fecha:
            print("Error: el vencimiento no puede ser antes de la donacion.")
            vence = leerFecha("Fecha de vencimiento (AAAA-MM-DD): ")
        if vence < hoy:
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
        print(f"{'Donante':28}{'Fecha':12}{'Producto':20}{'Lote':6}{'Cantidad':>10}")
        for donacion in donaciones:
            print(f"{donacion.getDonante().getNombre():28}"
                  f"{donacion.getFecha().isoformat():12}"
                  f"{donacion.getProducto().getNombre():20}"
                  f"{donacion.getLote().getCodigo():6}{donacion.getCantidad():10.2f}")

    # ---------------- 5. Entregas ----------------
    def regEntrega(self):
        beneficiarios = self.__banco.getBeneficiarios()
        productos = self.__banco.getProductos()
        if len(beneficiarios) == 0 or len(self.__banco.getLotes()) == 0:
            print("Primero registre un beneficiario y una donacion.")
            return
        benef = beneficiarios[leerCodExist(beneficiarios, "Codigo del beneficiario: ")]
        print(f"Beneficiario seleccionado: {benef.getNombre()}")
        fecha = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
        while fecha > self.__banco.getHoy():
            print("Error: la fecha de entrega no puede ser posterior a hoy.")
            fecha = leerFecha("Fecha de entrega (AAAA-MM-DD): ")
        producto = productos[leerCodExist(productos, "Codigo del producto: ")]
        validos = {}
        for lote in self.__banco.lotesValidos(producto, fecha):
            validos[lote.getCodigo()] = lote
            print(f"  {lote.getCodigo()}: {lote.getDisponible():.2f} disponibles, "
                  f"vence {lote.getVence().isoformat()}")
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

    def detEntregas(self):
        beneficiarios = self.__banco.getBeneficiarios()
        if len(beneficiarios) == 0:
            print("No hay beneficiarios registrados.")
            return
        benef = beneficiarios[leerCodExist(beneficiarios, "Codigo del beneficiario: ")]
        encontradas = self.__banco.entregasDe(benef)
        if len(encontradas) == 0:
            print("Este beneficiario todavia no tiene entregas registradas.")
            return
        print(f"Entregas a {benef.getNombre()}:")
        print(f"{'Fecha':12}{'Lote':6}{'Producto':20}{'Cantidad':>10}")
        total = 0
        for entrega in encontradas:
            print(f"{entrega.getFecha().isoformat():12}{entrega.getLote().getCodigo():6}"
                  f"{entrega.getProducto().getNombre():20}{entrega.getCantidad():10.2f}")
            total += entrega.getCantidad()
        print(f"Total entregado: {total:.2f}")

    # ---------------- 6. Stock y vencimientos ----------------
    def listLotes(self):
        hoy = self.__banco.getHoy()
        print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}{'Dias':>5}  Estado")
        for lote in self.__banco.getLotes().values():
            print(f"{lote.getCodigo():6}{lote.getProducto().getNombre():20}"
                  f"{lote.getDisponible():10.2f}  {lote.getVence().isoformat():12}"
                  f"{lote.diasParaVencer(hoy):5d}  {lote.estado(hoy)}")

    def lotesProx(self):
        hoy = self.__banco.getHoy()
        print(f"{'Lote':6}{'Producto':20}{'Disponible':>10}  {'Vence':12}{'Dias':>5}")
        comp = 0
        for lote in self.__banco.lotesProximos():
            print(f"{lote.getCodigo():6}{lote.getProducto().getNombre():20}"
                  f"{lote.getDisponible():10.2f}  {lote.getVence().isoformat():12}"
                  f"{lote.diasParaVencer(hoy):5d}")
            comp += lote.getDisponible()
        print(f"Cantidad comprometida: {comp:.2f}")

    def regPerdidas(self):
        bajas = self.__banco.regPerdidas()
        tot = 0
        for lote, cantidad in bajas:
            print(f"Lote {lote.getCodigo()}: se pierden {cantidad:.2f}")
            tot += cantidad
        if len(bajas) > 0:
            self.__guardar()
        print(f"Total registrado como perdida: {tot:.2f}")

    # ---------------- 7. Graficos ----------------
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

    # ---------------- Menus ----------------
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
                print(f"Datos guardados en la carpeta '{CARPETA_DATOS}'. Hasta pronto!")
                break
            else:
                print("Opcion no valida.")


# ------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Trabaja en la carpeta del archivo .py, asi "datos" y "graficos" quedan a su lado
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = Aplicacion()
    app.iniciar()
