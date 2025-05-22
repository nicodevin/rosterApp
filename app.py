from flask import Flask, render_template, request, send_file, redirect, url_for
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Acá vas a poner la lógica de procesamiento
        return "Procesamiento futuro"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
