from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'secreto_super_seguro'

# Conexión a MongoDB
client = MongoClient('mongodb+srv://Neider:Nei%40123.@cluster0.4ipvsze.mongodb.net/')
db = client['medicenter']
usuarios = db['usuarios']
medicamentos = db["medicamentos"]

@app.route('/')
def inicio():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje_error = None

    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        usuario = usuarios.find_one({'nombre': nombre, 'cedula': cedula})

        if usuario:
            session['usuario_id'] = str(usuario['_id'])
            return redirect(url_for('panel'))
        else:
            mensaje_error = "El usuario no está registrado en la base de datos registrate cabrón."

    return render_template('login.html', error=mensaje_error)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']

        if usuarios.find_one({'cedula': cedula}):
            return "Ya existe un usuario con esa cédula.", 400

        nuevo_usuario = {
            'nombre': nombre,
            'cedula': cedula,
            'medicamento': None  # No se asigna medicamento
        }
        usuarios.insert_one(nuevo_usuario)
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/panel')
def panel():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario = usuarios.find_one({'_id': ObjectId(session['usuario_id'])})

    medicamento = usuario.get('medicamento')
    if medicamento:
        nombre_med = medicamento.get('nombre', 'Desconocido')
        dosis_med = medicamento.get('dosis', 'No especificada')
    else:
        nombre_med = 'No asignado'
        dosis_med = 'No asignada'

    return render_template('panel.html',
                           nombre=usuario['nombre'],
                           cedula=usuario['cedula'],
                           medicamento={'nombre': nombre_med, 'dosis': dosis_med})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/asignar', methods=['GET', 'POST'])
def asignar_medicamentos():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        medicamento_id = request.form['medicamento_id']

        medicamento = db['medicamentos'].find_one({'_id': ObjectId(medicamento_id)})

        if medicamento:
            usuarios.update_one(
                {'_id': ObjectId(usuario_id)},
                {'$set': {'medicamento': medicamento}}
            )
        return redirect(url_for('asignar_medicamentos'))

    todos_usuarios = list(usuarios.find())
    todos_medicamentos = list(db['medicamentos'].find())
    return render_template('asignar.html', usuarios=todos_usuarios, medicamentos=todos_medicamentos)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if usuario == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('asignar_medicamentos'))
        else:
            return "Credenciales de administrador incorrectas", 401
    return render_template('admin_login.html')

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))



if __name__ == '__main__':
    app.run(debug=True)
