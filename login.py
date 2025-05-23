import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression

class VentanaLogin(QWidget):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #282C34;")

        # Layout principal
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.crear_seccion_izquierda()
        self.crear_seccion_derecha()

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
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(60, 0, 60, 0)
        right_layout.setSpacing(0)

        right_layout.addStretch()

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(25)

        title = QLabel("¡Bienvenido!")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 30px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title)

        self.entry_usuario = QLineEdit()
        self.entry_usuario.setPlaceholderText("Ingresa tu correo")
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
        form_layout.addWidget(self.entry_usuario)

        self.email_error_msj = QLabel("Por favor ingresa un correo electrónico válido")
        self.email_error_msj.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #af0000;
        """)
        self.email_error_msj.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.email_error_msj.hide()
        form_layout.addWidget(self.email_error_msj)

        email_regex = QRegularExpression(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        email_validator = QRegularExpressionValidator(email_regex, self)
        self.entry_usuario.setValidator(email_validator)

        self.entry_contrasena = QLineEdit()
        self.entry_contrasena.setPlaceholderText("Ingresa tu contraseña")
        self.entry_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_contrasena.setStyleSheet(self.entry_usuario.styleSheet())
        form_layout.addWidget(self.entry_contrasena)

        self.boton_login = QPushButton("Iniciar sesión")
        self.boton_login.setStyleSheet("""
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
        self.boton_login.clicked.connect(self.verificar_login)
        form_layout.addWidget(self.boton_login)

        self.login_error_msj = QLabel("Tus credenciales son incorrectas, por favor inténtalo de nuevo")
        self.login_error_msj.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #af0000;
        """)
        self.login_error_msj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_error_msj.hide()
        form_layout.addWidget(self.login_error_msj)

        links_container = QWidget()
        links_layout = QHBoxLayout(links_container)
        links_layout.setContentsMargins(0, 20, 0, 0)
        links_layout.setSpacing(10)

        self.link_olvide = QLabel("<a href='#' style='color: #6c757d; text-decoration: none;'></a>")
        self.link_olvide.setOpenExternalLinks(True)

        self.link_signup = QLabel("<a href='#' style='color: #6c757d; text-decoration: none;'></a>")
        self.link_signup.setOpenExternalLinks(True)

        links_layout.addStretch()
        links_layout.addWidget(self.link_olvide)
        links_layout.addWidget(QLabel("•"))
        links_layout.addWidget(self.link_signup)
        links_layout.addStretch()

        form_layout.addWidget(links_container)
        right_layout.addWidget(form_container)

        right_layout.addStretch()

        self.layout.addWidget(right_container, 1)

    def verificar_login(self):
        usuario_correcto = "admin@example.com"
        contrasena_correcta = "1234"

        if not self.entry_usuario.hasAcceptableInput():
            self.email_error_msj.show()
            return

        if (self.entry_usuario.text() == usuario_correcto and 
            self.entry_contrasena.text() == contrasena_correcta):
            self.login_error_msj.hide()
            if self.on_login_success:
                self.on_login_success()
            self.close()
        else:
            self.login_error_msj.setText("Tus credenciales son incorrectas, por favor inténtalo de nuevo")
            self.login_error_msj.show()
