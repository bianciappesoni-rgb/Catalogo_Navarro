import pandas as pd
import mysql.connector
from pathlib import Path

# 👉 Usá la misma config que ya usás hoy para conectarte a navarro_dwh
DB_CONFIG = {
    "host": "172.10.10.203",
    "user": "BianMKT",
    "password": "Bia2025*!",
    "database": "navarro_dwh",
}


def exportar_catalogo_a_csv():
    """
    Lee la VIEW catalogo_navarro y la exporta a data/catalogo.csv
    con las columnas que usa el catálogo público.
    """
    conn = mysql.connector.connect(**DB_CONFIG)

    query = """
        SELECT
            titulo,
            marca,
            familia,
            precio_texto,
            foto_url,
            url_aviso,
            fecha_data
        FROM catalogo_navarro;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Carpeta local /data al lado del código
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    salida = data_dir / "catalogo.csv"
    df.to_csv(salida, index=False, encoding="utf-8")

    print(f"✔ Exportados {len(df)} registros a {salida}")


if __name__ == "__main__":
    exportar_catalogo_a_csv()
