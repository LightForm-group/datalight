"""Methods to prepare widgets for addition to a UI form"""

import datetime
from PyQt5 import QtWidgets

from datalight.ui import form_generator, button_methods


def add_ui_element(storage_location, element_description, parent):
    """ Add a non-GroupBox widget to the form.
    :param storage_location: (GroupBox or UIWindow) Where the widget instance will be stored.
    :param element_description: (dict) A description of the element to add.
    :param parent: (QWidget) The instance of the parent widget of the new widget.
    """

    # If it is a group box then add a GroupBox to the parent
    if element_description["widget"] == "QGroupBox":
        name = element_description["_name"]
        storage_location.containers[name] = form_generator.Container(element_description, parent)
        if isinstance(storage_location.layout, QtWidgets.QFormLayout):
            storage_location.layout.addRow(storage_location.containers[name].group_box)
        else:
            storage_location.layout.addWidget(storage_location.group_box)
    elif "label" in element_description:
        # Add a widget and label and add them to a layout
        storage_location.widgets.append(add_new_widget(element_description, parent))
        storage_location.widgets.append(add_role_label(element_description, parent))
        storage_location.layout.addRow(storage_location.widgets[-1], storage_location.widgets[-2])
    else:
        storage_location.widgets.append(add_new_widget(element_description, parent))
        storage_location.layout.addWidget(storage_location.widgets[-1])

    # Process widget dependencies
    if "activates_on" in element_description:
        storage_location.widgets[-2].currentTextChanged.connect(
            lambda: storage_location.enable_dependent_widget(element_description["activates_on"]))


def add_new_widget(element_description, parent_widget, main_window=None):
    """Add a non-Group box widget."""
    widget_type = element_description["widget"]

    if widget_type == "QComboBox":
        new_widget = _add_combo_box(element_description, parent_widget)
    elif widget_type == "QPlainTextEdit":
        new_widget = _add_plain_text_edit(element_description, parent_widget)
    elif widget_type == "QDateEdit":
        new_widget = _add_date_edit(element_description, parent_widget)
    elif widget_type == "QPushButton":
        new_widget = _add_push_button(element_description, parent_widget)
    else:
        raise TypeError("No method to add element {}.".format(widget_type))

    # Set widget properties common to all widgets
    if "tooltip" in element_description:
        new_widget.setToolTip = element_description["tooltip"]

    return new_widget


def _add_combo_box(element_description, parent_widget):
    new_combo_box = QtWidgets.QComboBox(parent_widget)
    name = element_description["_name"]
    new_combo_box.setObjectName(name)

    if "editable" in element_description:
        new_combo_box.setEditable(element_description["editable"])

    if "values" in element_description:
        for item in element_description["values"]:
            new_combo_box.addItem(item)

    return new_combo_box


def _add_plain_text_edit(element_description, parent_widget):
    new_plain_text = QtWidgets.QPlainTextEdit(parent_widget)
    name = element_description["_name"]
    new_plain_text.setObjectName(name)
    return new_plain_text


def _add_date_edit(element_description, parent_widget):
    new_date_edit = QtWidgets.QDateEdit(parent_widget)
    name = element_description["_name"]
    new_date_edit.setObjectName(name)
    new_date_edit.setCalendarPopup(True)
    new_date_edit.setDate(datetime.date.today())
    return new_date_edit


def add_role_label(element_description, parent_widget):
    new_label = QtWidgets.QLabel(parent_widget)
    name = element_description["_name"]
    label = element_description["label"]
    new_label.setText(label)
    new_label.setObjectName("label_{}".format(name))
    return new_label


def _add_push_button(element_description, parent_widget):
    new_button = QtWidgets.QPushButton(parent_widget)
    name = element_description["_name"]
    new_button.setObjectName(name)
    if "button_text" not in element_description:
        raise KeyError("PushButton {} must have a 'button_text' property.".format(name))
    new_button.setText(element_description["button_text"])
    return new_button
