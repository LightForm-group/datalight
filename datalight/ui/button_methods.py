import re

from PyQt5 import QtWidgets, QtCore

from datalight.ui import form_generator


def remove_selected_items(self):
    files = self.file_upload["list"].selectedItems()
    for item in files:
        row_index = self.file_upload["list"].row(item)
        self.file_upload["list"].takeItem(row_index)


def file_select_dialogue(ui, directory):
    """Set up file dialogue widget."""
    file_dialogue = QtWidgets.QFileDialog(ui.group_boxes["upload"])
    if directory:
        file_dialogue.setFileMode(QtWidgets.QFileDialog.Directory)
    else:
        file_dialogue.setFileMode(QtWidgets.QFileDialog.ExistingFiles)

    if file_dialogue.exec():
        for path in file_dialogue.selectedFiles():
            if not ui.file_upload["list"].findItems(path, QtCore.Qt.MatchExactly):
                ui.file_upload["list"].addItem(path)
            else:
                QtWidgets.QMessageBox.warning(ui.central_widget, "Warning",
                                              "File {}, already selected.".format(
                                                  re.split("[\\\/]", path)[-1]))


def ok_button(main_window):
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
            elif isinstance(widget, QtWidgets.QPushButton):
                pass
            else:
                raise form_generator.GuiError("Unknown widget type when summarising data.")
    print(output)
