from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",      # Cambia por tu usuario de MySQL
        password="",  # Cambia por tu contraseña de MySQL
        database="arte_db"
    )
    return connection

# RUTA PARA EL CRUD (LISTAR Y FORMULARIO DE CREAR/EDITAR)
@app.route('/', methods=['GET', 'POST'])
def index():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Si envían el formulario por POST (Crear o Actualizar)
    if request.method == 'POST':
        id_C = request.form.get('id_C')
        nombre = request.form['nombre']
        hora = request.form['hora']
        profesor = request.form['profesor']

        if id_C:  # Si existe ID, actualizamos (Update)
            cursor.execute(
                "UPDATE cursos_crud SET nombre = %s, hora = %s, profesor = %s WHERE id_C = %s",
                (nombre, hora, profesor, id_C)
            )
        else:  # Si no existe ID, creamos uno nuevo (Create)
            cursor.execute(
                "INSERT INTO cursos_crud (nombre, hora, profesor) VALUES (%s, %s, %s)",
                (nombre, hora, profesor)
            )
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))

    # Listar todos los registros (Read)
    cursor.execute("SELECT * FROM cursos_crud")
    cursos = cursor.fetchall()

    # Verificar si se solicitó editar un registro específico
    edit_id = request.args.get('edit')
    curso_a_editar = None
    if edit_id:
        cursor.execute("SELECT * FROM cursos_crud WHERE id_C = %s", (edit_id,))
        curso_a_editar = cursor.fetchone()

    cursor.close()
    conexion.close()
    return render_template('cursos_admin.html', cursos=cursos, curso_a_editar=curso_a_editar)

# RUTA PARA ELIMINAR (Delete)
@app.route('/eliminar/<int:id_C>')
def eliminar(id_C):
    conexion = get_db_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM cursos_crud WHERE id_C = %s", (id_C,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)