from datos_json.json_manager import Administrador_JSON

# Librerías necesarias para las validaciones de JSON.

from json.decoder import JSONDecodeError
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# region Variables Globales (Esquemas para Validación de los JSON):

VALIDACION_SCHEMA_CARRITO = {
    "type": "object",
    "properties": {
        "idCarrito": {"type": "integer"},
        "productos": {
            "type": "array",
            "required": ["idProducto", "nombreProducto", "cantidadProducto", "precioProducto"]}},
    "required": ["idCarrito", "productos"]
}

VALIDACION_SCHEMA_PRODUCTO = {
    "type": "object",
    "properties": {
        "idProducto": {"type": "integer"},
        "nombreProducto": {"type": "string"},
        "cantidadProducto": {"type": "integer"},
        "precioProducto": {"type": "integer"}
    },
    "required": ["idProducto", "nombreProducto", "cantidadProducto", "precioProducto"]
}

VALIDACION_SCHEMA_USUARIO = {
    "type": "object",
    "properties": {
        "idUsuario": {"type": "integer"},
        "username": {"type": "string"},
        "password": {"type": "string"},
        "idCarrito": {"type": "integer"}
    },
    "required": ["idUsuario", "username", "password"]
}

# endregion

"""
Esta clase estará encargada de recibir y enviar la información a nuesta base de datos. En el caso de nuestro proyecto, 
estaremos usando archivos con formato JSON (carrito.json, productos.json y usuarios.json).
"""
class Modelo_DataRetriever():

    def __init__(self, nombre_campo, archivo_json, nombre_schema):
        self.nombre_campo  = nombre_campo
        self.json_manager  = Administrador_JSON(archivo_json)
        self.nombre_schema = nombre_schema

    def validar_datos(self, datos_a_validar):
        # Método para validar que los JSON procesados cumplan con el un formato válido y que sigan el esquema cargado.
        try:
            validate(datos_a_validar, self.nombre_schema)
            return True, None
        except ValidationError as error_esquema:
            mensaje_error  = f"JSON no cumple con el esquema: {error_esquema}" #? Fer, encontré una mejor simplificada para el formato de los string.
            #print(mensaje_error)
            return False, mensaje_error
        except JSONDecodeError as error_parseo:
            mensaje_error  = f"No es un JSON válido: {error_parseo}" 
            #print(mensaje_error)
            return False, mensaje_error
    
    def cargar_contenido(self):
        # Se carga con los contenidos de JSON enviado. 
        return self.json_manager.datos_json

    def select(self, id_elemento):
        # Carga un elemento que concuerde con el id_elemento.
        return self.json_manager.select_item(self.nombre_campo, id_elemento)

    def eliminar(self, id_elemento):
        #Elimina el dato que concuerde con el id_elemento.
        self.json_manager.delete_item(self.nombre_campo, id_elemento)

    def insert(self, nuevos_datos):
        # Inserta el nuevos_datos dentro del JSON que se haya cargado.
        validado, mensaje_error = self.validar_datos(nuevos_datos)
        if validado:
            #Si el valor se valida correctamente, procede a ser agregado.
            self.json_manager.insert_item(nuevos_datos)
        else: 
            #Si el valor falla, entonces genera la alerta de error.
            raise Exception(mensaje_error)
    
    def actualizar(self, id_elemento, nuevo_valor):
        # Actualiza el valor del item que concuerde con el id_elemento
        validado, mensaje_error = self.validar_datos(nuevo_valor)
        if validado:
            #Si el valor se valida correctamente, procede a ser agregado.
            self.json_manager.update_item(self.nombre_campo, id_elemento, nuevo_valor)
        else: 
            #Si el valor falla, entonces genera la alerta de error.
            raise Exception(mensaje_error)
        
"""
Estos modelos se encargarán de interactuar con el DataRetriever para obtner información de nuestra fuente de datos, y devolverán
la información a nuestros controllers para que esta sea enviada a nuestras views.
"""

class Modelo_Carrito(Modelo_DataRetriever):
    def __init__(self):
        self.nombre_campo = "idCarrito"
        super().__init__(self.nombre_campo, 'carrito.json', VALIDACION_SCHEMA_CARRITO)
    
    def limpiar_carrito(self, id_carrito):
        carrito = self.select(id_carrito)
        carrito['productos'] = []
        self.actualizar(id_carrito, carrito)

    def reducir_item_carrito(self, id_carrito, id_producto, cantidad):
        carrito = self.select(id_carrito)
        productos_carrito = carrito.get('productos')
        for item in productos_carrito:
            if item.get("idProducto") == id_producto:
                item["cantidadProducto"] = item["cantidadProducto"] - cantidad
                self.actualizar(id_carrito, carrito)
                return True
        # Si el producto no pudo ser encontrado, entonces retorna False. 
        return False

    def aumentar_item_carrito(self, id_carrito, id_producto, cantidad):
        carrito = self.select(id_carrito)
        productos_carrito = carrito.get('productos')
        for item in productos_carrito:
            if item.get("idProducto") == id_producto:
                item["cantidadProducto"] = item["cantidadProducto"] + cantidad
                self.actualizar(id_carrito, carrito)
                return True
        # Si el producto no pudo ser encontrado, entonces retorna False. 
        return False

class Modelo_Producto(Modelo_DataRetriever):
    def __init__(self):
        self.nombre_campo = "idProducto"
        super().__init__(self.nombre_campo, 'productos.json', VALIDACION_SCHEMA_PRODUCTO)

    def reducir_item_stock(self, id_producto, cantidad):
        productos = self.select(id_producto)
        productos["cantidadProducto"] = productos["cantidadProducto"] - cantidad
        self.actualizar(id_producto, productos)

    def aumentar_item_stock(self, id_producto, cantidad):
        productos = self.select(id_producto)
        productos["cantidadProducto"] = productos["cantidadProducto"] + cantidad
        self.actualizar(id_producto, productos)

class Modelo_Usuario(Modelo_DataRetriever):    
    def __init__(self):
        self.nombre_campo = "idUsuario"
        super().__init__(self.nombre_campo, 'usuarios.json', VALIDACION_SCHEMA_USUARIO)