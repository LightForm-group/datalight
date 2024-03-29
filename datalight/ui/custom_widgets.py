"""This module contains overloaded PyQT widgets. By overloading the base widgets,
 custom attributes and behaviour can be defined."""

import datetime
import sys
from typing import List, Tuple, Union, TypeVar

import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtGui, QtCore

Widget = TypeVar('Widget', bound=QtWidgets.QWidget)


def get_new_widget(parent: Widget, widget_description: dict) -> Tuple[
      Widget, Union[None, str], Union[None, List[int]]]:
    """Return an instance of a widget described by widget_description.

    :param widget_description: (dict) A description of the element to add.
    :param parent: The instance of the parent widget of the new widget.
    """

    label = None
    grid_layout = None
    widget_type = widget_description["widget"]

    if "help_text" in widget_description:
        new_widget = HelpWidget(parent, widget_description)
    else:
        try:
            widget_method = getattr(sys.modules[__name__], widget_type)
        except AttributeError:
            raise AttributeError(f"No method to add widget {widget_type}.")
        new_widget = widget_method(parent, widget_description)

    # Set widget properties common to all widgets
    if "tooltip" in widget_description:
        new_widget.setToolTip(widget_description["tooltip"])
    if "label" in widget_description:
        label = widget_description["label"]
    if "grid_layout" in widget_description:
        grid_layout = widget_description["grid_layout"].split(",")
        grid_layout = [int(x) for x in grid_layout]
    # Make sure widget is killed when closed to stop memory leak.
    new_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    return new_widget, label, grid_layout


class WidgetMixin:
    """This is a mixin class to provide common methods for Widget classes.

    Even though 'optional' and 'name' are class variables in the mixin, they are converted to
    instance variables on calling the set_common_properties method. set_common_properties
    is a pseudo __init__ method, __init__ cannot be used directly because its arguments
    vary from the __init__ methods of the widget superclasses. For this reason, any subclass
    of this class should call super().set_common_properties()
    """
    optional = None
    name = None
    minimum_length = 0

    def set_common_properties(self, widget_description):
        """
        A pseudo __init__ method for the mixin. Should be called by any child that inherits
        this mixin class.
        """
        if "name" not in widget_description:
            self.name = widget_description["_name"]
        self.setObjectName(self.name)

        self.optional = True
        if "optional" in widget_description:
            self.optional = widget_description["optional"]

    def get_value(self):
        """Get the user input value of a widget. The result depends on the widget type."""
        # If the subclass does not implement this method, raise an AttributeError
        raise AttributeError

    def validate_input(self):
        """
        Validate the widget contents.
        If the widget is not optional then the user must input a value.
        Return True if the widget value is valid else return False.
        """
        # If the subclass does not implement this method, raise an AttributeError
        raise AttributeError

    def check_length(self):
        """If the widget has a minimum_length field, check whether the input meets this."""
        # If the subclass does not implement this method, raise an AttributeError
        raise AttributeError


class Splitter(QtWidgets.QSplitter, WidgetMixin):
    def __init__(self, parent_widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)
        self.setOrientation(QtCore.Qt.Horizontal)
        self._add_children(widget_description)

    def _add_children(self, widget_description: dict):
        if "children" in widget_description:
            for element_name in widget_description["children"]:
                element_description = widget_description["children"][element_name]
                element_description = element_setup(element_name, element_description)
                self.addWidget(get_new_widget(self, element_description)[0])


class CheckBox(QtWidgets.QCheckBox, WidgetMixin):
    def __init__(self, parent_widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        if widget_description["default"] is True:
            self.setChecked(True)

    def get_value(self) -> bool:
        if self.isChecked():
            return True
        else:
            return False


class HelpWidget(QtWidgets.QWidget, WidgetMixin):
    """Combination of another widget and a HelpButton."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)
        self.help_text = widget_description.pop("help_text")

        # Add the help button and the actual widget that needs the help button.
        button_name = {f"_name": "{widget_description['_name'])}_help"}
        self.help_button = HelpButton(self, button_name)
        self.help_button.clicked.connect(lambda: self.set_tooltip())
        self.input_widget = get_new_widget(self, widget_description)

        # Add a layout to make sure that the two elements stack nicely.
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.input_widget[0])
        self.layout.addWidget(self.help_button)

    def set_tooltip(self):
        tip_position = self.help_button.mapToGlobal(QtCore.QPoint(25, -10))
        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 12))
        QtWidgets.QToolTip.showText(tip_position, self.help_text)


class HelpButton(QtWidgets.QToolButton, WidgetMixin):
    """A small button with a question mark on it that raises some sort of help text.
    Most of the time this shouldn't be called directly. In order to get the help button to line
    up nicely with other widgets on a form layout it is nested in a HelpWidget."""

    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        self.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxQuestion))


class ComboBox(QtWidgets.QComboBox, WidgetMixin):
    """A widget that allows selection from a drop down list."""
    def __init__(self, parent_widget, widget_description):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        self.parent_widget = parent_widget

        if "editable" in widget_description:
            self.setEditable(widget_description["editable"])

        # Add items with the key as a extra field stored in the UserRole.
        # This key is useful if Zenodo requires a specific format but it is not
        # pretty to display as a label.
        if "values" in widget_description:
            combo_values = widget_description["values"]
            if isinstance(combo_values, dict):
                for key, value in combo_values.items():
                    self.addItem(value, key)
            elif isinstance(combo_values, list):
                for item in combo_values:
                    self.addItem(item, item)
            else:
                raise TypeError(f"Cannot add {combo_values} to ComboBox, "
                                f"must be dict or list Type.")

        # Keys are the values of this combobox that activate another widget. Values are the
        # widget name it activates. There may be more than one key-value pair.
        if "activates_when" in widget_description:
            self.activates_when = widget_description["activates_when"]
        else:
            self.activates_when = None

    def paintEvent(self, event: QtGui.QPaintEvent):
        """
        Overloads the method of the QComboBox superclass to do something every time the
        box is repainted. This seems to be the easiest way to make the value of one widget
        dependent on another.
        """
        super().paintEvent(event)

        # Process widget dependencies
        if self.activates_when:
            for value, dependent_widget_name in self.activates_when.items():
                dependent_widget = self.parent_widget.findChild(QtWidgets.QWidget,
                                                                dependent_widget_name)
                if self.get_value() == value:
                    dependent_widget.setEnabled(True)
                else:
                    dependent_widget.setEnabled(False)

    def get_value(self) -> str:
        if not self.isEnabled():
            # If the combobox is disabled then we pretend it does not have a value at all.
            raise AttributeError
        if self.isEditable():
            return self.currentText()
        else:
            # For fixed vocabulary boxes, return the currentData field
            # as this returns the key value stored in the UserRole
            return self.currentData()

    def validate_input(self) -> bool:
        if not self.optional and self.get_value() == "":
            return False
        return True


class PlainTextEdit(QtWidgets.QPlainTextEdit, WidgetMixin):
    """A larger box to add free-form text."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        if "minimum_length" in widget_description:
            self.minimum_length = widget_description["minimum_length"]

        if "default" in widget_description:
            self.setPlainText(str(widget_description["default"]))

        self.setTabChangesFocus(True)

    def get_value(self) -> str:
        return self.toPlainText()

    def validate_input(self) -> bool:
        if not self.optional and self.get_value() == "":
            return False
        return True

    def check_length(self) -> bool:
        """Return True if value of Text box is greater than the minimum length."""
        if len(self.get_value()) >= self.minimum_length:
            return True
        return False


class DateEdit(QtWidgets.QDateEdit, WidgetMixin):
    """A widget that allows date selection from a dropdown popup."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        self.setCalendarPopup(True)
        self.setDate(datetime.date.today())

    def get_value(self) -> str:
        return self.date().toString(QtCore.Qt.ISODate)


class PushButton(QtWidgets.QPushButton, WidgetMixin):
    """A push button. In order to make the  """
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        if "button_text" not in widget_description:
            raise KeyError(f"PushButton {self.name} must have a 'button_text' property.")
        self.setText(widget_description["button_text"])


class ListWidget(QtWidgets.QListWidget, WidgetMixin):
    """Allows display and selection of items from a scrolling list."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

    def get_value(self) -> List[str]:
        items = []
        for index in range(self.count()):
            items.append(self.item(index).text())
        return items

    def validate_input(self) -> bool:
        if not self.optional and self.get_value() == []:
            return False
        return True


class LineEdit(QtWidgets.QLineEdit, WidgetMixin):
    """A free text box that spans a single line."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        if "default" in widget_description:
            self.setText(str(widget_description["default"]))

        if "minimum_length" in widget_description:
            self.minimum_length = widget_description["minimum_length"]

    def validate_input(self) -> bool:
        if not self.optional and self.get_value() == "":
            return False
        return True

    def get_value(self) -> str:
        return self.text()

    def check_length(self) -> bool:
        """Return True if value of Text box is greater than the minimum length."""
        if len(self.get_value()) >= self.minimum_length:
            return True
        return False


class Table(QtWidgets.QTableWidget, WidgetMixin):
    """A table to display tabular data."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        column_titles = widget_description["column_titles"]
        for _ in column_titles:
            self.insertColumn(0)
        self.insertRow(0)
        self.setHorizontalHeaderLabels(widget_description["column_titles"])

    def validate_input(self) -> bool:
        if self.optional:
            return True

        data = self._collect_data()
        for row in data:
            for column in row:
                if column == "":
                    return False
        return True

    def get_value(self) -> List[list]:
        return self._collect_data()

    def _collect_data(self) -> List[list]:
        data = []
        for row_index in range(self.rowCount()):
            row = []
            for column_index in range(self.columnCount()):
                cell_data = self.item(row_index, column_index)
                if cell_data:
                    row.append(cell_data.data(QtCore.Qt.ItemDataRole.DisplayRole))
                else:
                    row.append("")
            data.append(row)
        return data


class Label(QtWidgets.QLabel, WidgetMixin):
    """A label to annotate the form."""
    def __init__(self, parent_widget: Widget, widget_description: dict):
        super().__init__(parent_widget)
        super().set_common_properties(widget_description)

        self.setText(widget_description["text"])


class GroupBox(QtWidgets.QGroupBox, WidgetMixin):
    """A GroupBox stores child widgets. A GroupBox layout organises the layout of child widgets.

    :ivar element_description: (dict) A description of the GroupBox and any child widgets.
    :ivar parent: (QWidget) The parent widget of the GroupBox.
    :ivar _layout: (QLayout) The layout applied to group_box.
    :ivar _widgets: (list of QWidget) The widgets contained within this GroupBox.
    """

    def __init__(self, parent: Widget, group_box_description: dict):
        """ Initialise a new GroupBox

        :param parent: The parent of the group box.
        :param group_box_description: Specification of the group box and widgets
        contained by this GroupBox.
        """
        super().__init__(parent)
        super().set_common_properties(group_box_description)

        self.element_description = group_box_description
        self.parent = parent
        self._layout = None
        self._widgets: List[Widget] = []

        if "title" in self.element_description:
            self.setTitle(self.element_description["title"])
        else:
            self.setStyleSheet("QGroupBox#{} {{ border: 0px;}}".format(self.name))

        self._add_layout()
        self._add_children()

    def _add_layout(self):
        if "layout" not in self.element_description:
            raise KeyError(f"Must specify layout type in QGroupBox widget:'{self.objectName()}'")
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
            raise KeyError(f"layout type {self.element_description['layout']} in "
                           f"GroupBox {self.objectName()} not understood.")
        self._layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

    def _add_children(self):
        if "children" in self.element_description:
            for element_name in self.element_description["children"]:
                element_description = self.element_description["children"][element_name]
                element_description = element_setup(element_name, element_description)
                self.add_widget(*get_new_widget(self, element_description))

    def add_widget(self, widget: Widget, label: str = None, grid_layout=None):
        """Add 'widget' to this layout."""
        self._widgets.append(widget)
        self._add_widget_to_layout(self._widgets[-1], label, grid_layout)

    def _add_widget_to_layout(self, widget: Widget, label: str = None,
                              grid_position: List[int] = None):
        if isinstance(self._layout, QtWidgets.QFormLayout):
            self._add_widget_to_form_layout(widget, label)
        elif isinstance(self._layout, QtWidgets.QGridLayout):
            self._add_widget_to_grid_layout(widget, grid_position)
        elif isinstance(self._layout, QtWidgets.QHBoxLayout):
            self._layout.addWidget(widget)
        elif isinstance(self._layout, QtWidgets.QVBoxLayout):
            self._layout.addWidget(widget)
        else:
            print("Unknown layout type '{self._layout}'")

    def remove_widget_from_layout(self, widget: Widget):
        """Remove a widget from this layout."""
        self._layout.removeWidget(widget)

    def _add_widget_to_form_layout(self, widget: Widget, label: str = None):
        if label is None:
            self._layout.addRow(widget)
        else:
            self._layout.addRow(label, widget)

    def _add_widget_to_grid_layout(self, widget: Widget, grid_position: List[int]):
        self._layout.addWidget(widget, *grid_position)

    def list_widgets(self) -> List[QtWidgets.QWidget]:
        """Recursively list widgets in this GroupBox and contained GroupBoxes."""
        widgets = []
        for widget in self._widgets:
            if isinstance(widget, GroupBox):
                widgets.extend(widget.list_widgets())
        widgets.extend(self._widgets)
        return widgets


def message_box(message_text: str, message_type: QtWidgets.QMessageBox.Icon):
    """A generic message box to alert the user of something."""
    warning_widget = QtWidgets.QMessageBox()
    warning_widget.setIcon(message_type)
    warning_widget.setText(message_text)
    warning_widget.setWindowTitle("Datalight message")
    warning_widget.exec()


def element_setup(element_name: str, element_description: dict) -> dict:
    """This is where secondary processing of the YAML data takes place. These method is applied to
    every widget.
    :param element_name: The base name of the widget being added.
    :param element_description: The name of the element being added
    :returns element_description: A description of an element, ready to add.
    """
    element_description["_name"] = element_name
    # Every element must have a widget type
    if "widget" not in element_description:
        raise KeyError(f"Missing 'widget:' type in UI element {element_name}")

    return element_description
