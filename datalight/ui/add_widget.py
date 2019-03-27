import datetime
from PyQt5 import QtWidgets


def add_new_widget(element_description, parent_widget):
    widget_type = element_description["widget"]

    if widget_type == "QComboBox":
        new_widget = _add_combo_box(element_description, parent_widget)
    elif widget_type == "QPlainTextEdit":
        new_widget = _add_plain_text_edit(element_description, parent_widget)
    elif widget_type == "QDateEdit":
        new_widget = _add_date_edit(element_description, parent_widget)
    else:
        raise TypeError("No method to add element {}.".format(widget_type))

    # Set widget properties common to all widgets
    if "tooltip" in element_description:
        new_widget.setToolTip = element_description["tooltip"]
    if "active_when" in element_description:
        new_widget.setEnabled(False)

    return new_widget


def _add_combo_box(element_description, parent_widget):
    new_widget = QtWidgets.QComboBox(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName("combo_{}".format(name))

    if "editable" in element_description:
        new_widget.setEditable(element_description["editable"])

    if "values" in element_description:
        for item in element_description["values"]:
            new_widget.addItem(item)

    return new_widget


def _add_plain_text_edit(element_description, parent_widget):
    new_widget = QtWidgets.QPlainTextEdit(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName("plain_text_{}".format(name))
    return new_widget


def _add_date_edit(element_description, parent_widget):
    new_widget = QtWidgets.QDateEdit(parent_widget)
    name = element_description["_name"]
    new_widget.setObjectName("date_edit{}".format(name))
    new_widget.setCalendarPopup(True)
    new_widget.setDate(datetime.date.today())
    return new_widget


def add_role_label(name, parent_widget):
    new_label = QtWidgets.QLabel(parent_widget)
    new_label.setText(name)
    new_label.setObjectName("label_{}".format(name))
    return new_label



