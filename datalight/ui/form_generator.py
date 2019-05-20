"""Generates the UI which is used to input data into Datalight"""
import sys
from functools import partial

import yaml
from PyQt5 import QtWidgets

from datalight.ui import slot_methods, custom_widgets


class DatalightUIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI.
    :ivar ui_specification:(dict) A dict describing the elements on the form. Read from a YAML file
    :ivar main_window: (QMainWindow) The main application window object.
    :ivar central_widget: (QWidget) The main blank area in which all other widgets sit.
    :ivar layout: (QLayout) The layout of central_widget.
    """
    def __init__(self):
        # The dictionary describing the form
        self.ui_specification = None

        # The main window. The widget from which all other widgets are descended.
        self.main_window = QtWidgets.QMainWindow()

        # The base elements of the main form.
        self.central_widget = QtWidgets.QWidget(self.main_window)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.group_box = None
        self.set_up_main_window()

    def set_up_main_window(self):
        """ Set up the widgets on the main window.
        :return:
        """
        self.main_window.setWindowTitle("Datalight Record Creator")
        self.main_window.setCentralWidget(self.central_widget)

    def ui_setup(self):
        """ Load UI description from style and then add widgets hierarchically."""
        self.read_basic_ui()
        self.add_base_group_box()
        self.populate_author_list()

    def read_basic_ui(self):
        """Read the UI specification from a YAML file."""
        with open("minimum_ui.yaml", encoding='utf8') as input_file:
            ui_specification = yaml.load(input_file, Loader=yaml.FullLoader)
        self.ui_specification = ui_specification

    def add_base_group_box(self):
        """Add a base group box that will contain all other widgets."""

        base_description = {"widget": "GroupBox",
                            "layout": "QFormLayout",
                            "_name": "BaseGroupBox",
                            "children": self.ui_specification}

        self.group_box = custom_widgets.get_new_widget(self.central_widget, base_description)[0]
        self.layout.addWidget(self.group_box)

    def populate_author_list(self):
        with open("author_details.yaml", 'r') as input_file:
            authors = yaml.load(input_file, Loader=yaml.FullLoader)
        author_list_box = self.get_widget_by_name("name")
        affiliation_box = self.get_widget_by_name("affiliation")
        orcid_box = self.get_widget_by_name("orcid")
        author_list_box.addItem("")
        for name in authors:
            author_list_box.addItem(name)
        update_method = lambda name: slot_methods.update_author_details(name, affiliation_box, orcid_box)
        author_list_box.currentIndexChanged[str].connect(update_method)

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
        """Return the widget in self.widgets whose objectName is name.
        :param name: (string) the name of the widget to find.
        :returns widget if widget with `name` is found else returns None."""

        widgets = self.group_box.list_widgets()

        for widget in widgets:
            if widget.objectName() == name:
                return widget
        return None

    def set_window_position(self):
        """Put the UI window in the middle of the screen."""
        self.main_window.frameGeometry()
        screen = self.main_window.windowHandle().screen()
        screen_height = screen.availableGeometry().height()
        screen_width = screen.availableGeometry().width()
        window_height = self.main_window.geometry().height()
        window_width = self.main_window.geometry().width()

        window_vertical = (screen_height - window_height) / 2
        window_horizontal = (screen_width - window_width) / 2
        self.main_window.move(window_horizontal, window_vertical)


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


def connect_button_methods(datalight_ui):
    """Create an association between the buttons on the form and their functions in the code."""
    button_widgets = datalight_ui.main_window.findChildren(QtWidgets.QPushButton)

    for button in button_widgets:
        button_name = button.objectName()
        try:
            button_method = getattr(slot_methods, button_name)
        except AttributeError:
            print("Warning, button '{}' has no method in button_methods.py.".format(
                button.objectName()))
            continue
        button.clicked.connect(partial(button_method, datalight_ui))


def main():
    """The main function."""
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow()
    datalight_ui.ui_setup()
    datalight_ui.main_window.show()
    datalight_ui.set_window_position()
    connect_button_methods(datalight_ui)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
