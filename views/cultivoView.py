from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QButtonGroup, QLabel, QFrame, QToolButton, QAbstractButton, QMessageBox
)
from configCultivo import guardar_cultivo_seleccionado
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QPixmap

class CultivoView(QWidget):
    def __init__(self):
        super().__init__()

        # Diccionario con datos de cada cultivo
        self.cultivos_data = {
            "Lechuga Orejona": {
                "descripcion": "La lechuga orejona es una hortaliza de hojas verdes y crujientes, ideal para ensaladas. "
                               "Crece rápido, requiere pocos nutrientes y se adapta muy bien al cultivo en agua. "
                               "Prefiere ambientes ventilados y no necesita luz intensa.",
                "param_izq": "• pH: 5.5 – 6.5\n• Temperatura del agua: 18°C – 22°C\n• Conductividad eléctrica (CE): 0.8 – 1.2 mS/cm",
                "param_der": "• Tiempo estimado de cosecha: 30 a 40 días\n• ¿Requiere poda?: No",
                "icon_normal": "assets/icons/seedling-solid-off.svg",
                "icon_selected": "assets/icons/seedling-solid.svg"
            },
            "Espinaca": {
                "descripcion": "La espinaca es una planta de hoja verde rica en hierro y vitaminas. "
                               "Requiere temperaturas frescas y un riego constante. Ideal para cultivo hidropónico en climas templados.",
                "param_izq": "• pH: 6.0 – 7.0\n• Temperatura del agua: 16°C – 20°C\n• CE: 1.8 – 2.3 mS/cm",
                "param_der": "• Cosecha: 40 a 50 días\n• ¿Requiere poda?: No",
                "icon_normal": "assets/icons/seedling-solid-off.svg",
                "icon_selected": "assets/icons/seedling-solid.svg"
            },
            "Cilantro": {
                "descripcion": "El cilantro es una hierba aromática de rápido crecimiento. Necesita buena ventilación "
                               "y prefiere climas templados a cálidos. Su cultivo en agua requiere un buen manejo de nutrientes.",
                "param_izq": "• pH: 6.2 – 6.8\n• Temperatura del agua: 20°C – 25°C\n• CE: 1.2 – 1.8 mS/cm",
                "param_der": "• Cosecha: 20 a 30 días\n• ¿Requiere poda?: Sí",
                "icon_normal": "assets/icons/seedling-solid-off.svg",
                "icon_selected": "assets/icons/seedling-solid.svg"
            },
            "Albahaca": {
                "descripcion": "La albahaca es una planta aromática que necesita calor, luz solar directa y buena humedad. "
                               "Ideal para cultivos hidropónicos en ambientes cálidos y bien iluminados.",
                "param_izq": "• pH: 5.5 – 6.5\n• Temperatura del agua: 20°C – 27°C\n• CE: 1.0 – 1.6 mS/cm",
                "param_der": "• Cosecha: 25 a 35 días\n• ¿Requiere poda?: Sí",
                "icon_normal": "assets/icons/seedling-solid-off.svg",
                "icon_selected": "assets/icons/seedling-solid.svg"
            }
        }

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 25, 20, 25)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título principal
        titulo = QLabel("Selecciona tu cultivo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #55E8BE; font-size: 42px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(titulo)

        # Botones de selección de cultivo
        cultivos_layout = QHBoxLayout()
        self.boton_group = QButtonGroup(self)
        self.boton_group.setExclusive(True)

        self.botones_cultivo = {}
        for cultivo_nombre, datos in self.cultivos_data.items():
            btn = QToolButton()
            btn.setText(cultivo_nombre)
            btn.setCheckable(True)
            btn.setIcon(QIcon(datos["icon_normal"]))
            btn.setIconSize(QSize(50, 50))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    color: #444444;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    margin-bottom: 10px;
                }
                QToolButton:checked {
                    color: #55E8BE;
                }
            """)
            self.boton_group.addButton(btn)
            cultivos_layout.addWidget(btn)
            self.botones_cultivo[btn] = cultivo_nombre
            self.boton_group.buttonClicked[QAbstractButton].connect(self.actualizar_info)
        main_layout.addLayout(cultivos_layout)

        # Contenedor gris para información
        self.contenedor_info = QFrame()
        self.contenedor_info.setStyleSheet("background-color: #222222; border-radius: 10px;")
        self.contenedor_info.setMinimumHeight(410)

        info_layout = QVBoxLayout(self.contenedor_info)
        info_layout.setContentsMargins(40, 20, 20, 40)
        info_layout.setSpacing(15)

        # Widgets para contenido dinámico
        self.titulo_planta = QLabel()
        self.titulo_planta.setStyleSheet("color: #d8f3dc; font-size: 34px; font-weight: bold;")

        self.descripcion = QLabel()
        self.descripcion.setStyleSheet("color: white; font-size: 20px;")
        self.descripcion.setWordWrap(True)

        self.parametros_layout = QHBoxLayout()
        self.param_izq = QLabel()
        self.param_izq.setStyleSheet("color: white; font-size: 20px;")
        self.param_der = QLabel()
        self.param_der.setStyleSheet("color: white; font-size: 20px;")
        self.parametros_layout.addWidget(self.param_izq)
        self.parametros_layout.addWidget(self.param_der)

        self.btn_usar = QPushButton("Usar este cultivo")
        self.btn_usar.clicked.connect(self.usar_cultivo)
        self.btn_usar.setStyleSheet("""
            QPushButton {
                background-color: #55E8BE;
                color: black;
                font-size: 26px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
                width: 960px;
                margin: 20px 40px 0px 40px;
            }
            QPushButton:hover {
                background-color: #4bcca7;
            }
        """)
        self.btn_usar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Agregar widgets al layout de información
        info_layout.addWidget(self.titulo_planta)
        info_layout.addWidget(self.descripcion)
        info_layout.addLayout(self.parametros_layout)
        info_layout.addWidget(self.btn_usar)

        main_layout.addWidget(self.contenedor_info)

        # Texto informativo final
        texto_final = QLabel("Elige qué planta vas a cultivar. Al seleccionarla, el sistema ajustará automáticamente\nlos parámetros ideales para su crecimiento.")
        texto_final.setStyleSheet("color: #848E91; font-size: 18px;")
        texto_final.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(texto_final)

        # Conectar botones a la función que actualiza la información
        self.boton_group.buttonClicked.connect(self.actualizar_info)

        # Seleccionar cultivo inicial por defecto
        self.boton_group.buttons()[0].setChecked(True)
        self.actualizar_info(self.boton_group.buttons()[0])

    def actualizar_info(self, boton):
        nombre = boton.text()
        datos = self.cultivos_data[nombre]

        for btn, cultivo_nombre in self.botones_cultivo.items():
            icon_path = self.cultivos_data[cultivo_nombre]["icon_selected" if btn is boton else "icon_normal"]
            btn.setIcon(QIcon(icon_path))

        self.titulo_planta.setText(nombre)
        self.descripcion.setText(datos["descripcion"])
        self.param_izq.setText(datos["param_izq"])
        self.param_der.setText(datos["param_der"])

    def mostrar_alerta(self, mensaje, icono_path="assets/icons/circle-check-solid.svg"):
        if hasattr(self, 'alerta') and self.alerta:
            self.alerta.deleteLater()

        # Contenedor de la alerta (QWidget en lugar de QLabel para mayor personalización)
        self.alerta = QWidget(self)
        self.alerta.setStyleSheet("""
            background-color: #222222;
            border-radius: 8px;
        """)
        self.alerta.setFixedHeight(50)

        # Layout horizontal (icono + texto)
        layout = QHBoxLayout(self.alerta)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # Icono
        icono = QLabel()
        icono.setPixmap(QPixmap(icono_path).scaled(24, 24))
        layout.addWidget(icono)

        # Texto
        texto = QLabel(mensaje)
        texto.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold;")
        layout.addWidget(texto)

        # Tamaño final
        self.alerta.adjustSize()
        ancho_alerta = self.alerta.width()
        alto_alerta = self.alerta.height()

        # Posición de inicio (fuera de pantalla)
        x_final = self.width() - ancho_alerta - 20
        y_final = 20
        x_inicio = self.width()

        self.alerta.setGeometry(QRect(x_inicio, y_final, ancho_alerta, alto_alerta))
        self.alerta.show()

        # Animación de entrada
        anim = QPropertyAnimation(self.alerta, b"geometry")
        anim.setDuration(500)
        anim.setStartValue(QRect(x_inicio, y_final, ancho_alerta, alto_alerta))
        anim.setEndValue(QRect(x_final, y_final, ancho_alerta, alto_alerta))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        # Ocultar después de 3 segundos
        QTimer.singleShot(3000, self.alerta.hide)

        # Evita que el objeto de animación se elimine
        self.alerta.animacion = anim


    def usar_cultivo(self):
        boton_seleccionado = self.boton_group.checkedButton()
        if boton_seleccionado:
            nombre_visible = boton_seleccionado.text()

            # Mapea a clave interna
            clave_map = {
                "Lechuga Orejona": "Lechuga_orejona",
                "Espinaca": "Espinaca",
                "Cilantro": "Cilantro",
                "Albahaca": "Albahaca"
            }
            clave_interna = clave_map.get(nombre_visible)
            if not clave_interna:
                self.mostrar_alerta("No se pudo identificar la clave del cultivo.")
                return

            guardar_cultivo_seleccionado(nombre_visible, clave_interna)
            self.mostrar_alerta(f"Cultivo seleccionado: {nombre_visible}")
        else:
            self.mostrar_alerta("Selecciona un cultivo antes de continuar.")

