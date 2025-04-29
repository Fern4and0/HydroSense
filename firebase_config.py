import firebase_admin
from firebase_admin import credentials, db

# Ruta al archivo JSON de tu Service Account
cred = credentials.Certificate("DB/credenciales.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sistema-hidroponico-d3e3c-default-rtdb.firebaseio.com/'
})

db = db.reference()  # db_ref es ahora tu objeto de referencia

def get_latest_value(key):
    try:
        ref = db.child("datos/" + key)
        data = ref.get()
        if isinstance(data, dict):
            sorted_items = sorted(data.items(), key=lambda x: int(x[0]))
            return list(sorted_items)[-1][1]
        elif isinstance(data, list):
            return data[-1] if data else None
        return None
    except Exception as e:
        print(f"Error al obtener {key}:", e)
        return None
