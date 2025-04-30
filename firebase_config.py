import firebase_admin
from firebase_admin import credentials

# Ruta al archivo JSON de tu Service Account
cred = credentials.Certificate("DB/credenciales.json")

firebase_admin.initialize_app(cred, {
     'databaseURL': 'https://sistema-hidroponico-2d761-default-rtdb.firebaseio.com/'
})


