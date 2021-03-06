from flask import Flask
from flask import request, render_template, jsonify, make_response, abort, redirect, url_for
from controllers import Controller_Producto, Controller_Carritos, Controller_Usuarios

#  - GitHub OAuth 2.0
from flask_github import GitHub

# region Variables Goblales

app = Flask(__name__, template_folder='views')

controller_Carrito = Controller_Carritos()
controller_Productos = Controller_Producto()
controller_Usuarios = Controller_Usuarios() 

#region GITHUB OAUTH 
    # (LOCAL):
# app.config['GITHUB_CLIENT_ID'] = '31437e8463c8e7e1768e'
# app.config['GITHUB_CLIENT_SECRET'] = '51e3e9ba596ae39946963c0639588366bb3b1da0'

# github = GitHub(app)

    # (PÚBLICO):
app.config['GITHUB_CLIENT_ID'] = '31437e8463c8e7e1768e'
app.config['GITHUB_CLIENT_SECRET'] = '51e3e9ba596ae39946963c0639588366bb3b1da0'

github = GitHub(app)
#endregion

# region Constantes

HOST_ADRESS = '127.0.0.1'
HTML_TEMPLATE = 'main_page.html'

# endregion

@app.route("/git_aut/")
# Se invoca el OAuth de GitHub.
def login_github():
    return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
# Nuestro call back the GitHub, donde se determina si el usuario autorizó nuestra aplicación.
def authorized_git(oauth_token):
    next_url = request.args.get('next') or url_for('login_HTML')
    if oauth_token is None:
        return redirect(next_url)
    else:
        next_url = url_for('main_page_HTML')
    return redirect(next_url)

# endregion

@app.errorhandler(404)
# Handler para el error 404.
def error_404(e):
    return render_template('error_404_page.html')

@app.route('/', defaults = {'username': None, 'password': None})
@app.route('/<username>', defaults = {'password': None})
@app.route('/<username>/<password>')
# URL para la página principal.
def login_HTML(username, password):
    if username:
        if password:
            if login(username, password, True) == "Invalid User":
                print(username+"-"+password)
                return render_template('landing_page.html', login = "Invalid User", error = "Los datos no coinciden con ningún usuario.")
            else:
                return redirect('/main_page')
        else:
            return render_template('landing_page.html', login = "Invalid User")
    else: 
        return render_template('landing_page.html', login = "First Time")

@app.route('/main_page', methods=['POST','GET'])
def main_page_HTML():
    # URL para visualizar los usuarios registrados.
    return render_template('landing_page.html', login = "Valid User")

# region Productos:

@app.route('/products/all')
def listar_productos_HTML():
    # URL para listar los productos.
    return render_template('productos.html', rendered_response=listar_productos(True), name = "listar" )

@app.route('/products/detail/<idProducto>')
def filtrar_productos_HTML(idProducto):
    # URL para filtrar los productos.
    return render_template('productos.html', rendered_response=filtrar_productos(idProducto,True), name = "filtrar" )

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
        return make_response(jsonify({"Mensaje de Error": f'El parámetro idProducto ({idProducto}) debe ser un número.'}), 400)

# endregion

# region Carrito:

@app.route('/cart/<idUsuario>')
def ver_carrito_HTML(idUsuario):
    # URL para ver los contenidos de un usuario.
    return render_template('carrito.html', rendered_response=ver_carrito(idUsuario,True), username = filtrar_usuarios(idUsuario,True))

@app.route('/cart/price/<idUsuario>')
def ver_precio_total_HTML(idUsuario):
    # URL para ver el precio total de un carrito.
    return render_template('total_pagar.html', rendered_response=ver_precio_total(idUsuario,True), username = filtrar_usuarios(idUsuario,True))

@app.route('/cart/qty/<idUsuario>')
def ver_cantidad_total_HTML(idUsuario):
    # URL para ver la cantidad total de productos en un carrito.
    return render_template('total_cantidad.html', rendered_response=ver_cantidad_total(idUsuario, True), username = filtrar_usuarios(idUsuario,True))

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
        return make_response(jsonify({"Mensaje de Error": f'El parametro idUsuario debe ser un número.'}), 400)


@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['POST'])
def agregar_producto_carrito(idUsuario, idProducto):
    # Genera el request para agregar un producto al carrito.
    try:
        mensaje = controller_Carrito.agregar_item_Carrito(
            int(idUsuario), int(idProducto), 1)
        if mensaje:
            return jsonify({"Mensaje": f'El producto {mensaje} fue añadido.'})
        else:
            return jsonify({"Mensaje de Error": f'El producto {mensaje} no pudo ser añadido.'})

    except ValueError:
        return make_response(jsonify({"Mensaje de Error": f'El parametro idUsuario debe ser un número'}), 400)
    except Exception as mensaje_error:
        return make_response(jsonify({"Mensaje de Error": str(mensaje_error)}), 400)

@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['DELETE'])
def eliminar_producto_carrito(idUsuario, idProducto):
    # Genera el request para eliminar un producto de un carrito.
    try:
        return jsonify({"Mensaje": controller_Carrito.borrar_item_Carrito(int(idUsuario), int(idProducto), 1)})
    except ValueError:
        return make_response(jsonify({"Mensaje de Error": f'Los parametros idUsuario y idProducto debe ser números.'}), 400)

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
    return render_template('usuarios.html', rendered_request='/api/users/all', rendered_response=listar_usuarios(True), name = "listar")

@app.route('/users/filtrar/<idUsuario>')
def filtrar_usuarios_HTML(idUsuario):
    # URL para filtrar un usuario en específico.
    return render_template('usuarios.html', rendered_request='/api/users/filtrar/<idUsuario>', rendered_response=filtrar_usuarios(idUsuario, True), name = "filtrar")

# -|- URL de Usuario con prefijo -> /api -|-

@app.route('/api/users/all', methods=['GET'])
def listar_usuarios(flag = None):
    # Genera el request para visualizar los usuarios registrados.
    if flag:
        return controller_Usuarios.listar_usuario()
    else:
        return jsonify({"users": controller_Usuarios.listar_usuario()})

@app.route('/api/users/filtrar/<idUsuario>', methods=['GET'])
def filtrar_usuarios(idUsuario,flag = None):
    # Genera el request para visualizar un usuario con un ID específico.
    if flag:
        return controller_Usuarios.filtrar_usuario(int(idUsuario))
    else:
        return jsonify({'user_info': controller_Usuarios.filtrar_usuario(int(idUsuario))})

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

@app.route("/api/users/login/<username>/<password>", methods=["POST"])
def login(username, password, flag = None):
    if flag:  
        if username and password:
            result = controller_Usuarios.login(username, password)
            if result != "password_incorrecto" and result != "usuario_no_existe":
                return "Valid User"
        return "Invalid User"
    else:
        if not username and not password:
            abort(400)
        result = controller_Usuarios.login(username, password)
        if result != "password_incorrecto" and result != "usuario_no_existe":
            return make_response(jsonify({"message": 'Ha ingresado exitósamente.'}), 201)
        return make_response(jsonify({"message": "Ha ingresado un usuario inválido."}), 500)



# endregion

app.run(host=HOST_ADRESS, port= 80, debug=True)
