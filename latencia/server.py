from flask import Flask, jsonify
import pymysql
import random
import time
import socket

app = Flask(__name__)

# Configuración de conexión a RDS
DB_CONFIG = {
    "host": "tu-endpoint-rds.amazonaws.com",  # cambia esto
    "user": "admin",                          # tu usuario RDS
    "password": "password",                   # tu clave RDS
    "database": "bodega"
}

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/pedido", methods=["GET"])
def procesar_pedido():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Seleccionamos 1 a 10 items aleatorios de la bodega
        cursor.execute("SELECT id FROM items ORDER BY RAND() LIMIT %s", (random.randint(1, 10),))
        items = cursor.fetchall()

        ubicaciones = []
        for item in items:
            cursor.execute("SELECT ubicacion FROM items WHERE id=%s", (item["id"],))
            ubicacion = cursor.fetchone()
            if ubicacion:
                ubicaciones.append(ubicacion["ubicacion"])

        conn.close()

        # Simulamos optimización rápida (milisegundos)
        time.sleep(random.uniform(0.05, 0.15))

        return jsonify({
            "pedido_id": random.randint(1000, 9999),
            "items": len(items),
            "ubicaciones": ubicaciones,
            "ruta_optimizada": f"Ruta({len(ubicaciones)} puntos)",
            "instancia": socket.gethostname()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
