"""Generates the UI which is used to input data into Datalight"""
import sys
import yaml
from PyQt5 import QtCore, QtWidgets

from datalight.ui import add_widget, static_elements


class GuiError(Exception):
    """An error raised by the GUI."""


class UIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI.
    :ivar ui_specification:(dict) A dict describing the elements on the form. Read from a YAML file
    :ivar num_widgets: (int) The number of widgets on the form
    :ivar widgets:
    :ivar group_boxes: (dict) Group box elements on the form, group boxes help to organise widgets
    :ivar
    """
    def __init__(self):
        # The dictionary describing the form
        self.ui_specification = None

        # The main window. The widget from which all other widgets are descended.
        self.main_window = QtWidgets.QMainWindow()

        # Stores widgets that sit in the main Window. Most widgets should go in a group box instead
        self.widgets = []
        self.num_widgets = 0
        self.group_boxes = {}

        # The base elements of the main form.
        self.layout = None
        self.central_widget = None

        # Datalight specific elements (to be moved into a form description file later)
        self.file_upload = {}
        self.ok_button = None
        self.form_layout = None

    def ui_setup(self):
        """ Initialise widgets on main window before display."""
        self.set_up_main_window()

        # Set up file upload widgets
        #static_elements.set_up_file_upload(ui=self)

        # Read ui description from YAML file
        self.read_basic_ui()

        self.set_up_base_widgets()

        # self.add_ok_button()

        # Connects the buttons to their press methods
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

    def set_up_main_window(self):
        """ Set up the widgets on the main window.
        :return:
        """
        # Get main window
        self.main_window.setObjectName("MainWindow")
        self.main_window.setWindowTitle("MainWindow")
        self.main_window.resize(506, 335)

        # Set up central widget - the blank panel on which other widgets sit.
        self.central_widget = QtWidgets.QWidget(self.main_window)
        self.central_widget.setObjectName("central_widget")

        # Layout of central widget
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setObjectName("vertical_layout")

        self.main_window.setCentralWidget(self.central_widget)

    def read_basic_ui(self):
        with open("minimum_ui.yaml", 'r') as input_file:
            ui_specification = yaml.load(input_file, Loader=yaml.FullLoader)
        self.ui_specification = ui_specification

    def enable_dependent_widget(self, dependencies):
        """Process the 'activates_on' dependency. This turns a widget on or off depending
        on the value of a parent widget.
        :param dependencies: (dictionary) Keys are the widgets to turn on or off. Values are the
        values that activate the child element.
        """
        chosen_value = self.central_widget.sender().currentText()
        for child in dependencies:
            trigger_value = dependencies[child]
            if chosen_value == trigger_value:
                self.get_widget_by_name(child).setEnabled(True)
            else:
                self.get_widget_by_name(child).setEnabled(False)

    def get_widget_by_name(self, name):
        """Return the widget in self.widgets whose objectName ends with name.
        :param name: (string) the name of the widget to find.
        :returns widget if widget with `name` is found else returns none."""
        for widget in self.widgets:
            if widget.objectName() == name:
                return widget
        return None

    def set_up_base_widgets(self):
        """Add the widgets that are children of the main form.
        These should mostly be group boxes, though it might be useful to add some buttons at
        the bottom. If you do this the layout probably wont be great though."""

        # Iteratively insert each element onto the form
        for element_name in self.ui_specification:
            element_description = self.element_setup(element_name)

            if element_description["widget"] == "QGroupBox":
                self.group_boxes[element_name] = GroupBox(element_description, self.main_window)
            else:
                add_widget.add_ui_element(self, element_description, self.group_boxes["basic_metadata"])
                self.layout.addWidget(self.group_boxes[element_name], self)

    def element_setup(self, element_name):
        """This is where secondary processing of the YAML data takes place.
        :param element_name: (string) The name of the element being added
        :returns element_description: (dict) A description of an element, ready to add.
        """
        element_description = self.ui_specification[element_name]
        element_description["_name"] = element_name
        if "fancy_name" not in element_description:
            element_description["fancy_name"] = element_name
        # Every element must have a widget type
        if "widget" not in element_description:
            raise KeyError("Missing 'widget:' type in UI element {}".format(element_name))

        return element_description

    def remove_selected_items(self):
        files = self.file_upload["list"].selectedItems()
        for item in files:
            row_index = self.file_upload["list"].row(item)
            self.file_upload["list"].takeItem(row_index)


class GroupBox:
    """A GroupBox widget organises widgets on a form. This class provides hierarchical storage
    of widgets within GroupBoxes in order to better organise widgets and layouts.
    :ivar layout: (QLayout) The layout applied to the group box.
    :ivar widgets: (list of QWidget) The widgets contained within the GroupBox.
    """

    def __init__(self, group_box_description, parent):
        """ Initialise a new GroupBox

        :param group_box_description: (dict) Description of the group box and widgets
        contained within.
        :param parent: (QWidget) The parent of the group box.
        """
        self.element_description = group_box_description
        self.parent = parent
        self.group_box = None
        self.layout = QtWidgets.QFormLayout(self.group_box)
        self.widgets = []

        self._add_group_box()
        self._add_layout()
        self._add_elements()

    def _add_group_box(self):
        name = self.element_description["_name"]
        self.group_box = QtWidgets.QGroupBox(self.parent)
        self.group_box.setObjectName(name)
        self.group_box.setTitle(self.element_description["fancy_name"])

    def _add_layout(self):
        if "layout" not in self.element_description:
            raise KeyError("Must specify layout type in QGroupBox widget:'{}'".format(
                self.group_box.objectName()))
        if self.element_description["layout"] == "QFormLayout":
            QtWidgets.QFormLayout(self.group_box)
        else:
            raise KeyError("layout type {} in GroupBox {} not understood.".format(
                self.element_description["layout"], self.group_box.objectName()))

    def _add_elements(self):
        for element in self.element_description["children"]:
            new_widget = add_widget.add_new_widget(self.element_description["children"][element],
                                                   self.group_box)
            self.widgets.append(new_widget)
            self._add_element_to_layout(self.widgets[-1])

    def _add_element_to_layout(self, widget):
        self.layout.addWidget(widget)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UIWindow()
    ui.ui_setup()
    ui.main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
