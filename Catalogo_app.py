from flask import Flask, render_template, redirect, url_for, request
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

    # Si hubo error, devolvemos igual para mostrar el mensaje en pantalla
    if error:
        return render_template("catalogo.html", productos=[], error=error)

    # ---------- valores de los filtros (vienen por ?marca=xxx&familia=yyy) ----------
    marca_sel = request.args.get("marca", "").strip()
    familia_sel = request.args.get("familia", "").strip()

    # ---------- armamos listas únicas para los combos ----------
    marcas = sorted({p["marca"] for p in productos if p.get("marca")})
    familias = sorted({p["familia"] for p in productos if p.get("familia")})

    # ---------- aplicamos filtros en memoria ----------
    productos_filtrados = []
    for p in productos:
        if marca_sel and p.get("marca") != marca_sel:
            continue
        if familia_sel and p.get("familia") != familia_sel:
            continue
        productos_filtrados.append(p)

    return render_template(
        "catalogo.html",
        productos=productos_filtrados,
        error=error,
        marcas=marcas,
        familias=familias,
        marca_sel=marca_sel,
        familia_sel=familia_sel,
    )


if __name__ == "__main__":
    print("Levantando Flask…")
    app.run(debug=True)
