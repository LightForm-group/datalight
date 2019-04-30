"""Methods to prepare widgets for addition to a UI form"""

import datetime
from PyQt5 import QtWidgets

from datalight.ui.form_generator import Container


def add_ui_element(parent_container: Container, element_description: dict, parent):
    """ Add a non-GroupBox widget to the form.
    :param parent_container: (Container) Where the widget instance will be stored.
    :param element_description: (dict) A description of the element to add.
    :param parent: (QWidget) The instance of the parent widget of the new widget.
    """

    # If it is a group box then add a new Container to the parent
    if element_description["widget"] == "QGroupBox":
        name = element_description["_name"]
        new_container = Container(element_description, parent)
        parent_container.add_container(name, new_container)
        parent_container.add_widget_to_layout(parent_container._containers[name].group_box)

    elif "label" in element_description:
        # Add a widget and label and add them to a layout
        parent_container.add_widget(get_new_widget(element_description, parent))
        parent_container.add_widget(new_role_label(element_description, parent))
        parent_container.add_widget_to_layout(parent_container._widgets[-2], parent_container._widgets[-1])
    else:
        parent_container.add_widget(get_new_widget(element_description, parent))
        parent_container.add_widget_to_layout(parent_container._widgets[-1])

    # Process widget dependencies
    #if "activates_on" in element_description:
    #    parent_container.widgets[-2].currentTextChanged.connect(
    #        lambda: parent_container.enable_dependent_widget(element_description["activates_on"]))


def get_new_widget(element_description, parent_widget, main_window=None):
    """Add a non-Group box widget."""
    widget_type = element_description["widget"]

    if widget_type == "QComboBox":
        new_widget = _new_combo_box(element_description, parent_widget)
    elif widget_type == "QPlainTextEdit":
        new_widget = _new_plain_text_edit(element_description, parent_widget)
    elif widget_type == "QDateEdit":
        new_widget = _new_date_edit(element_description, parent_widget)
    elif widget_type == "QPushButton":
        new_widget = _new_push_button(element_description, parent_widget)
    elif widget_type == "QListWidget":
        new_widget = _new_list_widget(element_description, parent_widget)
    else:
        raise TypeError("No method to add element {}.".format(widget_type))

    # Set widget properties common to all widgets
    if "tooltip" in element_description:
        new_widget.setToolTip = element_description["tooltip"]

    return new_widget


def _new_combo_box(element_description, parent_widget):
    new_combo_box = QtWidgets.QComboBox(parent_widget)
    name = element_description["_name"]
    new_combo_box.setObjectName(name)

    if "editable" in element_description:
        new_combo_box.setEditable(element_description["editable"])

    if "values" in element_description:
        for item in element_description["values"]:
            new_combo_box.addItem(item)

    return new_combo_box


def _new_plain_text_edit(element_description, parent_widget):
    new_plain_text = QtWidgets.QPlainTextEdit(parent_widget)
    name = element_description["_name"]
    new_plain_text.setObjectName(name)
    return new_plain_text


def _new_date_edit(element_description, parent_widget):
    new_date_edit = QtWidgets.QDateEdit(parent_widget)
    name = element_description["_name"]
    new_date_edit.setObjectName(name)
    new_date_edit.setCalendarPopup(True)
    new_date_edit.setDate(datetime.date.today())
    return new_date_edit


def _new_push_button(element_description, parent_widget):
    new_button = QtWidgets.QPushButton(parent_widget)
    name = element_description["_name"]
    new_button.setObjectName(name)
    if "button_text" not in element_description:
        raise KeyError("PushButton {} must have a 'button_text' property.".format(name))
    new_button.setText(element_description["button_text"])
    return new_button


def _new_list_widget(element_description, parent_widget):
    new_list_widget = QtWidgets.QListWidget(parent_widget)
    name = element_description["_name"]
    new_list_widget.setObjectName(name)
    return new_list_widget


def new_role_label(element_description, parent_widget):
    new_label = QtWidgets.QLabel(parent_widget)
    name = element_description["_name"]
    label = element_description["label"]
    new_label.setText(label)
    new_label.setObjectName("label_{}".format(name))
    return new_label
