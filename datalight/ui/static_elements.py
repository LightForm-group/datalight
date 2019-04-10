"""Non dynamic widgets inserted into every form."""

import re

from PyQt5 import QtWidgets, QtGui, QtCore
from datalight.ui import button_methods


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


def add_ok_button(ui):
    """ Put in an OK button and attach its click method."""
    ui.ok_button = QtWidgets.QPushButton(ui.central_widget)
    ui.ok_button.setObjectName("pushButton_2")
    ui.ok_button.setText("OK")
    ui.ok_button.clicked.connect(button_methods.do_ok_button(main_window=ui))
    ui.form_layout.addWidget(QtWidgets.QFormLayout.FieldRole, ui.ok_button)


def set_up_file_upload(ui):
    """Set up the static widgets for the file upload section at the top of the form."""
    ui.group_boxes["upload"] = QtWidgets.QGroupBox(ui.central_widget)
    ui.group_boxes["upload"].setTitle("Upload Files")

    ui.file_upload["list"] = QtWidgets.QListWidget(ui.group_boxes["upload"])
    ui.file_upload["list_model"] = QtGui.QStandardItemModel(ui.file_upload["list"])

    ui.file_upload["file_button"] = QtWidgets.QPushButton(ui.group_boxes["upload"])
    ui.file_upload["file_button"].setText("Select file to upload")
    ui.file_upload["file_button"].clicked.connect(
        lambda: file_select_dialogue(ui, directory=False))

    ui.file_upload["folder_button"] = QtWidgets.QPushButton(ui.group_boxes["upload"])
    ui.file_upload["folder_button"].setText("Select folder to upload")
    ui.file_upload["folder_button"].clicked.connect(
        lambda: file_select_dialogue(ui, directory=True))

    ui.file_upload["clear_button"] = QtWidgets.QPushButton(ui.group_boxes["upload"])
    ui.file_upload["clear_button"].setText("Remove selected files")
    ui.file_upload["clear_button"].clicked.connect(
        ui.remove_selected_items)

    ui.layouts["upload_grid"] = QtWidgets.QGridLayout(ui.group_boxes["upload"])

    # Position in grid given by: y-pos, x-pos, y-width, x-width.
    ui.layouts["upload_grid"].addWidget(ui.file_upload["list"], 0, 0, 1, 3)
    ui.layouts["upload_grid"].addWidget(ui.file_upload["file_button"], 1, 0, 1, 1)
    ui.layouts["upload_grid"].addWidget(ui.file_upload["folder_button"], 1, 1, 1, 1)
    ui.layouts["upload_grid"].addWidget(ui.file_upload["clear_button"], 1, 2, 1, 1)

    ui.layouts["vertical_layout"].addWidget(ui.group_boxes["upload"])
