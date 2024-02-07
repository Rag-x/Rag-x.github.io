from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from flask import render_template

# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
@app.route('/lista-sensor', methods=['GET'])
def lista_sensorBD():
    if 'conectado' in session:
        sensores = lista_sensor()  # Asegúrate de implementar esta función
        areas = lista_areasBD()
        data_login = dataLoginSesion()
        return render_template('public/usuarios/lista_sensor.html', sensores=sensores, areas=areas, dataLogin=data_login)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
@app.route('/lista-vista', methods=['GET'])
def lista_vista():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_vista.html', lista_vista1=lista_vista(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    
@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())
    
@app.route("/reporte-ingreso", methods=['GET'])
def reporteingresos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/usuarios/ingresos.html',  lista_ingreso=dataingreso(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    print(id)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    guardarClaveAuditoria(clave_generada,id)
    return clave_generada
#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']
        ubicacion = request.form['ubicacion']
        dispositivos = request.form['dispositivos']
        marca_dispositivos = request.form['marca_dispositivos']

        resultado_insert = guardarArea(area_name, ubicacion, dispositivos, marca_dispositivos)

        if resultado_insert:
            flash('El Área fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            flash('Hubo un error al guardar el Área', 'error')

    # Si llegamos aquí, es una solicitud GET o un error en la solicitud POST
    return render_template('public/usuarios/lista_areas.html')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        # Obtener los valores actualizados desde el formulario
        nombre_area = request.form['nombre_area']
        ubicacion = request.form['ubicacion']
        dispositivos = request.form['dispositivos']
        marca_dispositivos = request.form['marca_dispositivos']
        id_area = request.form['id_area']

        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    # Actualizar todos los campos en la tabla 'area'
                    sql = """UPDATE area 
                             SET nombre_area = %s, ubicacion = %s, dispositivos = %s, marca_dispositivos = %s
                             WHERE id_area = %s"""

                    valores = (nombre_area, ubicacion, dispositivos, marca_dispositivos, id_area)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()

                    # Verificar si la actualización fue exitosa
                    resultado_update = mycursor.rowcount

                    if resultado_update:
                        flash('El área fue actualizada correctamente', 'success')
                    else:
                        flash('Hubo un error al actualizar el área', 'error')

        except Exception as e:
            flash(f'Se produjo un error al actualizar el área: {str(e)}', 'error')

    return redirect(url_for('lista_areas'))
    