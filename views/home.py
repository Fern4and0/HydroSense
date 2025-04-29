from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QApplication, QSizePolicy, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from firebase_config import db, get_latest_value


def evaluar_estado(tipo, valor):
    try:
        valor = float(valor)
        if tipo == "temperatura":
            if valor < 18:
                return 2
            elif valor <= 26:
                return 0
            else:
                return 1
        elif tipo == "ph":
            if 5.5 <= valor <= 6.5:
                return 0
            elif 4.5 <= valor < 5.5 or 6.5 < valor <= 7.5:
                return 1
            else:
                return 2
        elif tipo == "ce":
            if 1.2 <= valor <= 2.4:
                return 0
            elif 1.0 <= valor < 1.2 or 2.4 < valor <= 2.8:
                return 1
            else:
                return 2
        elif tipo == "agua":
            if valor > 60:
                return 0
            elif 40 <= valor <= 60:
                return 1
            else:
                return 2
    except:
        return 1


class CustomToolTip(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet("""
            background-color: #2B2B2B;
            color: white;
            border: 1px solid #55E8BE;
            border-radius: 6px;
            padding: 8px;
        """)
        self.setWordWrap(True)
        self.setMaximumWidth(280)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.hide()


class TempChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 4), facecolor="#1e1e1e")
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot("Temperatura")

    def get_data_from_firebase(self, key):
        try:
            ref = db.child("datos/" + key)
            data = ref.get()
            if isinstance(data, dict):
                sorted_items = sorted(data.items(), key=lambda x: int(x[0]))
                return [v for _, v in sorted_items]
            elif isinstance(data, list):
                return data
            return [0] * 24
        except Exception as e:
            print("Error al obtener datos de Firebase:", e)
            return [0] * 24

    def plot(self, title):
        self.axes.clear()
        self.axes.set_facecolor("#1e1e1e")
        self.axes.set_title(title, color='white', pad=20)

        key_map = {
            "Temperatura": "temperatura",
            "Nivel de pH": "ph",
            "Nivel de CE": "ce",
            "Nivel de agua": "nivel_agua"
        }

        key = key_map.get(title, "temperatura")
        y = self.get_data_from_firebase(key)
        x = list(range(len(y)))

        self.axes.plot(x, y, color="#55E8BE", linewidth=2.5)

        self.axes.set_xlabel("Muestra", color='white', labelpad=15)
        self.axes.set_ylabel("Valor", color='white', labelpad=15)
        self.axes.set_xlim(0, len(y)-1)
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')

        for spine in self.axes.spines.values():
            spine.set_color('white')

        self.fig.tight_layout()
        self.draw()


def create_card(title, value, tooltip_text=""):
    card = QFrame()
    card.setMinimumSize(200, 100)
    card.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
    card.setStyleSheet("""
        QFrame {
            background-color: #1e1e1e;
            border-radius: 10px;
            color: white;
        }
        QLabel {
            color: white;
        }
    """)

    layout = QVBoxLayout()

    title_layout = QHBoxLayout()
    label_title = QLabel(title)
    label_title.setStyleSheet("font-size: 16px; color: #55E8BE;")

    info_icon = QPushButton("ℹ️")
    info_icon.setCursor(Qt.CursorShape.PointingHandCursor)
    info_icon.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 14px;
            color: white;
        }
        QPushButton:hover {
            color: #55E8BE;
        }
    """)
    info_icon.setFixedSize(20, 20)
    info_icon.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    custom_tooltip = CustomToolTip(tooltip_text, info_icon)

    def show_tooltip():
        pos = info_icon.mapToGlobal(QPoint(info_icon.width()//2, info_icon.height()))
        custom_tooltip.move(pos.x() - custom_tooltip.width()//2, pos.y() + 10)
        custom_tooltip.show()

    def hide_tooltip():
        custom_tooltip.hide()

    info_icon.enterEvent = lambda event: show_tooltip()
    info_icon.leaveEvent = lambda event: hide_tooltip()

    title_layout.addWidget(label_title)
    title_layout.addWidget(info_icon)
    title_layout.addStretch()

    label_value = QLabel(value)
    label_value.setStyleSheet("font-size: 26px; font-weight: bold;")

    layout.addLayout(title_layout)
    layout.addWidget(label_value)
    card.setLayout(layout)

    return card


def create_status_card(title, active_index):
    colors = ["#55E8BE", "#FFD93D", "#F05A5A"]
    card = QFrame()
    card.setStyleSheet("background-color: #2B2B2B; border-radius: 14px;")
    card.setMinimumSize(160, 120)
    card.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

    layout = QVBoxLayout()
    layout.setContentsMargins(6, 6, 6, 6)

    label = QLabel(title)
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    label.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding-bottom: 5px;")
    layout.addWidget(label)

    dot_row = QHBoxLayout()
    dot_row.setSpacing(12)

    for i in range(3):
        vbox = QVBoxLayout()
        arrow = QLabel("▼" if i == active_index else "")
        arrow.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        arrow.setStyleSheet(f"color: {colors[active_index]}; font-size: 18px;")

        dot = QLabel("●")
        dot.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        dot.setStyleSheet(f"""
            font-size: 40px;
            color: {colors[i] if i == active_index else '#777777'};
        """)

        vbox.addWidget(arrow)
        vbox.addWidget(dot)
        dot_row.addLayout(vbox)

    layout.addLayout(dot_row)
    card.setLayout(layout)
    return card


class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráficas de Monitoreo")
        self.setStyleSheet("background-color: #121212;")
        self.resize(1920, 1080)

        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(30, 30, 30, 30)

        self.card_layout = QHBoxLayout()
        self.card_layout.setSpacing(20)
        content_layout.addLayout(self.card_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        chart_titles = ["Temperatura", "Nivel de pH", "Nivel de CE", "Nivel de agua"]

        for title in chart_titles:
            btn = QPushButton(title)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #55E8BE;
                    border-radius: 10px;
                    padding: 6px 16px;
                    color: #55E8BE;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #55E8BE;
                    color: black;
                }
            """)
            btn.clicked.connect(lambda _, t=title: self.chart.plot(t))
            button_layout.addWidget(btn)
            self.button_group.addButton(btn)

        content_layout.addLayout(button_layout)

        graph_layout = QHBoxLayout()
        graph_layout.setSpacing(30)

        self.chart = TempChart()
        graph_layout.addWidget(self.chart, stretch=3)

        status_container = QWidget()
        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(20)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        status_container.setLayout(self.status_layout)

        graph_layout.addWidget(status_container, stretch=1)
        content_layout.addLayout(graph_layout)

        first_button = self.button_group.buttons()[0]
        first_button.setChecked(True)
        self.chart.plot(first_button.text())

        self.actualizar_datos()
        self.iniciar_timer()

    def iniciar_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(10000)

    def actualizar_datos(self):
        cards_data = {
            "Temperatura": (get_latest_value("temperatura"), " °C", "Temperatura ideal: entre 18°C y 26°C para un crecimiento óptimo."),
            "Nivel de pH": (get_latest_value("ph"), "", "El pH óptimo para cultivos hidropónicos está entre 5.5 y 6.5."),
            "Nivel de CE": (get_latest_value("ce"), " mS/cm", "CE ideal: 1.2 - 2.4 mS/cm para nutrientes en solución."),
            "Nivel de agua": (get_latest_value("nivel_agua"), "%", "El nivel de agua debe mantenerse por encima del 60% para evitar daños en raíces.")
        }

        for i in reversed(range(self.card_layout.count())):
            self.card_layout.itemAt(i).widget().deleteLater()

        for nombre, (valor, sufijo, tooltip) in cards_data.items():
            card = create_card(nombre, f"{valor}{sufijo}", tooltip)
            self.card_layout.addWidget(card)

        estado_temp = evaluar_estado("temperatura", cards_data["Temperatura"][0])
        estado_ph = evaluar_estado("ph", cards_data["Nivel de pH"][0])
        estado_ce = evaluar_estado("ce", cards_data["Nivel de CE"][0])
        estado_agua = evaluar_estado("agua", cards_data["Nivel de agua"][0])

        for i in reversed(range(self.status_layout.count())):
            self.status_layout.itemAt(i).widget().deleteLater()

        self.status_layout.addWidget(create_status_card("Temperatura", estado_temp))
        self.status_layout.addWidget(create_status_card("Nivel de pH", estado_ph))
        self.status_layout.addWidget(create_status_card("Nivel de CE", estado_ce))
        self.status_layout.addWidget(create_status_card("Nivel de agua", estado_agua))

        current_button = next((b for b in self.button_group.buttons() if b.isChecked()), None)
        if current_button:
            self.chart.plot(current_button.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeView()
    window.showMaximized()
    sys.exit(app.exec())
