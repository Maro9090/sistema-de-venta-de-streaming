from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'TU CLAVE SECRETA'
#app.permanent_session_lifetime = 10  # Establecer la vida útil de la sesión en cero

def connect_db():
    return sqlite3.connect('database.db')

@app.after_request
def add_header(response):
    # Evitar que el navegador cachee la página.
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):  # Verificar la contraseña con el hash almacenado
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email=?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('El usuario ya existe. Por favor, elige otro correo electrónico.', 'error')
            return redirect(url_for('signup'))

        password_hash = generate_password_hash(password)  # Hashear la contraseña antes de almacenarla

        cursor.execute('INSERT INTO users (nombre, apellido, email, password) VALUES (?, ?, ?, ?)', (nombre, apellido, email, password_hash))
        conn.commit()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'email' in session:
        email = session['email']
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT nombre, apellido FROM users WHERE email=?', (email,))
        user_data = cursor.fetchone()
        
        if user_data:
            nombre, apellido = user_data
            return render_template('home.html', nombre=nombre, apellido=apellido)
        else:
            flash('Usuario no encontrado en la base de datos', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# BARRA DE NAVEGACION

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def inicio():
    return redirect(url_for('home'))

@app.route('/editar_cliente.html')
def editarcliente():
    return redirect(url_for('/clientes/editar_cliente.html'))

@app.route('/cliente.html')
def cliente():
    return render_template('/clientes/cliente.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

# Area de clientes

@app.route('/clientes')
def mostrar_clientes():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Clientes')
    clientes = cursor.fetchall()

    conn.close()

    return render_template('/clientes/buscarcliente.html', clientes=clientes)

# Ruta para mostrar el formulario de agregar cliente
@app.route('/agregar_cliente_form')
def agregar_cliente_form():
    return render_template('/clientes/agregar_cliente.html')


# Ruta para manejar el formulario y agregar el cliente a la base de datos
@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO Clientes (Nombre, Telefono, Direccion) VALUES (?, ?, ?)', (nombre, telefono, direccion))
        conn.commit()
        conn.close()

        return redirect(url_for('mostrar_clientes'))

@app.route('/editar_cliente_form', methods=['GET'])
def editar_cliente_form():
    cliente_id = request.args.get('cliente_id')
    
    # Verificar si se proporcionó un ID de cliente
    if cliente_id:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Buscar el cliente por ID o nombre
        cursor.execute('SELECT * FROM Clientes WHERE ID_Cliente = ? OR Nombre LIKE ?', (cliente_id, f'%{cliente_id}%'))
        cliente = cursor.fetchone()
        conn.close()
        
        # Verificar si se encontró un cliente
        if cliente:
            return render_template('/clientes/editar_cliente.html', cliente_id=cliente[0], nombre=cliente[1], telefono=cliente[2], direccion=cliente[3])
        else:
            return "Cliente no encontrado"
    else:
        return "ID de cliente no proporcionado"

# Ruta para procesar la actualización de los datos del cliente
@app.route('/editar_cliente', methods=['POST'])
def editar_cliente():
    cliente_id = request.form['cliente_id']
    telefono = request.form['telefono']
    direccion = request.form['direccion']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Clientes SET  Telefono=?, Direccion=? WHERE ID_Cliente=?', ( telefono, direccion, cliente_id))
    conn.commit()
    conn.close()

    return redirect(url_for('cliente'))

@app.route('/buscarclienteeditar')
def buscarclienteeditar():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Clientes')
    clientes = cursor.fetchall()

    conn.close()

    return render_template('/clientes/buscarclienteeditar.html', clientes=clientes)

# ELIMINAR CLIENTE
@app.route('/eliminar_cliente_form', methods=['GET', 'POST'])
def eliminar_cliente_form():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM Clientes WHERE ID_Cliente = ?', (cliente_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('mostrar_clientes'))  # Redirige a la página de clientes después de eliminar el cliente
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Clientes')
    clientes = cursor.fetchall()

    conn.close()

    return render_template('/clientes/eliminar_cliente_form.html', clientes=clientes)

############################################
# Route for rendering the sales registration form
@app.route('/venta')
def ventas_form():
    # Conectar a la base de datos
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Obtener clientes y productos de la base de datos
        cursor.execute("SELECT ID_Cliente, Nombre FROM Clientes")
        clientes = cursor.fetchall()

        cursor.execute("SELECT ID_Producto, Nombre FROM Productos")
        productos = cursor.fetchall()

        return render_template('/ventas/ventas_form.html', clientes=clientes, productos=productos)
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()

# Ruta para manejar la solicitud de obtener las opciones del correo y la contraseña
@app.route('/fetch_credentials')
def fetch_credentials():
    producto_id = request.args.get('producto_id')

    # Conectar a la base de datos y ejecutar la consulta para obtener las opciones del correo y la contraseña
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT ID_Credencial, Correo, Contraseña FROM Credenciales WHERE Producto_ID = ?', (producto_id,))
    credentials = cursor.fetchall()

    conn.close()

    # Devolver las opciones del correo y la contraseña en formato JSON
    return jsonify({
        'credentials': credentials
    })

@app.route('/registro_venta', methods=['POST'])
def registro_venta():
    if request.method == 'POST':
        cliente = request.form['cliente']
        producto = request.form['producto']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        perfil = request.form['perfil']  # Ahora se lee como texto
        pin_perfil = request.form['pin_perfil']  # Ahora se lee como texto
        fecha_venta = request.form['fecha_venta']
        fecha_vencimiento = request.form['fecha_vencimiento']

        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Insertar la venta en la tabla Ventas
            cursor.execute('''INSERT INTO Ventas (ID_Cliente, ID_Producto, ID_Perfil, Fecha_Venta, Fecha_Vencimiento)
                              VALUES (?, ?, ?, ?, ?)''',
                              (cliente, producto, perfil, fecha_venta, fecha_vencimiento))
            
             # Insertar el perfil y pin en la tabla Perfiles
            cursor.execute('''INSERT INTO Perfiles (ID_Producto, Perfil, Pin, Vendido)
                              VALUES (?, ?, ?, ?)''',
                              (producto, perfil, pin_perfil, 1))  # 1 indica que está vendido


            # Confirmar los cambios en la base de datos
            conn.commit()

            return redirect(url_for('ventas_form'))
        except sqlite3.Error as e:
            print("Error:", e)
            conn.rollback()
        finally:
            conn.close()

################################################
@app.route('/mostrar_credenciales')
def mostrar_credenciales():
    conn = connect_db()
    cursor = conn.cursor()

    # Obtener todas las credenciales de la base de datos
    cursor.execute("SELECT * FROM Credenciales")
    credenciales = cursor.fetchall()

    conn.close()

    return render_template('credenciales.html', credenciales=credenciales)

@app.route('/agregar_credencial', methods=['POST'])
def agregar_credencial():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        producto_id = request.form['producto_id']

        conn = connect_db()
        cursor = conn.cursor()

        # Insertar la nueva credencial en la base de datos
        cursor.execute("INSERT INTO Credenciales (Correo, Contraseña, Producto_ID) VALUES (?, ?, ?)",
                       (correo, contrasena, producto_id))
        conn.commit()
        conn.close()

    return redirect(url_for('mostrar_credenciales'))

@app.route('/editar_credencial', methods=['POST'])
def editar_credencial():
    if request.method == 'POST':
        credencial_id = request.form['credencial_id']
        nuevo_correo = request.form['nuevo_correo']
        nueva_contrasena = request.form['nueva_contrasena']
        nuevo_producto_id = request.form['nuevo_producto_id']

        conn = connect_db()
        cursor = conn.cursor()

        # Actualizar la credencial en la base de datos
        cursor.execute("UPDATE Credenciales SET Correo=?, Contraseña=?, Producto_ID=? WHERE ID_Credencial=?",
                       (nuevo_correo, nueva_contrasena, nuevo_producto_id, credencial_id))
        conn.commit()
        conn.close()

    return redirect(url_for('mostrar_credenciales'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
