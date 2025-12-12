from flask import Flask, render_template, redirect, url_for, request, send_file
from pathlib import Path
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


app = Flask(__name__)

# ==========================
# CONFIG RUTA CSV
# ==========================

DATA_PATH = Path(__file__).parent / "data" / "catalogo.csv"


def obtener_catalogo():
    """
    Lee el archivo CSV generado desde el scraping.
    Si algo falla, devuelve ([], mensaje_error).
    """
    try:
        if not DATA_PATH.exists():
            return [], f"No se encontró el archivo {DATA_PATH.name} en la carpeta data/"

        df = pd.read_csv(DATA_PATH)

        # 🔧 limpiar nombres de columnas (BOM / espacios)
        df.columns = (
            df.columns.astype(str)
            .str.replace("\ufeff", "", regex=False)
            .str.strip()
        )

        # 🔧 compatibilidad de nombre de fecha
        if "fecha_data" not in df.columns and "fecha_scraping" in df.columns:
            df = df.rename(columns={"fecha_scraping": "fecha_data"})

        # DEBUG para Render
        print("Columnas CSV:", list(df.columns))

        columnas_necesarias = [
            "titulo",
            "marca",
            "familia",
            "precio_texto",
            "foto_url",
            "url_aviso",
            "fecha_data",
        ]

        faltantes = [c for c in columnas_necesarias if c not in df.columns]
        if faltantes:
            return [], f"Faltan columnas en CSV: {faltantes}"

        productos = df[columnas_necesarias].to_dict(orient="records")
        return productos, None

    except Exception as e:
        print("Error leyendo catalogo.csv:", e)
        return [], str(e)


# ==========================
# RUTAS FLASK
# ==========================

@app.route("/")
def home():
    return redirect(url_for("catalogo"))


@app.route("/catalogo")
def catalogo():
    productos, error = obtener_catalogo()

    if error:
        return render_template("catalogo.html", productos=[], error=error)

    marca_sel = request.args.get("marca", "").strip()
    familia_sel = request.args.get("familia", "").strip()

    marcas = sorted({p["marca"] for p in productos if p.get("marca")})
    familias = sorted({p["familia"] for p in productos if p.get("familia")})

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


@app.route("/catalogo/print")
def catalogo_print():
    productos, error = obtener_catalogo()

    if error:
        return render_template(
            "catalogo_print.html",
            productos=[],
            error=error,
            marca_sel="",
            familia_sel=""
        )

    marca_sel = request.args.get("marca", "").strip()
    familia_sel = request.args.get("familia", "").strip()

    productos_filtrados = []
    for p in productos:
        if marca_sel and p.get("marca") != marca_sel:
            continue
        if familia_sel and p.get("familia") != familia_sel:
            continue
        productos_filtrados.append(p)

    return render_template(
        "catalogo_print.html",
        productos=productos_filtrados,
        error=error,
        marca_sel=marca_sel,
        familia_sel=familia_sel,
    )


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    print("Levantando Flask…")
    app.run(debug=True)
