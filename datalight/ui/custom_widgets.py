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

        if "active_when" in widget_description:
            self.active_when = widget_description["active_when"]
        else:
            self.active_when = None

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)

        # Process widget dependencies
        # if self.active_when:
        #     source_widget = list(self.active_when.keys())[0]
        #     print(source_widget)

    def get_value(self):
        return self.currentText()


class QPlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)

    def get_value(self):
        return self.toPlainText()


class QDateEdit(QtWidgets.QDateEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        self.setCalendarPopup(True)
        self.setDate(datetime.date.today())

    def get_value(self):
        return self.date()


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

    def get_value(self):
        return self.currentItem()


class QLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)

    def get_value(self):
        self.text()


class QLabel(QtWidgets.QLabel):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        self.setText(widget_description["text"])
