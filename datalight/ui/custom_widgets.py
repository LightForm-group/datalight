import datetime

import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtGui


class QComboBox(QtWidgets.QComboBox):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)

        if "editable" in widget_description:
            self.setEditable(widget_description["editable"])

        if "values" in widget_description:
            for item in widget_description["values"]:
                self.addItem(item)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)


class QPlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)


class QDateEdit(QtWidgets.QDateEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        self.setCalendarPopup(True)
        self.setDate(datetime.date.today())


class QPushButton(QtWidgets.QPushButton):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "button_text" not in widget_description:
            raise KeyError("PushButton {} must have a 'button_text' property.".format(name))
        self.setText(widget_description["button_text"])


class QListWidget(QtWidgets.QListWidget):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)


class QLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)


class QLabel(QtWidgets.QLabel):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        self.setText(widget_description["text"])
