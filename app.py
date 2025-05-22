from flask import Flask, render_template, request
import pdfplumber
import os

app = Flask(__name__)

def extraer_estadisticas(pdf_path):
    horas_vuelo = 0
    horas_servicio = 0
    dias_servicio = 0
    actividades_servicio = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                # Filtrar líneas de actividad (vuelos, ELR, GUA)
                # Evitar D/L, *, VAC (días libres)
                if any(lib in line for lib in ["D/L", "VAC", "*"]):
                    continue
                # Buscar líneas con vuelos y actividades de servicio
                if "AR" in line or "ELR" in line or "GUA" in line:
                    dias_servicio += 1
                    actividades_servicio.append(line)
                    # Buscar horas de vuelo y servicio si están en la línea (ejemplo: "02:50 02:50 05:10")
                    partes = line.split()
                    for p in partes:
                        if ":" in p:
                            h, m = p.split(":")
                            try:
                                horas = int(h)
                                mins = int(m)
                                # Heurística: horas de vuelo suelen ser las primeras horas
                                if horas_vuelo == 0:
                                    horas_vuelo += horas + mins / 60
                                else:
                                    horas_servicio += horas + mins / 60
                            except:
                                continue

    return {
        "horas_vuelo": round(horas_vuelo, 2),
        "horas_servicio": round(horas_servicio, 2),
        "dias_servicio": dias_servicio,
        "actividades": actividades_servicio
    }

@app.route("/", methods=["GET", "POST"])
def index():
    stats = None
    actividades = []
    if request.method == "POST":
        if "pdf_file" in request.files:
            pdf = request.files["pdf_file"]
            pdf_path = os.path.join("/tmp", pdf.filename)
            pdf.save(pdf_path)
            stats = extraer_estadisticas(pdf_path)
            actividades = stats["actividades"]
            os.remove(pdf_path)
    return render_template("index.html", stats=stats, actividades=actividades)

if __name__ == "__main__":
    app.run(debug=True)
