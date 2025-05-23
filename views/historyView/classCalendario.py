from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget
)
from PyQt6.QtCore import QLocale, QSize
from PyQt6.QtGui import QIcon


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