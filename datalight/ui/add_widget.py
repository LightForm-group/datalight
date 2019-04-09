"""Methods to prepare widgets for addition to a UI form"""

import datetime
from PyQt5 import QtWidgets

from datalight.ui import form_generator


def add_ui_element(parent, element_description, location):
    """ Add a non-GroupBox widget to the form.
    :param parent: (GroupBox or UIWindow) Where the widget will be stored.
    :param element_description: (dict) A description of the element to add.
    :param location: (QWidget) The instance of the parent widget of the new widget.
    """

    # Add a new widget and then add it to the layout form
    parent.widgets.append(add_new_widget(element_description, location))
    if isinstance(parent.widgets[-1], QtWidgets.QGroupBox):
        parent.form_layout.addRow(parent.widgets[-1])
    else:
        # Add a label for the new widget and position it next to the new widget
        parent.widgets.append(add_role_label(element_description, location))
        parent.form_layout.addRow(parent.widgets[-1], parent.widgets[-2])

    # Process widget dependencies
    if "activates_on" in element_description:
        parent.widgets[-2].currentTextChanged.connect(
            lambda: parent.enable_dependent_widget(element_description["activates_on"]))


def add_new_widget(element_description, parent_widget):
    widget_type = element_description["widget"]

    if widget_type == "QComboBox":
        new_widget = _add_combo_box(element_description, parent_widget)
    elif widget_type == "QPlainTextEdit":
        new_widget = _add_plain_text_edit(element_description, parent_widget)
    elif widget_type == "QDateEdit":
        new_widget = _add_date_edit(element_description, parent_widget)
    elif widget_type == "QGroupBox":
        new_widget = form_generator.GroupBox(element_description, parent_widget)
    else:
        raise TypeError("No method to add element {}.".format(widget_type))

    # Set widget properties common to all widgets
    if "tooltip" in element_description:
        new_widget.setToolTip = element_description["tooltip"]

    return new_widget


def _add_combo_box(element_description, parent_widget):
    new_widget = QtWidgets.QComboBox(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName(name)

    if "editable" in element_description:
        new_widget.setEditable(element_description["editable"])

    if "values" in element_description:
        for item in element_description["values"]:
            new_widget.addItem(item)

    return new_widget


def _add_plain_text_edit(element_description, parent_widget):
    new_widget = QtWidgets.QPlainTextEdit(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName(name)
    return new_widget


def _add_date_edit(element_description, parent_widget):
    new_widget = QtWidgets.QDateEdit(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName(name)
    new_widget.setCalendarPopup(True)
    new_widget.setDate(datetime.date.today())
    return new_widget


def add_role_label(element_description, parent_widget):
    name = element_description["_name"]
    fancy_name = element_description["fancy_name"]
    new_label = QtWidgets.QLabel(parent_widget)
    new_label.setText(fancy_name)
    new_label.setObjectName("label_{}".format(name))
    return new_label
