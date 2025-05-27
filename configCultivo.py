import json
import os
from datetime import date

ARCHIVO_CULTIVO = "cultivo_seleccionado.json"

def guardar_cultivo_seleccionado(nombre_visible, clave_interna):
    with open(ARCHIVO_CULTIVO, "w") as archivo:
        json.dump({
            "nombre_visible": nombre_visible,
            "clave_interna": clave_interna,
            "fecha_inicio": date.today().isoformat()
        }, archivo)

def obtener_cultivo_seleccionado():
    if not os.path.exists(ARCHIVO_CULTIVO):
        return None, None, None
    with open(ARCHIVO_CULTIVO, "r") as archivo:
        data = json.load(archivo)
        return (
            data.get("nombre_visible"),
            data.get("clave_interna"),
            data.get("fecha_inicio")
        )
