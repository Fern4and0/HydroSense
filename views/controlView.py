from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel,
    QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QFont

from firebase_config import *
from firebase_admin import db

class ControlView(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 25, 20, 25)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        title = QLabel("Control manual")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #55E8BE; font-size: 42px; font-weight: bold; margin-bottom: 50px;")
        main_layout.addWidget(title)

        # Contenedor gris oscuro
        container = QFrame()
        container.setStyleSheet("""
                background-color: #222222;
                border-radius: 10px;
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(150, 40, 150, 40)
        container_layout.setSpacing(25)

        # Diccionario de bombas con sus rutas en Firebase
        self.bombas = {
            "Bomba pH+": "Actuadores/Bomba-pH+/Estado",
            "Bomba pH-": "Actuadores/Bomba-pH-/Estado",
            "Bomba Nutrientes": "Actuadores/Bomba-Nutrientes/Estado"
        }

        for texto, ruta in self.bombas.items():
            row = QHBoxLayout()
            row.setSpacing(100)

            label = QLabel(texto)
            label.setStyleSheet("color: #d3d3d3; font-size: 38px; font-weight: bold;")
            row.addWidget(label)

            toggle = QCheckBox()
            toggle.setStyleSheet("""
                QCheckBox::indicator {
                    width: 100px;
                    height: 84px;
                }
                QCheckBox::indicator:unchecked {
                    image: url(assets/icons/toggle-off-solid.svg);
                }
                QCheckBox::indicator:checked {
                    image: url(assets/icons/toggle-on-solid.svg);
                }
            """)
            # Conecta el estado del botón a la función que actualiza Firebase
            toggle.stateChanged.connect(
                lambda state, ruta_firebase=ruta: self.actualizar_estado_firebase(ruta_firebase, state)
            )

            row.addStretch()
            row.addWidget(toggle)
            container_layout.addLayout(row)

        main_layout.addWidget(container)

        # Advertencia inferior
        warning = QLabel(
            "El tiempo que dure activado el botón es igual al tiempo que se activará la bomba.\n\n"
            "Usar valores excesivos puede alterar los niveles de pH o CE de forma perjudicial para las plantas.\n"
            "Asegúrate de conocer las necesidades del cultivo antes de activar cualquier bomba."
        )
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setStyleSheet("color: #a0a0a0; font-size: 18px;")
        main_layout.addWidget(warning)

    def actualizar_estado_firebase(self, ruta: str, estado: int):
        """Actualiza el valor booleano en Firebase según el estado del botón."""
        try:
            valor = bool(estado)  # estado == 2 (Checked), 0 (Unchecked)
            db.reference(ruta).set(valor)
            print(f"[Firebase] {ruta} actualizado a {valor}")
        except Exception as e:
            print(f"[ERROR Firebase] No se pudo actualizar {ruta}: {e}")
