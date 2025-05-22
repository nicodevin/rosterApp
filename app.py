from flask import Flask, render_template, request
import pdfplumber
import os

app = Flask(__name__)

def extraer_estadisticas(pdf_path):
    total_tv = 0.0
    total_tsv = 0.0
    dias_servicio = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                partes = line.strip().split()
                # Filtro: líneas largas con horas y sin VAC, D/L, *, ni nombres (no tripulación)
                if (
                    len(partes) >= 8 and
                    ":" in partes[-1] and
                    ":" in partes[-2] and
                    not any(x in line for x in ["VAC", "D/L", "*"])
                ):
                    # TSV = última columna
                    tsv = partes[-1]
                    # TV = anteúltima columna
                    tv = partes[-2]
                    # Sumar horas
                    if tv and tv.count(":") == 1:
                        h, m = map(int, tv.split(":"))
                        total_tv += h + m / 60
                    if tsv and tsv.count(":") == 1:
                        h, m = map(int, tsv.split(":"))
                        total_tsv += h + m / 60
                    dias_servicio += 1

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
