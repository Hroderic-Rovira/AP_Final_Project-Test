from flask import Flask
from flask import request, render_template, jsonify, make_response

from controllers import Controller_Producto, Controller_Carritos, Controller_Usuarios

app = Flask(__name__, template_folder='views')

controller_Carrito = Controller_Carritos()
controller_Productos = Controller_Producto()
controller_Usuarios = Controller_Usuarios()

# region Variables Globales

HOST_ADRESS = '127.0.0.1'
HTML_TEMPLATE = 'main_page.html'

#endregion

@app.errorhandler(404)
def error_404(e):
    return jsonify(error=str(e)),404

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

# region Productos:

@app.route('/products/all')
def listar_productos_HTML():
    # Retornar una lista de todos los productos disponibles.
    return render_template(HTML_TEMPLATE, rendered_request='/api/products/all',rendered_response=listar_productos().data)

@app.route('/products/detail/<idProducto>')
def filtrar_productos_HTML(idProducto):
    #! Info.
    return render_template(HTML_TEMPLATE, rendered_request=f'/api/products/detail/{idProducto}',rendered_response=filtrar_productos(idProducto).data)

# -|- URL de Productos con prefijo -> /api -|-

@app.route('/api/products/all', methods=['GET'])
def listar_productos():
    # Listar todos los productos. 
    return jsonify({"productos": controller_Productos.listar_productos()})
    
@app.route('/api/products/detail/<idProducto>', methods=['GET'])
def filtrar_productos(idProducto):
    # Filtrar los productos por medio de un ID. 
    try:
        return jsonify({idProducto: controller_Productos.buscar_productos(int(idProducto))})
    except ValueError:
        return make_response(jsonify({"message":f'El parámetro idProducto ({idProducto}) debe ser un número.'}),400)

#endregion

# region Carrito:
@app.route('/cart/<idUsuario>')
def ver_carrito_HTML(idUsuario):
    #
    return render_template(HTML_TEMPLATE, rendered_request = f'/api/products/detail/{idUsuario}', rendered_response = filtrar_productos(idUsuario).data)
@app.route('/cart/price/<idUsuario>')
def ver_precio_total_HTML(idUsuario):
    #
    return render_template(HTML_TEMPLATE, render_request = f'/api/cart/{idUsuario}', rendered_response = ver_precio_total(idUsuario).data)

@app.route('/cart/qty/<idUsuario>')
def ver_cantidad_total_HTML(idUsuario):
    #
    return render_template(HTML_TEMPLATE, render_request = f'/api/cart/{idUsuario}', rendered_response = ver_cantidad_total(idUsuario).data)

# -|- URL de Carrito con prefijo -> /api -|-

@app.route('/api/cart/<idUsuario>', methods=['GET'])
def ver_carrito(idUsuario):
    #
    try:
        return jsonify({idUsuario: controller_Carrito.filtrar_carritos(int(idUsuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)

@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['POST'])
def agregar_producto_carrito(idUsuario, idProducto):
    # Se encarga de agregar un producto determinado al carrito del usuario.
    try:
        mensaje = controller_Carrito.agregar_item_Carrito(int(idUsuario), int(idProducto),1)
        if mensaje:
            return jsonify({"message": f'El producto {mensaje} fue añadido.'})
        else:
            return jsonify({"message": f'El producto {mensaje} no pudo ser añadido.'})

    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)
    except Exception as mensaje_error:
        return make_response(jsonify({"message": str(mensaje_error)}),400)

@app.route('/api/cart/<idUsuario>/<idProducto>', methods=['DELETE'])
def eliminar_producto_carrito(idUsuario, idProducto):
    # Se encarga de eliminar un producto determinado del carrito del usuario.
    try:
        return jsonify({"message": controller_Carrito.borrar_item_Carrito(int(idUsuario),int(idProducto),1)})
    except ValueError:
        return make_response(jsonify({"message": f'Los parametros idUsuario y idProducto debe ser números'}),400)

@app.route('/api/cart/qty/<idUsuario>', methods=['GET'])
def ver_precio_total(idUsuario):
    # Devuelve el precio total de todos los productos en el carrito.
    try:
        return jsonify({f'El {idUsuario} debe': controller_Carrito.calcular_Precio_Total(int(idUsuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)

@app.route('/api/cart/cart/<idUsuarios>', methods=['GET'])
def ver_cantidad_total(idUsuario):
    # Devuelve el total del productos en el carrito del usuario.
    try:
        return jsonify({idUsuario: controller_Carrito.filtrar_carritos(int(idUsuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)

#endregion

# region Usuarios:
@app.route('/users/all')
def listar_usuarios_HTML():
    #
    return render_template(HTML_TEMPLATE, rendered_request='/api/users/all', rendered_response=listar_usuarios().data)

# -|- URL de Usuario con prefijo -> /api -|-

@app.route('/api/users/all', methods=['GET'])
def listar_usuarios():
    #
    return jsonify({"users": controller_Usuarios.listar_usuario()})

@app.route('/api/users/', methods = ['POST'])
def crear_usuario():
    #
    try:
        datos_usuario = request.get_json()
        creado = controller_Usuarios.crear_usuario(datos_usuario)
        if creado:
            return {"usuario_creado":creado}
        return jsonify({"message": f"El usuario no pudo ser creado. El ID ({datos_usuario.get('idUsuario')}) ya está en uso."})
    except Exception as mensaje_error:
        return make_response(jsonify({"message": str(mensaje_error)}),400)
#endregion

app.run(host=HOST_ADRESS)