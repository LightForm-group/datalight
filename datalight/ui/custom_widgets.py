import datetime
import sys

import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtGui, QtCore


def get_new_widget(parent: "GroupBox", widget_description: dict):
    """Return an instance of a widget described by widget_description.

    :param widget_description: (dict) A description of the element to add.
    :param parent: The instance of the parent widget of the new widget.
    """

    label = None
    grid_layout = None
    widget_type = widget_description["widget"]

    try:
        widget_method = getattr(sys.modules[__name__], widget_type)
    except AttributeError:
        raise AttributeError("No method to add widget {}.".format(widget_type))
    new_widget = widget_method(parent, widget_description)

    # Set widget properties common to all widgets
    if "tooltip" in widget_description:
        new_widget.setToolTip = widget_description["tooltip"]
    if "label" in widget_description:
        label = widget_description["label"]
    if "grid_layout" in widget_description:
        grid_layout = widget_description["grid_layout"].split(",")
        grid_layout = [int(x) for x in grid_layout]
    # Make sure widget is killed when closed to stop memory leak.
    new_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    return new_widget, label, grid_layout


class ComboBox(QtWidgets.QComboBox):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

        if "editable" in widget_description:
            self.setEditable(widget_description["editable"])

        if "values" in widget_description:
            for item in widget_description["values"]:
                self.addItem(widget_description["values"][item], item)

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

    def is_valid(self):
        if not self.optional and self.get_value() == "":
            return False
        else:
            return True


class PlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]
        self.setTabChangesFocus(True)

    def get_value(self):
        return self.toPlainText()

    def is_valid(self):
        if not self.optional and self.get_value() == "":
            return False
        else:
            return True


class DateEdit(QtWidgets.QDateEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

        self.setCalendarPopup(True)
        self.setDate(datetime.date.today())

    def get_value(self):
        return self.date().toString(QtCore.Qt.ISODate)


class PushButton(QtWidgets.QPushButton):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)

        if "button_text" not in widget_description:
            raise KeyError("PushButton {} must have a 'button_text' property.".format(name))
        self.setText(widget_description["button_text"])


class ListWidget(QtWidgets.QListWidget):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

    def get_value(self):
        items = []
        for index in range(self.count()):
            items.append(self.item(index).text())
        return items

    def is_valid(self):
        if not self.optional and self.get_value() == []:
            return False
        else:
            return True


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

        if "default" in widget_description:
            self.setText(str(widget_description["default"]))

    def get_value(self):
        return self.text()

    def is_valid(self):
        if not self.optional and self.get_value() is "":
            return False
        else:
            return True


class Label(QtWidgets.QLabel):
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)

        name = widget_description["_name"]
        self.setObjectName(name)
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

        self.setText(widget_description["text"])


class GroupBox(QtWidgets.QGroupBox):
    """A GroupBox stores child widgets. A GroupBox layout organises the layout of child widgets.

    :ivar element_description: (dict) A description of the GroupBox and any child widgets.
    :ivar parent: (QWidget) The parent widget of the GroupBox.
    :ivar _layout: (QLayout) The layout applied to group_box.
    :ivar _widgets: (list of QWidget) The widgets contained within this GroupBox.
    """

    def __init__(self, parent, group_box_description):
        """ Initialise a new GroupBox

        :param parent: (QWidget) The parent of the group box.
        :param group_box_description: (dict) Specification of the group box and widgets
        contained by this GroupBox.
        """
        super().__init__(parent)
        self.element_description = group_box_description
        self.parent = parent
        self._layout = None
        self._widgets = []

        name = self.element_description["_name"]
        self.setObjectName(name)
        if "title" in self.element_description:
            self.setTitle(self.element_description["title"])
        else:
            self.setStyleSheet("QGroupBox#{} {{ border: 0px;}}".format(name))

        self._add_layout()
        self._add_children()

    def _add_layout(self):
        if "layout" not in self.element_description:
            raise KeyError("Must specify layout type in QGroupBox widget:'{}'".format(
                self.objectName()))
        layout = self.element_description["layout"]
        if layout == "FormLayout":
            self._layout = QtWidgets.QFormLayout(self)
        elif layout == "GridLayout":
            self._layout = QtWidgets.QGridLayout(self)
        elif layout == "HBoxLayout":
            self._layout = QtWidgets.QHBoxLayout(self)
        elif layout == "VBoxLayout":
            self._layout = QtWidgets.QVBoxLayout(self)
        else:
            raise KeyError("layout type {} in GroupBox {} not understood.".format(
                self.element_description["layout"], self.objectName()))

    def _add_children(self):
        if "children" in self.element_description:
            for element_name in self.element_description["children"]:
                element_description = self.element_description["children"][element_name]
                element_description = element_setup(element_name, element_description)
                self.add_widget(*get_new_widget(self, element_description))

    def add_widget(self, widget, label=None, grid_layout=None):
        self._widgets.append(widget)
        self.add_widget_to_layout(self._widgets[-1], label, grid_layout)

    def add_widget_to_layout(self, widget, label=None, grid_layout=None):
        if isinstance(self._layout, QtWidgets.QFormLayout):
            self.add_widget_to_form_layout(widget, label)
        elif isinstance(self._layout, QtWidgets.QGridLayout):
            self.add_widget_to_grid_layout(widget, grid_layout)
        elif isinstance(self._layout, QtWidgets.QHBoxLayout):
            self._layout.addWidget(widget)
        elif isinstance(self._layout, QtWidgets.QVBoxLayout):
            self._layout.addWidget(widget)
        else:
            print("Unknown layout type '{}'".format(self._layout))

    def remove_widget_from_layout(self, widget):
        self._layout.removeWidget(widget)

    def add_widget_to_form_layout(self, widget, label=None):
        if label is None:
            self._layout.addRow(widget)
        else:
            self._layout.addRow(label, widget)

    def add_widget_to_grid_layout(self, widget, grid_layout):
        self._layout.addWidget(widget, *grid_layout)

    def list_widgets(self):
        """Recursively list widgets in this GroupBox and contained GroupBoxes."""
        widgets = []
        for widget in self._widgets:
            if isinstance(widget, GroupBox):
                widgets.extend(widget.list_widgets())
        widgets.extend(self._widgets)
        return widgets


def element_setup(element_name, element_description):
    """This is where secondary processing of the YAML data takes place. These method is applied to
    every widget.
    :param element_name: (string) The base name of the widget being added.
    :param element_description: (string) The name of the element being added
    :returns element_description: (dict) A description of an element, ready to add.
    """
    element_description["_name"] = element_name
    # Every element must have a widget type
    if "widget" not in element_description:
        raise KeyError("Missing 'widget:' type in UI element {}".format(element_name))

    return element_description
