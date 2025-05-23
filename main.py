import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame
)
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap
from PyQt6.QtCore import Qt

from views.cultivoView import CultivoView
from views.home import HomeView
from views.historyView.history import HistoryView
from login import VentanaLogin


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("App")
        self.setGeometry(100, 100, 1280, 720)

        # Cargar fuente de Font Awesome
        self.icon_font_family = self.load_fontawesome()

        # Layout principal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Contenido principal
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #000000;")
        self.setup_pages()
        main_layout.addWidget(self.content_stack, 1)

        # Widget central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #000000;")
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Conexiones
        self.setup_connections()

    def load_fontawesome(self):
        """Carga la fuente TTF de Font Awesome y devuelve el nombre de la familia"""
        font_path = os.path.join("assets", "icons", "iconos.otf")  # Asegúrate de tener este archivo
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return families[0]
        return None

    def create_sidebar(self):
        """Crea la barra lateral con logo y botones"""
        sidebar = QFrame()
        sidebar.setFixedWidth(100)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #222222;
                border: 2px solid #333333;
                border-radius: 10px;
                margin: 15px;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(8)

        # Logo en la parte superior
        logo_label = QLabel()
        logo_path = os.path.join("assets", "Pendiente")
        if os.path.exists(logo_path):
            logo_label.setPixmap(QPixmap(logo_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sidebar_layout.addWidget(logo_label)

        # Botones
        self.home_btn = self.create_icon_button("\uf015", "Inicio")
        self.home_btn.setChecked(True)

        self.history_btn = self.create_icon_button("\uf1da", "Historial")
        self.cultivo_btn = self.create_icon_button("\ue5aa","Cultivo")
        self.noty_btn = self.create_icon_button("\uf0f3", "Notificaciones")

        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.history_btn)
        sidebar_layout.addWidget(self.cultivo_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.noty_btn)

        sidebar.setLayout(sidebar_layout)
        return sidebar

    def create_icon_button(self, icon_char, tooltip):
        """Crea un botón con ícono de Font Awesome"""
        btn = QPushButton(icon_char)
        if self.icon_font_family:
            btn.setFont(QFont(self.icon_font_family, 24))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 12px;
                color: white;
            }
            QPushButton:hover {
                color: #55E8BE;
            }
            QPushButton:checked {
                color: #55E8BE;
            }
        """)
        return btn

    def setup_pages(self):
        """Agrega las vistas externas"""
        self.cultivo_page = CultivoView()
        self.home_page = HomeView()
        self.history_page = HistoryView()

        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.history_page)
        self.content_stack.addWidget(self.cultivo_page)

    def setup_connections(self):
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.history_btn.clicked.connect(lambda: self.switch_page(1))
        self.cultivo_btn.clicked.connect(lambda: self.switch_page(2))
        self.noty_btn.clicked.connect(lambda: print("Notificaciones"))

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        self.home_btn.setChecked(index == 0)
        self.history_btn.setChecked(index == 1)
        self.cultivo_btn.setChecked(index == 2)
        self.noty_btn.setChecked(False)

        if index == 1:
            self.history_page.calendario_widget.actualizar_tabla_con_fecha_seleccionada()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()

    def abrir_main():
        main_window.show()

    login_window = VentanaLogin(on_login_success=abrir_main)
    login_window.show()

    sys.exit(app.exec())
