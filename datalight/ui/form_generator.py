"""Generates the UI which is used to input data into Datalight"""
import sys
import yaml
from PyQt5 import QtCore, QtWidgets

from datalight.ui import add_widget


class GuiError(Exception):
    """An error raised by the GUI."""


class DatalightUIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI.
    :ivar ui_specification:(dict) A dict describing the elements on the form. Read from a YAML file
    :ivar main_window: (QMainWindow) The main application window object.
    :ivar widgets: (List of QWidget) Non QGroupBox widgets that sit in the main window.
    :ivar containers: (List of Container) Containers that contain group boxes that sit in the main
    window.
    :ivar central_widget: (QWidget) The main blank area in which all other widgets sit.
    :ivar central_widget_layout: (QLayout) The layout of central_widget.
    """
    def __init__(self):
        # The dictionary describing the form
        self.ui_specification = None

        # The main window. The widget from which all other widgets are descended.
        self.main_window = QtWidgets.QMainWindow()

        self.widgets = []
        self.containers = {}

        # The base elements of the main form.
        self.central_widget = QtWidgets.QWidget(self.main_window)
        self.central_widget_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.set_up_main_window()

    def set_up_main_window(self):
        """ Set up the widgets on the main window.
        :return:
        """
        # Get main window
        self.main_window.setWindowTitle("Datalight Record Creator")
        self.main_window.resize(506, 335)
        self.main_window.setCentralWidget(self.central_widget)

    def ui_setup(self):
        """ Initialise widgets on main window before display."""

        # Set up file upload widgets
        # static_elements.set_up_file_upload(ui=self)

        # Read ui description from YAML file
        self.read_basic_ui()

        self.set_up_base_widgets()

        # self.add_ok_button()

        # Connects the buttons to their press methods
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

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
            element_description = element_setup(element_name, self.ui_specification[element_name])

            if element_description["widget"] == "QGroupBox":
                self.containers[element_name] = Container(element_description, self.central_widget)
                self.central_widget_layout.addWidget(self.containers[element_name].group_box)
            else:
                add_widget.add_ui_element(self, element_description, self.central_widget)




class Container:
    """A Container provides hierarchical storage in order to better organise widgets GroupBoxes
    and layouts. A Container stores a GroupBox widget, its layout its child widgets and any
    child Containers.
    :ivar element_description: (dict) A description of the GroupBox and any child widgets.
    :ivar parent: (QWidget) The parent widget of the GroupBox.
    :ivar group_box: (QGroupBox) The GropBox contined by this Container.
    :ivar layout: (QLayout) The layout applied to group_box.
    :ivar widgets: (list of QWidget) The widgets contained within group_box.
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
        self.containers = {}
        self.layout = None
        self.widgets = []

        self._add_group_box()
        self._add_layout()
        self._add_elements()

    def _add_group_box(self):
        name = self.element_description["_name"]
        self.group_box = QtWidgets.QGroupBox(self.parent)
        self.group_box.setObjectName(name)
        self.group_box.setTitle(self.element_description["label"])

    def _add_layout(self):
        if "layout" not in self.element_description:
            raise KeyError("Must specify layout type in QGroupBox widget:'{}'".format(
                self.group_box.objectName()))
        if self.element_description["layout"] == "QFormLayout":
            self.layout = QtWidgets.QFormLayout(self.group_box)
        else:
            raise KeyError("layout type {} in GroupBox {} not understood.".format(
                self.element_description["layout"], self.group_box.objectName()))

    def _add_elements(self):
        if "children" in self.element_description:
            for element_name in self.element_description["children"]:
                element_description = self.element_description["children"][element_name]
                element_description = element_setup(element_name, element_description)
                add_widget.add_ui_element(self, element_description, self.group_box)


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


def main():
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow()
    datalight_ui.ui_setup()
    datalight_ui.main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
