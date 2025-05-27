from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

from firebase_admin import db
from firebase_config import *

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar contraseña")
        self.setModal(True)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        self.label = QLabel("Introduce tu contraseña:")
        layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        self.confirm_button = QPushButton("Confirmar")
        self.confirm_button.clicked.connect(self.verify_password)
        layout.addWidget(self.confirm_button)

        self.password_correct = False

    def verify_password(self):
        contrasena_input = self.input.text()
        try:
            ref = db.reference("Usuarios")
            usuarios = ref.get()
            for _, datos in usuarios.items():
                if str(datos.get("Contraseña")) == contrasena_input:
                    self.password_correct = True
                    self.accept()
                    return
            self.error_label.setText("Contraseña incorrecta.")
        except Exception as e:
            self.error_label.setText("Error de conexión.")
