import json
import os

class Administrador_JSON():

    def __init__(self, archivo_json):

        #Obtenemos la ruta abosulta del archivo JSON.
        path = os.path.abspath(__file__)
        nombre_directorio = os.path.dirname(path)
        os.chdir(nombre_directorio)
        self.archivo_json = f'{archivo_json}'
        self.datos_json = self.read_json()

    #Métodos para la manipulación de los JSON:

    def read_json(self):
        # Abre el archivo que se encuentre en la dirección enviada por le programa.
        with open(self.archivo_json) as archivo_json:
            return json.load(archivo_json)

    def select_item(self, nombre_campo, valor):
        # Devuelve cualquier elemento que concuerde con el nombre del campo. Si no encuentra ninguno, devuelve None.
        self.datos_json = self.read_json()
        item_encontrado = next((item for item in self.datos_json if item[nombre_campo] == valor),None)
        return item_encontrado

    def insert_item(self, nuevos_datos):
        # Insertar un nuevo elemento y invoca el método para guardar el JSON File.
        self.datos_json.append(nuevos_datos)
        self.save_item(self.datos_json)

    def delete_item(self, nombre_campo, valor):
        # Ubica un elemento que concuerde con el nombre del campo, y luego elimina el objeto item. Por último, guarda el JSON File.
        for item in self.datos_json:
            if item.get(nombre_campo) == valor:
                del item
                self.save_item(self.datos_json)
                return True
        return False

    def update_item(self, nombre_campo, valor, nuevos_datos):
        # Ubica un elemento que concuerde con el nombre del campo, luego lo actualiza con los nuevos_datos. Por último, guarda el JSON File.
        for item in self.datos_json:
            if item.get(nombre_campo) == valor:
                item = nuevos_datos
                self.save_item(self.datos_json)
                return True
        return False

    def save_item(self, datos_a_guardar):
        # Guarad los contenidos de datos_a_guardar y recarga datos_json con la nueva información.
        with open(self.archivo_json, "w") as archivo_json:
            json.dump(datos_a_guardar, archivo_json)
        self.datos_json = self.read_json()

