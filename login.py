import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from firebase_admin import db
from firebase_config import *

class VentanaLogin(QWidget):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #282C34;")

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.crear_seccion_izquierda()
        self.crear_seccion_derecha()

        self.verificar_modo()

    def crear_seccion_izquierda(self):
        left_container = QWidget()
        left_container.setStyleSheet("background-color: #343840;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        image_label = QLabel()
        pixmap = QPixmap("background.jpg")
        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaled(500, 700,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(image_label)

        self.layout.addWidget(left_container, 1)

    def crear_seccion_derecha(self):
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(60, 0, 60, 0)
        self.right_layout.setSpacing(0)

        self.right_layout.addStretch()

        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(25)

        self.title = QLabel("")
        self.title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 30px;
        """)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addWidget(self.title)

        self.entry_usuario = QLineEdit()
        self.entry_usuario.setPlaceholderText("Ingresa tu usuario")
        self.entry_usuario.setStyleSheet("""
            QLineEdit {
                border: 1px solid #7b7b7b;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid #07ad90;
                outline: none;
            }
        """)
        self.form_layout.addWidget(self.entry_usuario)

        self.entry_contrasena = QLineEdit()
        self.entry_contrasena.setPlaceholderText("Ingresa tu contraseña")
        self.entry_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_contrasena.setStyleSheet(self.entry_usuario.styleSheet())
        self.form_layout.addWidget(self.entry_contrasena)

        self.boton_accion = QPushButton()
        self.boton_accion.setStyleSheet("""
            QPushButton {
                background-color: #07ad90;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #079c82;
            }
        """)
        self.form_layout.addWidget(self.boton_accion)

        self.login_error_msj = QLabel("")
        self.login_error_msj.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #af0000;
        """)
        self.login_error_msj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_error_msj.hide()
        self.form_layout.addWidget(self.login_error_msj)

        self.right_layout.addWidget(self.form_container)
        self.right_layout.addStretch()

        self.layout.addWidget(self.right_container, 1)

    def verificar_modo(self):
        try:
            ref = db.reference("Usuarios")
            usuarios = ref.get()

            if usuarios:
                # Modo login
                self.title.setText("¡Bienvenido!")
                self.boton_accion.setText("Iniciar sesión")
                self.boton_accion.clicked.connect(self.verificar_login)
            else:
                # Modo registro
                self.title.setText("Registro de administrador")
                self.boton_accion.setText("Registrarse")
                self.boton_accion.clicked.connect(self.registrar_usuario)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo verificar usuarios: {e}")

    def verificar_login(self):
        usuario_input = self.entry_usuario.text()
        contrasena_input = self.entry_contrasena.text()

        try:
            ref = db.reference("Usuarios")
            usuarios = ref.get()

            if usuarios:
                for _, datos in usuarios.items():
                    nombre = str(datos.get("Nombre", ""))
                    contrasena = str(datos.get("Contraseña", ""))

                    if usuario_input == nombre and contrasena_input == contrasena:
                        self.login_error_msj.hide()
                        if self.on_login_success:
                            self.on_login_success()
                        self.close()
                        return

            self.login_error_msj.setText("Usuario o contraseña incorrectos.")
            self.login_error_msj.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo verificar el login: {e}")

    def registrar_usuario(self):
        usuario = self.entry_usuario.text().strip()
        contrasena = self.entry_contrasena.text().strip()

        if not usuario or not contrasena:
            self.login_error_msj.setText("Completa todos los campos.")
            self.login_error_msj.show()
            return

        try:
            ref = db.reference("Usuarios")
            ref.push({
                "Nombre": usuario,
                "Contraseña": contrasena
            })
            QMessageBox.information(self, "Registro exitoso", "Usuario registrado correctamente.")
            self.close()
            if self.on_login_success:
                self.on_login_success()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el usuario: {e}")
