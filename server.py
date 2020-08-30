from flask import Flask
from flask import request, render_template, jsonify, make_response, abort

from controllers import Controller_Producto, Controller_Carritos, Controller_Usuarios

app = Flask(__name__, template_folder='views')
usuario_logeado = None
controller_Carrito = Controller_Carritos()
controller_Productos = Controller_Producto()
controller_Usuarios = Controller_Usuarios()

# region Variables Globales

HOST_ADRESS = '127.0.0.1'
HTML_TEMPLATE = 'main_page.html'

# endregion


@app.errorhandler(404)
# Handler para el error 404.
def error_404(e):
    return jsonify(error=str(e)), 404


@app.route('/')
# URL para la página principal.
def landing_page():
    return render_template('landing_page.html')

# region Productos:


@app.route('/products/all')
def listar_productos_HTML():
    # URL para listar los productos.
    return render_template('productos.html', rendered_request='/api/products/all', rendered_response=listar_productos(True))


@app.route('/products/detail/<idProducto>') #! El loop debe ser corregido.
def filtrar_productos_HTML(idProducto):
    # URL para filtrar los productos.
    return render_template('productos.html', rendered_request=f'/api/products/detail/{idProducto}', rendered_response=filtrar_productos(idProducto,True))

# -|- URL de Productos con prefijo -> /api -|-


@app.route('/api/products/all', methods=['GET'])
def listar_productos(flag = None):
    # Genera el request para listar los productos.
    if flag:
        return controller_Productos.listar_productos()
    else:
        return jsonify({"productos": controller_Productos.listar_productos()})


@app.route('/api/products/detail/<idProducto>', methods=['GET'])
def filtrar_productos(idProducto, flag = None):
    # Genera el request para filtrar un producto.
    try:
        if flag:
            return controller_Productos.buscar_productos(int(idProducto))
        else:
            return jsonify({idProducto: controller_Productos.buscar_productos(int(idProducto))})
    except ValueError:
        return make_response(jsonify({"message": f'El parámetro idProducto ({idProducto}) debe ser un número.'}), 400)

# endregion

# region Carrito:


@app.route('/cart/<idUsuario>')
def ver_carrito_HTML(idUsuario):
    # URL para ver los contenidos de un usuario.
    return render_template('carrito.html', rendered_request=f'/api/products/detail/{idUsuario}', rendered_response=ver_carrito(idUsuario,True))


@app.route('/cart/price/<idUsuario>')
def ver_precio_total_HTML(idUsuario):
    # URL para ver el precio total de un carrito.
    return render_template('total_pagar.html', render_request=f'/api/cart/{idUsuario}', rendered_response=ver_precio_total(idUsuario,True))


@app.route('/cart/qty/<idUsuario>')
def ver_cantidad_total_HTML(idUsuario):
    # URL para ver la cantidad total de productos en un carrito.
    return render_template('total_cantidad.html', render_request=f'/api/cart/{idUsuario}', rendered_response=ver_cantidad_total(idUsuario, True))

# -|- URL de Carrito con prefijo -> /api -|-


@app.route('/api/cart/<idUsuario>', methods=['GET'])
def ver_carrito(idUsuario, flag = None):
    # Genera el request para visualizar el carrito de un usuario.
    try:
        if flag:
            return controller_Carrito.filtrar_carritos(int(idUsuario))
        else:
            return jsonify({idUsuario: controller_Carrito.filtrar_carritos(int(idUsuario))})

    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}), 400)


@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['POST'])
def agregar_producto_carrito(idUsuario, idProducto):
    # Genera el request para agregar un producto al carrito.
    try:
        mensaje = controller_Carrito.agregar_item_Carrito(
            int(idUsuario), int(idProducto), 1)
        if mensaje:
            return jsonify({"message": f'El producto {mensaje} fue añadido.'})
        else:
            return jsonify({"message": f'El producto {mensaje} no pudo ser añadido.'})

    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}), 400)
    except Exception as mensaje_error:
        return make_response(jsonify({"message": str(mensaje_error)}), 400)


@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['DELETE'])
def eliminar_producto_carrito(idUsuario, idProducto):
    # Genera el request para eliminar un producto de un carrito.
    try:
        return jsonify({"message": controller_Carrito.borrar_item_Carrito(int(idUsuario), int(idProducto), 1)})
    except ValueError:
        return make_response(jsonify({"message": f'Los parametros idUsuario y idProducto debe ser números'}), 400)


@app.route('/api/cart/price/<idUsuario>', methods=['GET'])
def ver_precio_total(idUsuario, flag = None):
    # Genera el request para visualizar el precio total a pagar.
    try:
        if flag:
            return controller_Carrito.calcular_Precio_Total(int(idUsuario))
        else:
            return jsonify({f'El {idUsuario} debe': controller_Carrito.calcular_Precio_Total(int(idUsuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}), 400)


@app.route('/api/cart/qty/<idUsuario>', methods=['GET'])
def ver_cantidad_total(idUsuario, flag = None):
    # Genera el request para visualizar la cantidad total de productos en un carrito.
    try:
        if flag:
            return controller_Carrito.calcular_Cantidad_Total(int(idUsuario))
        else:
            return jsonify({idUsuario: controller_Carrito.calcular_Cantidad_Total(int(idUsuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}), 400)


@app.route('/api/cart/<idUsuario>', methods=['DELETE'])
def comprar_productos(idUsuario):
    # Genera el request para finalizar la compra (borra los producto de un carrito).
    try:
        mensaje = controller_Carrito.borrar_item_Carrito(int(idUsuario))
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}), 400)
    return jsonify({"mensaje": mensaje})

# endregion

# region Usuarios:


@app.route('/users/all')
def listar_usuarios_HTML():
    # URL para visualizar los usuarios registrados.
    return render_template('usuarios.html', rendered_request='/api/users/all', rendered_response=listar_usuarios(True))

@app.route('/users/login')
def login_HTML():
    # URL para visualizar los usuarios registrados.
    return render_template(HTML_TEMPLATE, rendered_request='/api/users/login', rendered_response=login())

# -|- URL de Usuario con prefijo -> /api -|-


@app.route('/api/users/all', methods=['GET'])
def listar_usuarios(flag = None):
    # Genera el request para visualizar los usuarios registrados.
    if flag:
        return controller_Usuarios.listar_usuario()
    else:
        return jsonify({"users": controller_Usuarios.listar_usuario()})

@app.route('/api/users/', methods=['POST'])
def crear_usuario():
    # Genera el request para crear un usuario. (Tentativo)
    try:
        datos_usuario = request.get_json()
        creado = controller_Usuarios.crear_usuario(datos_usuario)
        if creado:
            return {"usuario_creado": creado}
        return jsonify({"message": f"El usuario no pudo ser creado. El ID ({datos_usuario.get('idUsuario')}) ya está en uso."})
    except Exception as mensaje_error:
        return make_response(jsonify({"message": str(mensaje_error)}), 400)

@app.route("/api/users/login", methods=["POST"])
def login():
    if (
        not request.json
        or not "username" in request.json
        or not "password" in request.json
    ):
        abort(400)
    result = controller_Usuarios.login(
        request.json.get("username"), request.json.get("password")
    )
    if result != "password_incorrecto" and result != "usuario_no_existe":
        return jsonify({"message": 'Ha ingresado exitósamente.'}), 201
    return jsonify({"message": "Usuario Inválido."}), 500

# endregion

app.run(host=HOST_ADRESS, debug = True) #! Debemos cambiar esto luego.
