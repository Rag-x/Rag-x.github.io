import serial
import mysql.connector
import json
from datetime import datetime

ser = serial.Serial('COM4', 9600)  # Reemplazar 'COMX' con el puerto correcto para el Arduino
db = None  # Inicializa la variable de conexión como None

def connectionBD():
    print("ENTRO A LA CONEXION")
    try:
        # Conexión a la base de datos con los nuevos parámetros
        connection = mysql.connector.connect(
            host="monorail.proxy.rlwy.net",
            port=36072,
            user="root",
            passwd="1hF6f35-1-A-ehCg2Gh5gAdbaH6ACCC-",
            database="railway",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if connection.is_connected():
            print("Conexión exitosa a la BD")
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
        return None

try:
    db = connectionBD()  # Intenta establecer la conexión al inicio del script

    while True:
        arduino_data = ser.readline().decode('utf-8').strip()

        try:
            data_json = json.loads(arduino_data)

            if 'gas' in data_json:
                gas_value = data_json['gas']
                gas_query = f"INSERT INTO sensor (tipo, fecha, valor) VALUES ('GAS', NOW(), {gas_value})"
                cursor = db.cursor()
                cursor.execute(gas_query)
                db.commit()
                cursor.close()

            if 'temperatura' in data_json:
                temperatura_value = data_json['temperatura']
                temperatura_query = f"INSERT INTO sensor (tipo, fecha, valor) VALUES ('Temperatura', NOW(), {temperatura_value})"
                cursor = db.cursor()
                cursor.execute(temperatura_query)
                db.commit()
                cursor.close()

            if 'humedad' in data_json:
                humedad_value = data_json['humedad']
                humedad_query = f"INSERT INTO sensor (tipo, fecha, valor) VALUES ('Humedad', NOW(), {humedad_value})"
                cursor = db.cursor()
                cursor.execute(humedad_query)
                db.commit()
                cursor.close()

        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")

except KeyboardInterrupt:
    print("Detenido por el Usuario.")



