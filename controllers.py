from models import Modelo_Carrito, Modelo_Producto, Modelo_Usuario

class Controller_Producto:

    def __init__(self):
        self.productos = Modelo_Producto()

    def listar_productos(self):
        # Carga los productos dentro del JSON productos.json.
        return self.productos.cargar_contenido()

    def buscar_productos(self, id_producto):
        # Busca dentro del JSON productos.json cualquier elemento que concuerde con el ID.
        return self.productos.select(id_producto)

    def producto_disponible(self, id_producto,cantidad):
        # Determina si la cantidad a reducir es menor que la cantidad disponible.
        if self.buscar_productos(id_producto).get('cantidadProducto') >= cantidad:
            return True
        else:
            return False
    
    def reducir_inventario(self, id_producto, cantidad):
        # Si hay existencias, reduce la cantidad del inventario.
        if self.producto_disponible(id_producto, cantidad):
            self.productos.reducir_item_stock(id_producto, cantidad)
            return True
        else:
            return False

    def aumentar_inventario(self, id_producto, cantidad):
        # Aumenta la cantidad del producto determinado en el inventario.
        self.productos.aumentar_item_stock(id_producto, cantidad)

class Controller_Carritos:

    def __init__(self):
        self.carritos = Modelo_Carrito()
        self.producto_Controller = Controller_Producto()

    def crear_Carrito(self, id_carrito):
        # Creamos un objeto con el formato JSON y la información para el nuevo carrito.
        carrito = {
            "idCarrito":id_carrito,
            "productos": []
            }
        self.carritos.insert(carrito)

    #TODO Agregar métodos: Agregar al carrito, borrar, etc. 

    def calcular_Precio_Total(self, id_carrito):
        # Método para calcular el precio total a pagar por el cliente.
        carrito = self.carritos.select(id_carrito)
        total = 0
        for item in carrito.get('productos'):
            total += item['precioProducto'] * item['cantidadProducto']
        return total
    def calcular_Cantidad_Total(self, id_carrito):
        # Método para calcular la cantidad de productos el cliente va a comprar.
        carrito = self.carritos.select(id_carrito)
        total = 0
        for item in carrito.get('productos'):
            total += item['cantidadProducto']
        return total

class Controller_Usuarios:

    def __init__(self):
        self.usuarios = Modelo_Usuario()
        self.controller_Carritos = Controller_Carritos()

    def listar_usuario(self):
        # Carga todos los usuarios dentro del JSON usuarios.json.
        return self.usuarios.cargar_contenido()

    def usuario_actual(self):
        # Carga los los ID de todos los usuarios.
        return [item.get('idUsuario') for item in self.usuarios.cargar_contenido()]
    
    def crear_usuario(self, nuevo_usuario):
        # Se valida que el usuario no exista o que los datos no estén vacíos.
        if nuevo_usuario.get('idUsuario') in self.usuario_actual() or not nuevo_usuario:
            False 
        # El ID del carrito debe ser igual al ID del usuario.
        if not nuevo_usuario.get('idCarrito'):
            nuevo_usuario['idCarrito'] = nuevo_usuario.get('idUsuario')
        # Se crea el nuevo usuario y el nuevo carrito, con el ID de su dueño.
        self.usuarios.insert(nuevo_usuario)
        self.controller_Carritos.crear_Carrito(nuevo_usuario.get('idUsuario'))
