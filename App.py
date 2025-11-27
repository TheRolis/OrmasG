from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import io
import filetype

app = Flask(__name__)
DB_NAME = "inventario.db"

# Inicializar tabla si no existe
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            imagen BLOB
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ------------------------------------------------
# Ruta principal
# ------------------------------------------------
@app.route('/')
def home():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('Proyecto_web_y_mobil.html', productos=productos)

# ------------------------------------------------
# Página de gestión completa
# ------------------------------------------------
@app.route('/productos')
def productos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos)

# ------------------------------------------------
# Mostrar formulario para agregar producto
# ------------------------------------------------
@app.route('/crear', methods=['GET'])
def crear_producto():
    return render_template('Crear.html')

# ------------------------------------------------
# Agregar producto (procesa POST)
# ------------------------------------------------
@app.route('/agregar', methods=['POST'])
def agregar_producto():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    cantidad = request.form.get('cantidad')

    imagen_bytes = None
    file = request.files.get('imagen')
    if file and file.filename != '':
        imagen_bytes = file.read()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, precio, cantidad, imagen) VALUES (?, ?, ?, ?)",
        (nombre, precio, cantidad, imagen_bytes)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# ------------------------------------------------
# Lista completa → editar.html
# ------------------------------------------------
@app.route('/editar')
def editar():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('editar.html', productos=productos)

# ------------------------------------------------
# Edición individual → Edicion.html
# ------------------------------------------------
@app.route('/edicion/<int:id>', methods=['GET', 'POST'])
def edicion(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        eliminar_imagen = request.form.get('eliminar_imagen')

        if eliminar_imagen == "1":
            cursor.execute(
                "UPDATE productos SET nombre=?, precio=?, cantidad=?, imagen=NULL WHERE id=?",
                (nombre, precio, cantidad, id)
            )
        else:
            file = request.files.get('imagen')
            if file and file.filename != '':
                nueva_imagen = file.read()
                cursor.execute(
                    "UPDATE productos SET nombre=?, precio=?, cantidad=?, imagen=? WHERE id=?",
                    (nombre, precio, cantidad, nueva_imagen, id)
                )
            else:
                cursor.execute(
                    "UPDATE productos SET nombre=?, precio=?, cantidad=? WHERE id=?",
                    (nombre, precio, cantidad, id)
                )

        conn.commit()
        conn.close()
        return redirect(url_for('editar'))  # volver a la lista completa

    cursor.execute("SELECT * FROM productos WHERE id=?", (id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template('Edicion.html', producto=producto)

# ------------------------------------------------
# Eliminar producto
# ------------------------------------------------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('editar'))

# ------------------------------------------------
# Mostrar imagen
# ------------------------------------------------
@app.route('/imagen/<int:id>')
def mostrar_imagen(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT imagen FROM productos WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        img_bytes = row[0]
        kind = filetype.guess(img_bytes)
        mimetype = kind.mime if kind else "application/octet-stream"
        return send_file(io.BytesIO(img_bytes), mimetype=mimetype)

    return "No hay imagen", 404

# ------------------------------------------------
# Run
# ------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
