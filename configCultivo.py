import json
import os

ARCHIVO_CULTIVO = "cultivo_seleccionado.json"

def guardar_cultivo_seleccionado(nombre_cultivo):
    with open(ARCHIVO_CULTIVO, "w") as archivo:
        json.dump({"cultivo": nombre_cultivo}, archivo)

def obtener_cultivo_seleccionado():
    if not os.path.exists(ARCHIVO_CULTIVO):
        return None
    with open(ARCHIVO_CULTIVO, "r") as archivo:
        data = json.load(archivo)
        return data.get("cultivo")
