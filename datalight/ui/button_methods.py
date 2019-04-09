from PyQt5 import QtWidgets

from datalight.ui import form_generator


def do_ok_button(main_window):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    output = {}
    for widget in main_window.widgets:
        if not isinstance(widget, QtWidgets.QLabel):
            name = widget.objectName()
            if isinstance(widget, QtWidgets.QComboBox):
                output[name] = widget.currentText()
            elif isinstance(widget, QtWidgets.QPlainTextEdit):
                output[name] = widget.toPlainText()
            elif isinstance(widget, QtWidgets.QDateEdit):
                output[name] = widget.date()
            elif isinstance(widget, QtWidgets.QGroupBox):
                pass
            else:
                raise form_generator.GuiError("Unknown widget type when summarising data.")
    print(output)
