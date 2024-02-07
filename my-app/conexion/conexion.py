import serial
import mysql.connector
import json
from datetime import datetime
import time
import pandas as pd
import os

ser = serial.Serial('COM6', 9600)
db = None

# Especifica la ruta completa para el archivo Excel en la nueva carpeta
excel_file_path = r'C:\Users\User\Desktop\Nueva carpeta (2)'
excel_file_name = os.path.join(excel_file_path, 'informe_rfid.xlsx')

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def ensure_excel_file_exists():
    if not os.path.isfile(excel_file_name):
        # Si el archivo Excel no existe, crea un DataFrame vacío y guárdalo en el archivo Excel
        df_empty = pd.DataFrame(columns=['rfid_code', 'tarjeta_valida', 'detection_time'])
        df_empty.to_excel(excel_file_name, index=False)

def conexionBD():
    print("ENTRO A LA CONEXION")
    try:
        conexion = mysql.connector.connect(
            host="roundhouse.proxy.rlwy.net",
            port=19908,
            user="root",
            password="2AhcG42BDE3AFEdEEC4hHgHDFH25hD32",
            database="railway",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if conexion.is_connected():
            print("Conexión exitosa a la BD")
            return conexion
    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
        return None

def insert_sensor_data(cursor, sensor_type, value):
    try:
        query = f"INSERT INTO sensor (tipo, fecha, valor) VALUES (%s, CURDATE(), %s)"
        cursor.execute(query, (sensor_type, value))
        db.commit()
        print(f"Dato insertado en sensor ({sensor_type}): {value}")
    except Exception as e:
        print(f"Error al insertar dato en sensor ({sensor_type}): {e}")

def insert_rfid_data(cursor, rfid_code, tarjeta_valida):
    try:
        query = "INSERT INTO rfid_data (rfid_code, tarjeta_valida, detection_time) VALUES (%s, %s, CURRENT_TIMESTAMP)"
        cursor.execute(query, (rfid_code, tarjeta_valida))
        db.commit()
        print(f"Dato insertado en rfid_data. Código RFID: {rfid_code}, Tarjeta válida: {tarjeta_valida}")
    except Exception as e:
        print(f"Error al insertar dato en rfid_data: {e}")

def guardar_en_excel_rfid_data(rfid_code, tarjeta_valida):
    try:
        # Leer el archivo Excel existente
        df = pd.read_excel(excel_file_name)

        # Agregar nueva fila al DataFrame
        new_row = {'rfid_code': rfid_code, 'tarjeta_valida': tarjeta_valida, 'detection_time': pd.Timestamp.now()}
        df = df.append(new_row, ignore_index=True)
        
        # Guardar el DataFrame actualizado en el archivo Excel
        df.to_excel(excel_file_name, index=False)
        print(f"Dato de tarjeta RFID guardado en Excel. Código RFID: {rfid_code}, Tarjeta válida: {tarjeta_valida}")
    except Exception as e:
        print(f"Error al guardar datos en Excel: {e}")

def enviar_datos_a_bd(data_json):
    try:
        cursor = db.cursor()

        if 'rfid' in data_json:
            tarjeta_valida = True  # Reemplazar con la lógica adecuada para determinar la validez de la tarjeta
            rfid_code = data_json['rfid']
            insert_rfid_data(cursor, rfid_code, tarjeta_valida)
            
            # Llamar a la función para guardar en Excel solo para datos de RFID
            guardar_en_excel_rfid_data(rfid_code, tarjeta_valida)

        if 'gas' in data_json:
            gas_value = data_json['gas']
            insert_sensor_data(cursor, 'GAS', gas_value)

        if 'temperatura' in data_json:
            temperatura_value = data_json['temperatura']
            insert_sensor_data(cursor, 'Temperatura', temperatura_value)

        if 'humedad' in data_json:
            humedad_value = data_json['humedad']
            insert_sensor_data(cursor, 'Humedad', humedad_value)

        cursor.close()
    except Exception as e:
        print(f"Error al enviar datos a la base de datos: {e}")

try:
    ensure_folder_exists(excel_file_path)  # Asegurar que la carpeta exista
    ensure_excel_file_exists()  # Asegurar que el archivo Excel exista
    db = conexionBD()
    while True:
        arduino_data = ser.readline().decode('utf-8').strip()
        print(f"Datos recibidos desde Arduino: {arduino_data}")

        try:
            data_json = json.loads(arduino_data)
            if isinstance(data_json, dict):
                enviar_datos_a_bd(data_json)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
        except Exception as e:
            print(f"Error general: {e}")

except KeyboardInterrupt:
    print("Detenido por el Usuario.")
finally:
    if db:
        db.close()






















