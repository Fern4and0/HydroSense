from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QApplication, QSizePolicy, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
from firebase_config import *
from firebase_admin import db
from rangosPlantas import rangos_ideales

    

# ⚙️ Planta actual para evaluar
def get_latest_value(sensor_key):
    ref = db.reference("Sensores/" + sensor_key)
    data = ref.get()
    if data:
        sorted_data = sorted(data.items(), key=lambda item: item[1].get("Fecha", ""), reverse=True)
        for _, entry in sorted_data:
            valor = entry.get("Valor")
            try:
                if float(valor) != 1.0:
                    return valor
            except:
                continue
    return None

# ⚙️ Planta actual para evaluar
PLANTA_ACTUAL = "Cilantro"

def obtener_rangos_local(planta, parametro):
    try:
        return rangos_ideales["Plantas"][planta][parametro]
    except KeyError:
        return {}

def evaluar_estado_local(valor, rangos):
    try:
        valor = float(valor)
        bueno = rangos.get("bueno", {})
        regular = rangos.get("regular", [])
        regular_1 = rangos.get("regular_1", {})
        regular_2 = rangos.get("regular_2", {})
        malo = rangos.get("malo", {})

        if bueno.get("min") <= valor <= bueno.get("max"):
            return 0  # verde
        if any([
            isinstance(regular, list) and valor in [float(v) for v in regular],
            regular_1.get("min", -999) <= valor <= regular_1.get("max", -999),
            regular_2.get("min", -999) <= valor <= regular_2.get("max", -999),
        ]):
            return 1  # amarillo
        if valor <= malo.get("max", -999) or valor >= malo.get("extra_max", 999):
            return 2  # rojo

    except Exception as e:
        print(f"Error al evaluar estado: {e}")
    return 1


def evaluar_estado(tipo, valor):
    try:
        valor = float(valor)
        if tipo == "agua":
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
            ref = db.reference("Sensores/" + key)
            data = ref.get()
            if data:
                # Convertimos todos los datos a listas ordenadas por fecha
                sorted_data = sorted(data.items(), key=lambda item: item[1].get("Fecha", ""))
                values = [float(entry[1]["Valor"]) for entry in sorted_data if "Valor" in entry[1]]
                
                # Eliminar últimos hasta 3 valores si son iguales a 1
                while values and values[-1] == 1.0:
                    values.pop()
                return values
        except Exception as e:
            print("Error al obtener datos de Firebase:", e)
        return []

    def plot(self, title):
        self.axes.clear()
        self.axes.set_facecolor("#1e1e1e")
        self.axes.set_title(title, color='white', pad=20)

        key_map = {
            "Temperatura": "Sensor-Temperatura",
            "Nivel de pH": "Sensor-PH",
            "Nivel de CE": "Sensor-CE",
            "Nivel de agua": "Sensor-NA"
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
    # Estado: 0 = bueno, 1 = regular, 2 = malo
    colors = ["#55E8BE", "#FFD93D", "#F05A5A"]
    emojis = ["😀", "😐", "😟"]
    textos = ["Bueno", "Regular", "Malo"]

    card = QFrame()
    card.setStyleSheet("background-color: #2B2B2B; border-radius: 14px;")
    card.setMinimumSize(160, 120)
    card.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

    layout = QVBoxLayout()
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    # Título arriba
    label = QLabel(title)
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
    layout.addWidget(label)

    # Fila horizontal: cara + texto
    face_row = QHBoxLayout()
    face_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

    emoji_label = QLabel(emojis[active_index])
    emoji_label.setStyleSheet(f"""
        font-size: 42px;
        color: {colors[active_index]};
    """)
    emoji_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    texto_label = QLabel(textos[active_index])
    texto_label.setStyleSheet(f"""
        font-size: 18px;
        color: {colors[active_index]};
        font-weight: bold;
        padding-left: 10px;
    """)
    texto_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    face_row.addWidget(emoji_label)
    face_row.addWidget(texto_label)

    layout.addLayout(face_row)
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
            "Temperatura": (get_latest_value("Sensor-Temperatura"), " °C", "Temperatura ideal: entre 18°C y 26°C para un crecimiento óptimo."),
            "Nivel de pH": (get_latest_value("Sensor-PH"), "", "El pH óptimo para cultivos hidropónicos está entre 5.5 y 6.5."),
            "Nivel de CE": (get_latest_value("Sensor-CE"), " mS/cm", "CE ideal: 1.2 - 2.4 mS/cm para nutrientes en solución."),
            "Nivel de agua": (get_latest_value("Sensor-NA"), "%", "El nivel de agua debe mantenerse por encima del 60% para evitar daños en raíces.")
        }

        for i in reversed(range(self.card_layout.count())):
            self.card_layout.itemAt(i).widget().deleteLater()

        for nombre, (valor, sufijo, tooltip) in cards_data.items():
            card = create_card(nombre, f"{valor}{sufijo}", tooltip)
            self.card_layout.addWidget(card)

        estado_temp = evaluar_estado_local(
            cards_data["Temperatura"][0],
            obtener_rangos_local(PLANTA_ACTUAL, "temp")
        )

        estado_ph = evaluar_estado_local(
            cards_data["Nivel de pH"][0],
            obtener_rangos_local(PLANTA_ACTUAL, "pH")
        )

        estado_ce = evaluar_estado_local(
            cards_data["Nivel de CE"][0],
            obtener_rangos_local(PLANTA_ACTUAL, "CE")
        )

        estado_agua = evaluar_estado("agua", cards_data["Nivel de agua"][0])  # Sigue con la función antigua si no está en rangos


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
