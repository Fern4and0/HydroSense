from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from datetime import datetime, date

from firebase_config import *
from firebase_admin import db

from cultivoActual import cargar_cultivo_seleccionado

class TablaTemperatura(QWidget):
    def __init__(self):
        super().__init__()

        self.sensor_actual = "Temperatura"

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Contenedor para centrar el panel superior
        self.header_container_layout = QHBoxLayout()
        self.header_container_layout.setContentsMargins(0, 0, 0, 0)
        self.header_container_layout.addStretch()

        # Panel superior reducido a 840 px
        self.header_widget = QWidget()
        self.header_widget.setFixedWidth(840)
        self.header_widget.setFixedHeight(40)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(20, 10, 20, 10)

        self.title_label = QLabel("Temperatura")
        self.title_label.setFont(QFont("Arial", 14))
        self.title_label.setStyleSheet("color: #55E8BE; font-size: 20px;")

        fecha_actual = date.today().strftime("%d/%m/%Y")
        self.date_label = QLabel(fecha_actual)
        self.date_label.setFont(QFont("Arial", 12))
        self.date_label.setStyleSheet("color: #8C8C8C; font-size: 20px;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.date_label, 1)

        self.header_container_layout.addWidget(self.header_widget)
        self.header_container_layout.addStretch()
        self.main_layout.addLayout(self.header_container_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setFixedHeight(50)

        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Temperatura", "Hora", "Estado"])
        self.tabla.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tabla.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignRight)

        # Contenedor intermedio con padding para la tabla
        self.tabla_container_widget = QWidget()
        self.tabla_container_widget.setFixedWidth(840)
        self.tabla_container_widget.setObjectName("tabla_container_widget")

        tabla_container_layout = QVBoxLayout(self.tabla_container_widget)
        tabla_container_layout.setContentsMargins(20, 0, 20, 12)
        tabla_container_layout.setSpacing(0)
        tabla_container_layout.addWidget(self.tabla)

        tabla_container_centrado = QHBoxLayout()
        tabla_container_centrado.addStretch()
        tabla_container_centrado.addWidget(self.tabla_container_widget)
        tabla_container_centrado.addStretch()
        self.main_layout.addLayout(tabla_container_centrado)

        self.iniciar_timer_actualizacion()  # <<--- agregar esta línea al final del __init__

        self.obtener_datos_sensor()  # <<--- cargar datos la primera vez

        self.aplicar_estilos()

    def aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #222222;
                color: #ffffff;
                border: none;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #222222;
                color: #8C8C8C;
                padding: 10px;
                border: none;
                font-size: 20px;
                font-weight: normal;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 2px solid #333333;
            }
            QWidget#header_widget {
                border: 1.5px solid #333333;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                background-color: #222222;
            }
            QWidget#tabla_container_widget {
                background-color: #222222;
                border-left: 1.5px solid #333333;
                border-bottom: 1.5px solid #333333;
                border-right: 1.5px solid #333333;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QTableWidget QScrollBar:vertical {
                background: #5a5a5a;
                margin-top: 15px;
                margin-bottom: 15px;
                width: 14px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QTableWidget QScrollBar::handle:vertical {
                background: #8C8C8C;
                margin: 3.5px;
                min-height: 5px;
                border-radius: 10px;
            }
            QTableWidget QScrollBar::handle:vertical:hover {
                background: #b2b2b2;
            }
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {
                height: 0px;            /* Oculta las flechas */
                background: none;
                border-radius: 5px;
            }
            QTableWidget QScrollBar::add-page:vertical,
            QTableWidget QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        self.header_widget.setObjectName("header_widget")

    
    def obtener_datos_sensor(self, fecha_seleccionada=None):
        ruta_sensor = {
            "Temperatura": "Sensores/Sensor-Temperatura",
            "Conductividad Electrica": "Sensores/Sensor-CE",
            "Nivel de pH": "Sensores/Sensor-PH",
            "Nivel del agua": "Sensores/Sensor-NA",
            "pH-": "Sensores/Sensor-PHMenos",
            "pH+": "Sensores/Sensor-PHMas",
            "Nutrientes": "Sensores/Sensor-Nutrientes"
        }

        ruta = ruta_sensor.get(self.sensor_actual, "Sensores/Sensor-Temperatura")
        ref = db.reference(ruta)
        datos = ref.get()

        # Si no se pasa una fecha, usar la actual
        if fecha_seleccionada is None:
            fecha_filtrar = datetime.now().strftime("%Y-%m-%d")
        else:
            fecha_filtrar = fecha_seleccionada.toString("yyyy-MM-dd")

        datos_filtrados = []

        if datos:
            for key, value in datos.items():
                fecha_guardada = value.get("Fecha", "")
                if fecha_guardada.startswith(fecha_filtrar):
                    datos_filtrados.append({
                        "id": key,
                        "fecha": fecha_guardada,
                        "valor": value.get("Valor", None)
                    })

        datos_filtrados.sort(key=lambda x: x["fecha"], reverse=True)
        self.actualizar_tabla_con_datos(datos_filtrados)


    def actualizar_tabla_con_datos(self, datos):
        self.tabla.clearSpans()

        if not datos:
            self.tabla.clearContents()
            self.tabla.setRowCount(1)
            mensaje = QTableWidgetItem("No hay datos disponibles en esta fecha")
            mensaje.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            mensaje.setForeground(QColor("#888888"))
            self.tabla.setItem(0, 0, mensaje)
            self.tabla.setSpan(0, 0, 1, self.tabla.columnCount())
            return

        # Cargar cultivo seleccionado
        cultivo = cargar_cultivo_seleccionado()

        from rangosPlantas import Rangos_ideales

        Simbolos_sensor = {
            "Temperatura": "°C",
            "Conductividad Electrica": "mS/cm",
            "Nivel de pH": "pH",
            "Nivel del agua": "%",
            "pH-": "mL",
            "pH+": "mL",
            "Nutrientes": "mL"
        }

        def evaluar_estado(valor, sensor, cultivo):
            planta = Rangos_ideales["Plantas"].get(cultivo)
            if not planta:
                return "Desconocido", QColor("#888888")

            if sensor == "Temperatura":
                rangos = planta.get("temp", {})
                if rangos["malo"]["min"] <= valor <= rangos["malo"]["max"] or valor >= rangos["malo"]["extra_max"]:
                    return "Malo", QColor("#e3342f")
                elif rangos["regular_1"]["min"] <= valor <= rangos["regular_1"]["max"] or rangos["regular_2"]["min"] <= valor <= rangos["regular_2"]["max"]:
                    return "Regular", QColor("#ffed4a")
                elif rangos["bueno"]["min"] <= valor <= rangos["bueno"]["max"]:
                    return "Bueno", QColor("#4dc0b5")

            elif sensor == "Conductividad Electrica":
                rangos = planta.get("CE", {})
                if valor in rangos.get("regular", []):
                    return "Regular", QColor("#ffed4a")
                elif rangos["malo"]["min"] <= valor <= rangos["malo"]["max"] or valor >= rangos["malo"]["extra_max"]:
                    return "Malo", QColor("#e3342f")
                elif rangos["bueno"]["min"] <= valor <= rangos["bueno"]["max"]:
                    return "Bueno", QColor("#4dc0b5")

            elif sensor == "Nivel de pH":
                rangos = planta.get("pH", {})
                if valor in rangos.get("regular", []):
                    return "Regular", QColor("#ffed4a")
                elif rangos["malo"]["min"] <= valor <= rangos["malo"]["max"] or valor >= rangos["malo"]["extra_max"]:
                    return "Malo", QColor("#e3342f")
                elif rangos["bueno"]["min"] <= valor <= rangos["bueno"]["max"]:
                    return "Bueno", QColor("#4dc0b5")
                
            elif sensor == "Nivel del agua":
                if 31 <= valor < 69:
                    return "Regular", QColor("#ffed4a")
                elif valor <= 30:
                    return "Malo", QColor("#e3342f")
                elif valor >= 70:
                    return "Bueno", QColor("#4dc0b5")

            return "Desconocido", QColor("#888888")

        self.tabla.setRowCount(len(datos))

        for fila, dato in enumerate(datos):
            simbolo = Simbolos_sensor.get(self.sensor_actual, "")
            item_valor = QTableWidgetItem(f"{dato['valor']} {simbolo}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignLeft)

            item_fecha = QTableWidgetItem(dato['fecha'].split(' ')[1])
            item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            estado_texto, color_estado = evaluar_estado(dato["valor"], self.sensor_actual, cultivo)
            item_estado = QTableWidgetItem(estado_texto)
            item_estado.setForeground(color_estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignRight)

            self.tabla.setItem(fila, 0, item_valor)
            self.tabla.setItem(fila, 1, item_fecha)
            self.tabla.setItem(fila, 2, item_estado)

        for i in range(self.tabla.rowCount()):
            self.tabla.setRowHeight(i, 40)


    def iniciar_timer_actualizacion(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.obtener_datos_sensor)
        self.timer.start(3600 * 1000)  # 3600 segundos * 1000 ms = 1 hora