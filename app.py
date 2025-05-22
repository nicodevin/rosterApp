from flask import Flask, render_template, request
import pdfplumber
import os
import re

app = Flask(__name__)

def extraer_estadisticas(pdf_path):
    total_tv = 0.0
    total_tsv = 0.0
    dias_servicio = 0
    pattern = re.compile(r'(\d{2}:\d{2})')  # para encontrar horas tipo 05:15

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                if "TV" in line and "TSV" in line:
                    continue  # saltar encabezados
                if any(lib in line for lib in ["D/L", "VAC", "*"]):
                    continue  # saltar días libres
                if "TV" in line or "TSV" in line:
                    continue  # saltar líneas resumen o totales
                partes = line.split()
                tv_val = None
                tsv_val = None
                for idx, val in enumerate(partes):
                    if val == "TV" and idx + 1 < len(partes):
                        tv_val = partes[idx + 1]
                    if val == "TSV" and idx + 1 < len(partes):
                        tsv_val = partes[idx + 1]
                # Si encontramos valores válidos, sumamos
                if tv_val and re.match(r"\d{2}:\d{2}", tv_val):
                    h, m = tv_val.split(":")
                    minutos_vuelo = int(h) * 60 + int(m)
                    total_tv += minutos_vuelo / 60
                    dias_servicio += 1
                if tsv_val and re.match(r"\d{2}:\d{2}", tsv_val):
                    h, m = tsv_val.split(":")
                    minutos_servicio = int(h) * 60 + int(m)
                    total_tsv += minutos_servicio / 60

    return {
        "horas_vuelo": round(total_tv, 2),
        "horas_servicio": round(total_tsv, 2),
        "dias_servicio": dias_servicio
    }

@app.route("/", methods=["GET", "POST"])
def index():
    stats = None
    if request.method == "POST":
        if "pdf_file" in request.files:
            pdf = request.files["pdf_file"]
            pdf_path = os.path.join("/tmp", pdf.filename)
            pdf.save(pdf_path)
            stats = extraer_estadisticas(pdf_path)
            os.remove(pdf_path)
    return render_template("index.html", stats=stats)

if __name__ == "__main__":
    app.run(debug=True)
