from flask import Flask, render_template, redirect, url_for
from pathlib import Path
import pandas as pd

app = Flask(__name__)

# ==========================
# CONFIG RUTA CSV
# ==========================

# data/catalogo.csv (al lado de este .py)
DATA_PATH = Path(__file__).parent / "data" / "catalogo.csv"


def obtener_catalogo():
    """
    Lee el archivo CSV generado desde la VIEW catalogo_navarro.
    Si algo falla, devuelve ([], mensaje_error).
    """
    try:
        if not DATA_PATH.exists():
            return [], f"No se encontró el archivo {DATA_PATH.name} en la carpeta data/"

        df = pd.read_csv(DATA_PATH)

        # Nos aseguramos de que existan las columnas que usa el template
        columnas_necesarias = [
            "titulo",
            "marca",
            "familia",
            "precio_texto",
            "foto_url",
            "url_aviso",
            "fecha_data",
        ]
        for col in columnas_necesarias:
            if col not in df.columns:
                return [], f"Falta la columna '{col}' en el CSV de catálogo"

        # Convertir a lista de dicts para que Jinja pueda usar p.xxx
        productos = df.to_dict(orient="records")
        return productos, None

    except Exception as e:
        print("Error leyendo catalogo.csv:", e)
        return [], str(e)


# ==========================
# RUTAS FLASK
# ==========================

@app.route("/")
def home():
    # Redirigimos directo al catálogo
    return redirect(url_for("catalogo"))


@app.route("/catalogo")
def catalogo():
    productos, error = obtener_catalogo()
    return render_template("catalogo.html", productos=productos, error=error)


if __name__ == "__main__":
    print("Levantando Flask…")
    app.run(debug=True)
