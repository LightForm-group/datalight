"""
This script contains functions which are linked to buttons in the UI.
In order to be linked to a button, a function must have the same name as the button as specified
in the UI YAML specification.
"""
import pathlib
import re
from functools import partial
from typing import TYPE_CHECKING, List, Union

from PyQt5 import QtWidgets, QtCore, QtGui

import datalight.common
from datalight.ui import custom_widgets
import datalight.ui.validation
from datalight.zenodo import upload_record
from datalight.ui.custom_widgets import Widget, get_new_widget, Table

if TYPE_CHECKING:
    from datalight.ui.main_form import DatalightUIWindow


def remove_item_button(datalight_ui: "DatalightUIWindow"):
    """Remove the selected item(s) from the file/folder upload list."""
    list_widget = datalight_ui.get_widget_by_name("file_list")
    files = list_widget.selectedItems()
    for item in files:
        row_index = list_widget.row(item)
        list_widget.takeItem(row_index)


def select_file_button(datalight_ui: "DatalightUIWindow"):
    """Prepare to open a dialog box to select a file to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    open_file_window(datalight_ui, file_dialogue)


def select_folder_button(datalight_ui: "DatalightUIWindow"):
    """Prepare to open a dialog box to select a folder` to upload."""
    file_dialogue = QtWidgets.QFileDialog()
    file_dialogue.setFileMode(QtWidgets.QFileDialog.Directory)
    open_file_window(datalight_ui, file_dialogue)


def open_file_window(datalight_ui: "DatalightUIWindow", file_dialogue):
    """Open a dialogue box to select a file or folder."""
    list_widget = datalight_ui.get_widget_by_name("file_list")
    if file_dialogue.exec():
        for path in file_dialogue.selectedFiles():
            if not list_widget.findItems(path, QtCore.Qt.MatchExactly):
                list_widget.addItem(path)
            else:
                file_name = re.split(r"[\\/]", path)[-1]
                QtWidgets.QMessageBox.warning(datalight_ui.central_widget, "Warning",
                                              f"File {file_name}, already selected.")


def ok_button(datalight_ui: "DatalightUIWindow"):
    """
    The on click method for the OK button. Take all data from the form and package
    it up into a dictionary.
    """
    repository_metadata = validate_widgets(datalight_ui, "zenodo_core_metadata")
    experiment_metadata = validate_widgets(datalight_ui, "experimental_metadata")
    if repository_metadata and experiment_metadata:
        publish = repository_metadata["publish"]
        if publish:
            publish_result = show_publish_warning()
            if publish_result == QtWidgets.QMessageBox.YesRole:
                publish = True
            elif publish_result == QtWidgets.QMessageBox.NoRole:
                publish = False
            else:
                # If the user presses cancel then abort the upload and return to the form.
                return True

        upload_status = upload_record(experiment_metadata.pop("file_list"),
                                      repository_metadata, experiment_metadata,
                                      datalight_ui.config_path,
                                      publish,
                                      repository_metadata.pop("sandbox"))
        if upload_status.code == 200:
            custom_widgets.message_box("Datalight upload successful.",
                                       QtWidgets.QMessageBox.Information)
        else:
            custom_widgets.message_box(f"Error in upload.\n"
                                       f"Error type: '{upload_status.message}'\n"
                                       f"Affected field: '{upload_status.error_field}'\n"
                                       f"Error details: '{upload_status.error_message}'\n",
                                       QtWidgets.QMessageBox.Warning)


def show_publish_warning() -> QtWidgets.QMessageBox.ButtonRole:
    """Open a dialog asking the user whether they want to publish their record. Return True if the
    user wants to publish and False to abort the upload."""

    warning_widget = QtWidgets.QMessageBox()
    warning_widget.setIcon(QtWidgets.QMessageBox.Warning)
    warning_widget.setText("You have selected to publish the record.\n\n"
                           "If you select Upload and Publish, the record will be immediately "
                           "published after upload.\n\n"
                           "If you select Upload Only the record will be uploaded but not "
                           "published.")
    warning_widget.addButton("Upload and Publish", QtWidgets.QMessageBox.YesRole)
    warning_widget.addButton("Upload Only", QtWidgets.QMessageBox.NoRole)
    cancel_button = warning_widget.addButton("Cancel Upload", QtWidgets.QMessageBox.RejectRole)
    warning_widget.setEscapeButton(cancel_button)
    warning_widget.setWindowTitle("Publishing Warning")
    warning_widget.exec()
    clicked_button = warning_widget.clickedButton()
    return warning_widget.buttonRole(clicked_button)


def add_row_button(datalight_ui: "DatalightUIWindow"):
    """Add a new row to the author table."""
    table_widget: Table = datalight_ui.get_widget_by_name("author_details")
    table_widget.insertRow(table_widget.rowCount())


def delete_row_button(datalight_ui: "DatalightUIWindow"):
    """Add a new row to the author table."""
    table_widget: Table = datalight_ui.get_widget_by_name("author_details")
    selected_rows = sorted({row.row() for row in table_widget.selectedIndexes()}, reverse=True)
    for row_index in selected_rows:
        table_widget.removeRow(row_index)


def validate_widgets(datalight_ui: "DatalightUIWindow", root_widget_name: str) -> Union[None, dict]:
    """Check if the child Widgets of `root_widget_name are valid. If all widgets are valid, return
    their values, else return None."""
    child_widgets = get_child_widgets(datalight_ui, root_widget_name)

    valid_length = datalight.ui.validation.validate_output_length(child_widgets)
    short_widgets = [key for key, value in list(valid_length.items()) if not value]

    valid_output = datalight.ui.validation.validate_widget_contents(child_widgets)
    incomplete_widgets = [key for key, value in list(valid_output.items()) if not value]

    if incomplete_widgets:
        datalight.ui.validation.process_incomplete_widgets(incomplete_widgets)
    elif short_widgets:
        datalight.ui.validation.process_short_widgets(short_widgets)
    else:
        return datalight.ui.validation.get_widget_values(child_widgets)

    return None


def get_child_widgets(datalight_ui: "DatalightUIWindow", root_widget_name: str) -> List[Widget]:
    """Return the child widgets of the widget with name `root_widget_name`"""
    root_widget = datalight_ui.get_widget_by_name(root_widget_name)
    return root_widget.findChildren(QtWidgets.QWidget)


def about_menu_action(ui_path: pathlib.Path):
    """Open a dialog with information about Datalight. This method is called from the about menu."""
    about_widget = QtWidgets.QMessageBox()
    icon_path = str(ui_path.joinpath("images/icon.png"))
    datalight_icon = QtGui.QPixmap(icon_path).scaledToHeight(150, QtCore.Qt.SmoothTransformation)
    about_widget.setIconPixmap(datalight_icon)
    about_widget.setTextFormat(QtCore.Qt.RichText)
    about_widget.setText("<a href='https://github.com/LightForm-group/datalight'>"
                         "Click here to find out more about DataLight</a><br><br>"
                         "<a href='https://datalight.readthedocs.io'>Click here "
                         "for documentation.</a><br><br>"
                         "<a href='https://github.com/merrygoat'>Peter Crowther</a> 2019-2020.")
    about_widget.setWindowTitle("About Datalight")
    about_widget.exec()


def add_author_button(datalight_ui: "DatalightUIWindow"):
    """Open a dialog to add authors to the main form from the list of store authors."""
    author_window = QtWidgets.QDialog()
    author_window.setWindowTitle("Add author from stored authors")

    # Set up the dialog widgets
    author_widget_path = datalight_ui.ui_path.joinpath("ui_descriptions/add_authors.yaml")
    author_ui = datalight.common.read_yaml(author_widget_path)
    base_description = {"widget": "GroupBox",
                        "layout": "HBoxLayout",
                        "_name": "BaseGroupBox",
                        "children": author_ui}
    group_box = get_new_widget(author_window, base_description)[0]

    # Set up dialog layout and add it to the generated dialog
    layout = QtWidgets.QHBoxLayout(author_window)
    layout.addWidget(group_box)
    layout.setContentsMargins(0, 0, 0, 0)
    author_window.setLayout(layout)

    # Get the list of authors and add them to the combobox
    author_path = datalight_ui.ui_path.joinpath("ui_descriptions/author_details.yaml")
    authors = datalight.common.read_yaml(author_path)

    list_widget = author_window.findChildren(QtWidgets.QWidget, "author_list")[0]
    for author_name in authors:
        list_widget.addItem(author_name)

    # Add an action to the add author button
    add_selected_button = author_window.findChildren(QtWidgets.QWidget, "select_author_button")[0]
    add_selected_button.clicked.connect(partial(add_selected_author_button, datalight_ui,
                                                author_window))

    author_window.show()


def add_selected_author_button(datalight_ui: "DatalightUIWindow", author_window: QtWidgets.QDialog):
    """Method for the add selected combo button in the add authors dialog."""
    author_list_widget = author_window.findChildren(QtWidgets.QWidget, "author_list")[0]
    selected_authors = [item.text() for item in author_list_widget.selectedItems()]

    for author in selected_authors:
        datalight_ui.add_author(author)

    author_window.close()
