import json
import os

def cargar_cultivo_seleccionado():
    ruta = "cultivo_seleccionado.json"
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            datos = json.load(f)
            return datos.get("cultivo")
    return None