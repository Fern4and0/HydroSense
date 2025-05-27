from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import Qt

from views.historyView.classTabla import TablaTemperatura
from views.historyView.classCalendario import CalendarioPersonalizado


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

        sensor_group = QButtonGroup(self)
        sensor_group.setExclusive(True)

        sensor_group.addButton(btn_temp)
        sensor_group.addButton(btn_CE)
        sensor_group.addButton(btn_PH)
        sensor_group.addButton(btn_NA)

        btn_temp.clicked.connect(lambda: self.cambiar_sensor("Temperatura"))
        btn_CE.clicked.connect(lambda: self.cambiar_sensor("Conductividad Electrica"))
        btn_PH.clicked.connect(lambda: self.cambiar_sensor("Nivel de pH"))
        btn_NA.clicked.connect(lambda: self.cambiar_sensor("Nivel del agua"))

        btn_temp.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_CE.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_PH.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_NA.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        navbar.addWidget(btn_temp)
        navbar.addWidget(btn_CE)
        navbar.addWidget(btn_PH)
        navbar.addWidget(btn_NA)
        
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
        self.mi_tabla_temperatura.setMinimumSize(840, 700)
        self.mi_tabla_temperatura.setMaximumSize(900, 700) 
        self.mi_tabla_temperatura.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        table_layout.addWidget(self.mi_tabla_temperatura)

        # Layout para el calendario
        calendar_layout = QVBoxLayout()
        calendar_layout.setContentsMargins(0, 0, 10, 0)
        calendar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.calendario_widget = CalendarioPersonalizado(self.mi_tabla_temperatura)
        self.calendario_widget.setMinimumSize(300, 300)  # igual que el placeholder
        self.calendario_widget.setMaximumSize(500, 500)  # igual que el placeholder
        self.calendario_widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

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

    
