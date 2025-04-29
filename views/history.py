from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QCalendarWidget, QButtonGroup,
)
from PyQt6.QtCore import Qt, QTimer, QDate, QLocale, QSize
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QTextCharFormat, QBrush, QPen
from datetime import datetime, date
import sys

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("DB/credenciales.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sistema-hidroponico-cac0b-default-rtdb.firebaseio.com/'
})


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

        # Si no hay datos, mostrar un mensaje en la tabla
        if not datos:
            self.tabla.clearContents()
            self.tabla.setRowCount(1)
            mensaje = QTableWidgetItem("No hay datos disponibles en esta fecha")
            mensaje.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            mensaje.setForeground(QColor("#888888"))  # color gris claro
            self.tabla.setItem(0, 0, mensaje)
            self.tabla.setSpan(0, 0, 1, self.tabla.columnCount())  # Unir las columnas
            return  # No sigas procesando datos

        # Si hay datos, proceder normalmente
        Simbolos_sensor = {
            "Temperatura": "°C",
            "Conductividad Electrica": "µS/cm",
            "Nivel de pH": "pH",
            "Nivel del agua": "%",
            "pH-": "mL",
            "pH+": "mL",
            "Nutrientes": "mL"
        }

        Margenes_sensor = {
            "Temperatura": [
                (15, "#e3342f", "Malo"),
                (25, "#4dc0b5", "Bueno"),
                (30, "#ffed4a", "Aceptable"),
                (float('inf'), "#e3342f", "Malo")
            ],
            "Conductividad Electrica": [
                (500, "#e3342f", "Bajo"),
                (1500, "#4dc0b5", "Óptimo"),
                (float('inf'), "#ffed4a", "Alto")
            ],
            "Nivel de pH": [
                (5.5, "#e3342f", "Ácido"),
                (6.5, "#4dc0b5", "Óptimo"),
                (7.5, "#ffed4a", "Alcalino"),
                (float('inf'), "#e3342f", "Muy Alcalino")
            ],
            "Nivel del agua": [
                (30, "#e3342f", "Bajo"),
                (70, "#ffed4a", "Medio"),
                (float('inf'), "#4dc0b5", "Alto")
            ]
        }

        self.tabla.setRowCount(len(datos))  # Ajustar cantidad de filas

        for fila, dato in enumerate(datos):
            simbolo = Simbolos_sensor.get(self.sensor_actual, "")
            item_valor = QTableWidgetItem(f"{dato['valor']} {simbolo}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignLeft)

            item_fecha = QTableWidgetItem(dato['fecha'].split(' ')[1])  # solo hora
            item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            valor = dato['valor']
            margenes = Margenes_sensor.get(self.sensor_actual, [])
            estado_texto = "Desconocido"
            color_estado = QColor("#888888")

            for limite, color, texto in margenes:
                if valor <= limite:
                    estado_texto = texto
                    color_estado = QColor(color)
                    break

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


class QCustomCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        self.setNavigationBarVisible(True)
        self.setDateEditEnabled(False)
        
        locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
        self.setLocale(locale)

    def paintCell(self, painter, rect, date):
        # Pintar solo los días del mes visible
        if date.month() != self.monthShown() or date.year() != self.yearShown():
            return  # No pintar días fuera del mes actual
        super().paintCell(painter, rect, date)

class CalendarioPersonalizado(QWidget):
    def __init__(self, tabla, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabla = tabla 

        self.calendario = QCustomCalendar()
        
        # Ocultar botones de selección de mes/año
        self.calendario.findChild(QWidget, "qt_calendar_monthbutton").setEnabled(False)
        self.calendario.findChild(QWidget, "qt_calendar_yearbutton").setEnabled(False)

        boton_anterior = self.calendario.findChild(QWidget, "qt_calendar_prevmonth")
        boton_siguiente = self.calendario.findChild(QWidget, "qt_calendar_nextmonth")

        boton_anterior.setIcon(QIcon("assets/icons/caret-left-solid.svg"))
        boton_siguiente.setIcon(QIcon("assets/icons/caret-right-solid.svg"))

        boton_anterior.setIconSize(QSize(30, 30))
        boton_siguiente.setIconSize(QSize(30, 30))

        self.calendario.selectionChanged.connect(self.actualizar_tabla_con_fecha_seleccionada)


        layout.addWidget(self.calendario)

        self.setStyleSheet(""" 
            QWidget {
                background-color: #222222;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }

            QCalendarWidget {
                background-color: #222222;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #222222;
                border: 1.5px solid #333333;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                min-height: 37px;
                max-height: 37px;
                padding: 0px;
            }

            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {
                color: white;
                background-color: transparent;
                font-size: 16px;
                font-weight: bold;
                padding: 5px 0px;
                text-transform: uppercase;
            }

            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                color: #8C8C8C;
                background-color: transparent;
                border: none;
                font-size: 25px;
                min-width: 30px;
                padding: 5px 15px;
            }

            QCalendarWidget QMenu {
                background-color: #222222;
                color: white;
                border: 1px solid #333333;
            }

            QCalendarWidget QMenu::item:selected {
                background-color: #222222;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: transparent;
                selection-color: #ffffff;
                background-color: #222222;
            }

            QCalendarWidget QTableView {
                background-color: #222222;
                font-size: 14px;
                border-left: 1.5px solid #333333;
                border-right: 1.5px solid #333333;
                border-bottom: 1.5px solid #333333;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                outline: none;
            }
                           
            QCalendarWidget QHeaderView::section:horizontal {
                color: #000;
                font-weight: bold;
                font-size: 40px;
            }

            QCalendarWidget QAbstractItemView::item {
                background-color: #222222;
                color: #ffffff;
                padding: 5px;
                border-radius: 15px;
                margin: 1px;
            }

            QCalendarWidget QAbstractItemView::item:selected {
                background-color: transparent;
                color: #55E8BE;
            }
        """)

    def actualizar_tabla_con_fecha_seleccionada(self):
        fecha = self.calendario.selectedDate()
        fecha_formateada = fecha.toString("dd/MM/yyyy")
        self.tabla.date_label.setText(fecha_formateada)
        self.tabla.obtener_datos_sensor(fecha)



class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        # Layout principal horizontal (sidebar + contenido)
        main_layout = QHBoxLayout(self)
        # main_layout.setContentsMargins(0, 0, 0, 0)

        # Contenedor derecho
        right_container = QVBoxLayout()
        # right_container.setContentsMargins(0, 0, 0, 0)
        # right_container.setSpacing(10)

        # Navbar superior
        navbar = QHBoxLayout()
        btn_temp = QPushButton("Temperatura")
        btn_temp.setCheckable(True)
        btn_temp.setChecked(True)  
        btn_CE = QPushButton("Conductividad Electrica")
        btn_CE.setCheckable(True)
        btn_PH = QPushButton("Nivel de pH")
        btn_PH.setCheckable(True)
        btn_NA = QPushButton("Nivel del agua")
        btn_NA.setCheckable(True)
        btn_PHNegativo = QPushButton("pH-")
        btn_PHPositivo = QPushButton("pH+")
        btn_Nutrientes = QPushButton("Nutrientes")

        sensor_group = QButtonGroup(self)
        sensor_group.setExclusive(True)

        sensor_group.addButton(btn_temp)
        sensor_group.addButton(btn_CE)
        sensor_group.addButton(btn_PH)
        sensor_group.addButton(btn_NA)
        sensor_group.addButton(btn_PHNegativo)
        sensor_group.addButton(btn_PHPositivo)
        sensor_group.addButton(btn_Nutrientes)

        btn_temp.clicked.connect(lambda: self.cambiar_sensor("Temperatura"))
        btn_CE.clicked.connect(lambda: self.cambiar_sensor("Conductividad Electrica"))
        btn_PH.clicked.connect(lambda: self.cambiar_sensor("Nivel de pH"))
        btn_NA.clicked.connect(lambda: self.cambiar_sensor("Nivel del agua"))
        btn_PHNegativo.clicked.connect(lambda: self.cambiar_sensor("pH-"))
        btn_PHPositivo.clicked.connect(lambda: self.cambiar_sensor("pH+"))
        btn_Nutrientes.clicked.connect(lambda: self.cambiar_sensor("Nutrientes"))

        btn_temp.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_CE.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_PH.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_NA.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_PHNegativo.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_PHPositivo.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_Nutrientes.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        navbar.addWidget(btn_temp)
        navbar.addWidget(btn_CE)
        navbar.addWidget(btn_PH)
        navbar.addWidget(btn_NA)
        navbar.addWidget(btn_PHNegativo)
        navbar.addWidget(btn_PHPositivo)
        navbar.addWidget(btn_Nutrientes)
        
        self.setStyleSheet("""
            QPushButton {
                margin-top: 10px;
                padding: 0 10px 0 10px;
                height: 30px;
                background-color: #121212;
                color: #55E8BE;
                border: 1px solid #66ffcc;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px
            }
            QPushButton:hover {
                background-color: #55E8BE;
                color: #121212;
            }
            QPushButton:checked {
                background-color: #55E8BE;
                color: #121212;
            }
            """)
        

        # Contenedor inferior con la tabla y el calendario
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setSpacing(10)

        # Layout para la tabla
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.mi_tabla_temperatura = TablaTemperatura()
        table_layout.addWidget(self.mi_tabla_temperatura)

        # Layout para el calendario
        calendar_layout = QVBoxLayout()
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.calendario_widget = CalendarioPersonalizado(self.mi_tabla_temperatura)
        self.calendario_widget.setFixedSize(300, 300)  # igual que el placeholder

        calendar_layout.addWidget(self.calendario_widget)

        # Ahora agrega los layouts en vez de los widgets directos
        content_layout.addLayout(table_layout)
        content_layout.addLayout(calendar_layout)

        # Agregar navbar e inferior al contenedor derecho
        right_container.addLayout(navbar)
        right_container.addLayout(content_layout)

        # Agregar sidebar y contenedor derecho al layout principal
        main_layout.addLayout(right_container)

    def cambiar_sensor(self, nuevo_sensor):
        self.mi_tabla_temperatura.sensor_actual = nuevo_sensor
        self.mi_tabla_temperatura.title_label.setText(nuevo_sensor)  # actualizar el header
        self.mi_tabla_temperatura.tabla.horizontalHeaderItem(0).setText(nuevo_sensor)

        # OBTENER LA FECHA ACTUAL DEL CALENDARIO
        fecha_seleccionada = self.calendario_widget.calendario.selectedDate()
        
        # Y PASARLA AL LLAMAR obtener_datos_sensor
        self.mi_tabla_temperatura.obtener_datos_sensor(fecha_seleccionada)


