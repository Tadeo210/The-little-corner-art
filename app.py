import io
import base64
import qrcode
import database as db
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

# --- Ruta para la página donde se ingresa el ID y se genera el QR ---
@app.route("/generar_qr")
def vista_generar_qr():
    return render_template("generar_qr.html")

# --- Endpoint API que genera la imagen en base64 del código QR ---
@app.route("/api/generar_qr", methods=['POST'])
def api_generar_qr():
    id_alumno = request.json.get('id_alumno')

    if not id_alumno:
        return jsonify({'status': 'error', 'message': 'Por favor, ingresa un ID válido.'}), 400

    try:
        cursor = db.db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM alumnos WHERE id = %s", (id_alumno,))
        alumno = cursor.fetchone()
        cursor.close()

        if not alumno:
            return jsonify({'status': 'error', 'message': f'El alumno con ID #{id_alumno} no existe en la base de datos.'}), 404

        # Generar la URL absoluta a la que apuntará el QR
        url_carnet = request.host_url.rstrip('/') + url_for('ver_carnet', id_alumno=id_alumno)

        # Crear la imagen del código QR
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url_carnet)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#496b7b", back_color="white")

        # Convertir la imagen a base64 para enviarla al HTML
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            'status': 'success',
            'qr_image': f"data:image/png;base64,{img_str}",
            'url_carnet': url_carnet
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}), 500

# --- Ruta única que lee dinámicamente cualquier ID desde la URL y muestra sus datos ---
@app.route("/carnet/<int:id_alumno>")
def ver_carnet(id_alumno):
    try:
        cursor = db.db.cursor(dictionary=True)
        sql = """
            SELECT a.id, a.nombre, a.apellido, a.fecha_nacimiento, a.grupo,
                   IFNULL(c.nombre, 'Sin Curso') AS curso,
                   IFNULL(c.horario, 'N/A') AS horario,
                   IFNULL(c.dia, 'N/A') AS dia,
                   IFNULL(p.nombre, 'Sin Asignar') AS profesor
            FROM alumnos a
            LEFT JOIN cursos c ON a.id_curso = c.id
            LEFT JOIN profesores p ON c.id_profesor = p.id
            WHERE a.id = %s
        """
        cursor.execute(sql, (id_alumno,))
        alumno_data = cursor.fetchone()
        cursor.close()

        return render_template("carnet.html", alumno=alumno_data, id_buscado=id_alumno)

    except Exception as e:
        return render_template("carnet.html", alumno=None, id_buscado=id_alumno, error=str(e))

# =========================================================================
# 1. RUTAS DE NAVEGACIÓN Y PLANTILLAS
# =========================================================================

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/info")
def info():
    return render_template("informacion.html")

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

@app.route("/artistas")
def artistas():
    return render_template("artistas.html")

# --- Páginas de Artistas Individuales ---

@app.route("/frida")
def frida():
    return render_template("frida.html")

@app.route("/pablo")
def pablo():
    return render_template("picasso.html")

@app.route("/davinci")
def davinci():
    return render_template("davinci.html")

@app.route("/miguel")
def miguel():
    return render_template("miguelangel.html")

@app.route("/vangogh")
def vangogh():
    return render_template("vangogh.html")

@app.route("/claude")
def claude():
    return render_template("monet.html")

# --- Clases y Registro ---

@app.route("/clasevivo")
def clasevivo():
    return render_template("clasesenvivo.html")

@app.route("/horarios")
def horarios():
    return render_template("horarios.html")

@app.route("/clasegra")
def clasegra():
    return render_template("clasesgrabadas.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

# --- Cursos Individuales ---

@app.route("/cursopin")
def cursopin():
    return render_template("cursopintura.html")

@app.route("/cursodib")
def cursodib():
    return render_template("cursodibujo.html")

@app.route("/cursoesc")
def cursoesc():
    return render_template("cursoescultura.html")

# --- Panel de Administración ---

@app.route("/admin")
def admin():
    return render_template("admin.html")


# =========================================================================
# 2. ENDPOINTS Y API PARA LA BASE DE DATOS MYSQL
# =========================================================================

# --- Registrar Alumno (Desde el formulario general) ---
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    grupo = request.form.get('grupo')
    id_curso = request.form.get('id_curso') # <--- Capturar el curso

    if nombre and apellido and fecha_nacimiento and grupo and id_curso:
        try:
            cursor = db.db.cursor()
            sql = "INSERT INTO alumnos (nombre, apellido, fecha_nacimiento, grupo, id_curso) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, apellido, fecha_nacimiento, grupo, id_curso))
            db.db.commit()
            nuevo_id = cursor.lastrowid
            cursor.close()

            return jsonify({'status': 'success', 'id_alumno': nuevo_id, 'message': '¡Registro Exitoso!'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'Campos incompletos'}), 400


# --- Consulta de Inscripción a Clase en Vivo por ID ---
@app.route('/obtener_inscripcion', methods=['POST'])
def obtener_inscripcion():
    id_alumno = request.form.get('id_alumno')
    curso_clave = request.form.get('curso')

    if not id_alumno or not curso_clave:
        return jsonify({'status': 'error', 'message': 'Por favor, ingresa tu ID y selecciona un curso.'}), 400

    try:
        cursor = db.db.cursor(dictionary=True)

        cursor.execute("SELECT nombre, apellido FROM alumnos WHERE id = %s", (id_alumno,))
        alumno = cursor.fetchone()

        if not alumno:
            cursor.close()
            return jsonify({'status': 'error', 'message': f'El ID {id_alumno} no se encuentra registrado.'}), 404

        sql = """
            SELECT c.nombre AS curso, c.dia, c.horario, p.nombre AS profesor 
            FROM cursos c 
            JOIN profesores p ON c.id_profesor = p.id 
            WHERE LOWER(c.nombre) = LOWER(%s)
        """
        cursor.execute(sql, (curso_clave,))
        clases = cursor.fetchall()

        cursor.close()

        if not clases:
            return jsonify({'status': 'error', 'message': 'No se encontraron horarios para el curso seleccionado.'}), 404

        nombre_completo = f"{alumno['nombre']} {alumno['apellido']}"

        return jsonify({
            'status': 'success',
            'nombre_alumno': nombre_completo,
            'clases': clases
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}), 500


# =========================================================================
# 3. ENDPOINTS API PARA EL PANEL ADMIN (CRUD)
# =========================================================================

# Obtenemos Alumnos, Cursos y Profesores desde MySQL
@app.route("/api/admin/datos", methods=['GET'])
def obtener_datos_admin():
    try:
        cursor = db.db.cursor(dictionary=True)

        sql_alumnos = """
            SELECT a.id, a.nombre, a.apellido, a.fecha_nacimiento, a.grupo, a.id_curso,
                   IFNULL(c.nombre, 'Sin Curso') AS nombre_curso
            FROM alumnos a
            LEFT JOIN cursos c ON a.id_curso = c.id
        """
        cursor.execute(sql_alumnos)
        alumnos = cursor.fetchall()

        sql_cursos = """
            SELECT c.id, c.nombre, c.horario, c.dia, 
                   IFNULL(p.nombre, 'Sin Asignar') AS profesor
            FROM cursos c
            LEFT JOIN profesores p ON c.id_profesor = p.id
        """
        cursor.execute(sql_cursos)
        lista_cursos = cursor.fetchall()

        cursor.execute("SELECT id, nombre, especialidad FROM profesores")
        lista_profesores = cursor.fetchall()

        cursor.close()

        return jsonify({
            'status': 'success',
            'alumnos': alumnos,
            'cursos': lista_cursos,
            'profesores': lista_profesores
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Agregar Alumno desde el Panel Admin
@app.route("/api/alumnos", methods=['POST'])
def agregar_alumno():
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "INSERT INTO alumnos (nombre, apellido, fecha_nacimiento, grupo, id_curso) VALUES (%s, %s, %s, %s, %s)"
        values = (data['nombre'], data['apellido'], data['fecha_nacimiento'], data['grupo'], data['id_curso'])
        cursor.execute(sql, values)
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Alumno registrado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Actualizar Alumno desde el Panel Admin
@app.route("/api/alumnos/<int:id_alumno>", methods=['PUT'])
def actualizar_alumno(id_alumno):
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "UPDATE alumnos SET nombre=%s, apellido=%s, fecha_nacimiento=%s, grupo=%s, id_curso=%s WHERE id=%s"
        values = (data['nombre'], data['apellido'], data['fecha_nacimiento'], data['grupo'], data['id_curso'], id_alumno)
        cursor.execute(sql, values)
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Alumno actualizado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Eliminar Alumno desde el Panel Admin
@app.route("/api/alumnos/<int:id_alumno>", methods=['DELETE'])
def eliminar_alumno(id_alumno):
    try:
        cursor = db.db.cursor()
        cursor.execute("DELETE FROM alumnos WHERE id = %s", (id_alumno,))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Alumno eliminado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# =========================================================================
# OPERACIONES CRUD PARA PROFESORES Y CURSOS
# =========================================================================

# --- PROFESORES ---

@app.route("/api/profesores", methods=['POST'])
def agregar_profesor():
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "INSERT INTO profesores (nombre, especialidad) VALUES (%s, %s)"
        cursor.execute(sql, (data['nombre'], data['especialidad']))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Profesor registrado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/profesores/<int:id_profesor>", methods=['PUT'])
def actualizar_profesor(id_profesor):
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "UPDATE profesores SET nombre=%s, especialidad=%s WHERE id=%s"
        cursor.execute(sql, (data['nombre'], data['especialidad'], id_profesor))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Profesor actualizado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/profesores/<int:id_profesor>", methods=['DELETE'])
def eliminar_profesor(id_profesor):
    try:
        cursor = db.db.cursor()
        cursor.execute("DELETE FROM profesores WHERE id = %s", (id_profesor,))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Profesor eliminado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# --- CURSOS ---

@app.route("/api/cursos", methods=['POST'])
def agregar_curso():
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "INSERT INTO cursos (nombre, horario, dia, id_profesor) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (data['nombre'], data['horario'], data['dia'], data['id_profesor']))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Curso registrado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/cursos/<int:id_curso>", methods=['PUT'])
def actualizar_curso(id_curso):
    data = request.json
    try:
        cursor = db.db.cursor()
        sql = "UPDATE cursos SET nombre=%s, horario=%s, dia=%s, id_profesor=%s WHERE id=%s"
        cursor.execute(sql, (data['nombre'], data['horario'], data['dia'], data['id_profesor'], id_curso))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Curso actualizado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/cursos/<int:id_curso>", methods=['DELETE'])
def eliminar_curso(id_curso):
    try:
        cursor = db.db.cursor()
        cursor.execute("DELETE FROM cursos WHERE id = %s", (id_curso,))
        db.db.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'Curso eliminado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)