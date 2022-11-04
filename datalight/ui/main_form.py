"""Generates the UI which is used to input data into Datalight"""
import pathlib
from functools import partial
from typing import Union

from PyQt5 import QtWidgets, QtGui

import datalight.common
from datalight.ui import slot_methods, custom_widgets, menu_bar
from datalight.ui.custom_widgets import Widget
from datalight.common import logger


class DatalightUIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI.
    :ivar ui_specification: Description of the elements on the core form.
    :ivar experiments: UI specifications for experiments.
    :ivar main_window: The main application widget from which all other widgets
      are descended.
    :ivar central_widget: The main blank area in which all other widgets sit.
    :ivar central_widget_layout: The layout of central_widget.
    :ivar group_box: The base group box.
    :ivar authors: A dictionary of Author names, Affiliations and ORCIDs.
    """
    def __init__(self, root_path: str):
        self.ui_specification = {}
        self.experiments = {}

        # Main window and some properties
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle("Datalight Record Creator")
        self.main_window.setWindowIcon(QtGui.QIcon("ui/images/icon.png"))
        self.main_window.setGeometry(0, 0, 1100, 700)

        # Central widget and its layout
        self.central_widget = QtWidgets.QWidget(self.main_window)
        self.main_window.setCentralWidget(self.central_widget)
        self.central_widget_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)

        # Now add a scroll area
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.central_widget_layout.addWidget(self.scroll_area)

        # Add a child of scroll area and its layout (Scroll area must have a QWidget as a child)
        self.scroll_area_contents = QtWidgets.QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.scroll_area_contents_layout = QtWidgets.QHBoxLayout(self.scroll_area_contents)
        self.scroll_area_contents_layout.setContentsMargins(0, 0, 0, 0)

        # Inside the scroll area will go the first group box - the first "user content".
        self.group_box = None
        self.root_path = pathlib.Path(root_path).resolve()
        self._check_root_path()
        self.config_path = self.root_path.joinpath("datalight.ini")
        self._check_config()
        self.ui_path = self.root_path.joinpath("datalight/ui/")
        self.authors = {}

    def ui_setup(self):
        """ Load UI description from files and then add widgets hierarchically."""
        # Setup menu bar
        self.setup_menu()

        # Get and set basic UI descriptions
        repository_path = self.ui_path.joinpath("ui_descriptions/zenodo.yaml")
        experimental_path = self.ui_path.joinpath("ui_descriptions/metadata.yaml")

        self.ui_specification = datalight.common.read_yaml(repository_path)
        combined_ui = {**self.ui_specification, **datalight.common.read_yaml(experimental_path)}
        self.ui_specification = {"splitter": {"widget": "Splitter",
                                              "_name": "BaseSplitter",
                                              "children": combined_ui}
                                 }
        self.add_base_group_box()

        # Get authors from file
        author_path = self.ui_path.joinpath("ui_descriptions/author_details.yaml")
        self.authors = datalight.common.read_yaml(author_path)

    def setup_menu(self):
        """Add the menu bar to the form."""
        main_menu = self.main_window.menuBar()
        menu_bar.setup_file_menu(main_menu, self)
        menu_bar.setup_about_menu(main_menu, self)

    def add_base_group_box(self):
        """Add a base group box that will contain all other widgets."""
        base_description = {"widget": "GroupBox",
                            "layout": "HBoxLayout",
                            "_name": "BaseGroupBox",
                            "children": self.ui_specification}
        self.group_box = custom_widgets.get_new_widget(self.scroll_area_contents,
                                                       base_description)[0]
        self.scroll_area_contents_layout.addWidget(self.group_box)

    def add_author(self, name: str):
        """Given the name of an author in the authors file, add their details to the author details
        table."""
        author_table = self.group_box.findChildren(QtWidgets.QWidget, "author_details")[0]
        if author_table.rowCount() == 1 and author_table.item(0, 0) is None:
            row_num = 0
        else:
            row_num = author_table.rowCount()
            author_table.insertRow(author_table.rowCount())

        name_cell = QtWidgets.QTableWidgetItem(name)
        author_table.setItem(row_num, 0, name_cell)
        affiliation_cell = QtWidgets.QTableWidgetItem(self.authors[name]["affiliation"])
        author_table.setItem(row_num, 1, affiliation_cell)
        orcid_cell = QtWidgets.QTableWidgetItem(self.authors[name]["orcid"])
        author_table.setItem(row_num, 2, orcid_cell)

    def enable_dependent_widget(self, dependencies: dict):
        """Process the 'activates_on' dependency. This turns a widget on or off depending
        on the value of a parent widget.
        :param dependencies: Keys are the widgets to turn on or off. Values are the
        values that activate the child element.
        """
        chosen_value = self.central_widget.sender().currentText()
        for child in dependencies:
            trigger_value = dependencies[child]
            if chosen_value == trigger_value:
                self.get_widget_by_name(child).setEnabled(True)
            else:
                self.get_widget_by_name(child).setEnabled(False)

    def get_widget_by_name(self, name: str) -> Union[Widget, None]:
        """Return the widget in self.widgets whose objectName is name.
        :param name: The name of the widget to find.
        :returns widget if widget with `name` is found else returns None."""
        for widget in self.group_box.list_widgets():
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
        self.main_window.move(int(window_horizontal), int(window_vertical))

    def _check_root_path(self):
        main_file = self.root_path.joinpath("datalight/main.py")
        if not main_file.exists() and main_file.is_file():
            raise FileNotFoundError("Cannot find main.py."
                                    "You have probably specified given an incorrect root path.")

    def _check_config(self):
        if not self.config_path.exists():
            logger.info("No config file found so creating empty config file.")
            template_path = self.root_path.joinpath("datalight/config_template.txt")
            with open(template_path) as input_file:
                config_text = input_file.read()
            with open(self.config_path, 'w') as output_file:
                output_file.write(config_text)


def connect_button_methods(datalight_ui: DatalightUIWindow):
    """Create an association between the buttons on the form and their functions in the code."""
    button_widgets = datalight_ui.main_window.findChildren(QtWidgets.QPushButton)

    for button in button_widgets:
        button_name = button.objectName()
        try:
            button_method = getattr(slot_methods, button_name)
        except AttributeError:
            print(f"Warning, button '{button.objectName()}' has no method in button_methods.py.")
        else:
            button.clicked.connect(partial(button_method, datalight_ui))
