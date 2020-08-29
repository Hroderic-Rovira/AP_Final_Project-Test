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

@app.route('/products/detail/<idProduct>')
def filtrar_productos_HTML(id_producto):
    #! Info.
    return render_template(HTML_TEMPLATE, rendered_request=f'/api/products/detail/{id_producto}',rendered_response=filtrar_productos(id_producto).data)

# -|- URL de Productos con prefijo -> /api -|-

@app.route('/api/products/all', methods=['GET'])
def listar_productos():
    # Listar todos los productos. 
    return jsonify({"productos": controller_Productos.listar_productos()})
    
@app.route('/api/productos/detail/<idPorduct>', methods=['GET'])
def filtrar_productos(id_producto):
    # Filtrar los productos por medio de un ID. 
    try:
        return jsonify({id_producto: controller_Productos.buscar_productos(int(id_producto))})
    except ValueError:
        return make_response(jsonify({"message":f'El parámetro idProducto ({id_producto}) debe ser un número.'}),400)

#endregion

# region Carrito:
@app.route('/cart/<idUser>')
def ver_carrito_HTML(id_usuario):
    #
    return render_template(HTML_TEMPLATE, rendered_request = f'/api/products/detail/{id_usuario}', rendered_response = filtrar_productos(id_usuario).data)
@app.route('/cart/price/<idUser>')
def ver_precio_total_HTML(id_usuario):
    #
    return render_template(HTML_TEMPLATE, render_request = f'/api/cart/{id_usuario}', rendered_response = ver_precio_total(id_usuario).data)

@app.route('/cart/qty/<idUser>')
def ver_cantidad_total_HTML(id_usuario):
    #
    return render_template(HTML_TEMPLATE, render_request = f'/api/cart/{id_usuario}', rendered_response = ver_cantidad_total(id_usuario).data)

# -|- URL de Carrito con prefijo -> /api -|-

@app.route('/api/cart/<idUser>', methods=['GET'])
def ver_carrito(id_usuario):
    #
    try:
        return jsonify({id_usuario: controller_Carrito.filtrar_carritos(int(id_usuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)

@app.route('/api/cart/<idUser>/<idProduct>', methods=['POST'])
def agregar_producto_carrito(id_usuario, id_producto):
    # Se encarga de agregar un producto determinado al carrito del usuario.
    try:
        mensaje = controller_Carrito.agregar_item_Carrito(int(id_usuario), int(id_producto),1)
        if mensaje:
            return jsonify({"message": f'El producto {mensaje} fue añadido.'})
        else:
            return jsonify({"message": f'El producto {mensaje} no pudo ser añadido.'})

    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)
    except Exception as mensaje_error:
        return make_response(jsonify({"message": str(mensaje_error)}),400)

@app.route('/api/cart/<idUser>/<idProduct>', methods=['DELETE'])
def eliminar_producto_carrito(id_usuario, id_producto):
    # Se encarga de eliminar un producto determinado del carrito del usuario.
    try:
        return jsonify({"message": controller_Carrito.borrar_item_Carrito(int(id_usuario),int(id_producto),1)})
    except ValueError:
        return make_response(jsonify({"message": f'Los parametros idUsuario y idProducto debe ser números'}),400)

@app.route('/api/cart/qty/<idUser>', methods=['GET'])
def ver_precio_total(id_usuario):
    # Devuelve el precio total de todos los productos en el carrito.
    try:
        return jsonify({id_usuario: controller_Carrito.filtrar_carritos(int(id_usuario))})
    except ValueError:
        return make_response(jsonify({"message": f'El parametro idUsuario debe ser un número'}),400)

@app.route('/api/cart/cart/<idUsers>', methods=['GET'])
def ver_cantidad_total(id_usuario):
    # Devuelve el total del productos en el carrito del usuario.
    try:
        return jsonify({id_usuario: controller_Carrito.filtrar_carritos(int(id_usuario))})
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