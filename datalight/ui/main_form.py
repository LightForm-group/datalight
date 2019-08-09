"""Generates the UI which is used to input data into Datalight"""
import re
from functools import partial
from typing import Union

from PyQt5 import QtWidgets, QtGui

from datalight.ui import slot_methods, custom_widgets, menu_bar
from datalight.ui.ui_descriptions import file_readers


class DatalightUIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI.
    :ivar ui_specification:(dict) Description of the elements on the core form.
    :ivar experiments: (dict) UI specifications for experiments.
    :ivar main_window: (QMainWindow) The main application widget from which all other widgets are descended.
    :ivar central_widget: (QWidget) The main blank area in which all other widgets sit.
    :ivar central_widget_layout: (QLayout) The layout of central_widget.
    :ivar ui_path: (str) Path to the ui folder containing 'minimum_ui.yaml'.
    :ivar group_box: (GroupBox)
    :ivar authors: (dict) A dictionary of Author names, Affiliations and ORCIDs.
    """
    def __init__(self, ui_path: str):
        self.ui_specification = {}
        self.experiments = {}

        # Main window and some properties
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle("Datalight Record Creator")
        self.main_window.setWindowIcon(QtGui.QIcon("ui/icon.png"))
        self.main_window.setGeometry(0, 0, 500, 800)

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

        # Add a child of scroll area and its layout
        self.scroll_area_contents = QtWidgets.QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.scroll_area_contents_layout = QtWidgets.QHBoxLayout(self.scroll_area_contents)
        self.scroll_area_contents_layout.setContentsMargins(0, 0, 0, 0)

        # Inside the scroll area will go the first group box - the first "user content".
        self.group_box = None
        self.ui_path = ui_path
        self.authors = {}

    def ui_setup(self, metadata_index: str):
        """ Load UI description from files and then add widgets hierarchically."""
        # Setup menu bar
        menu_bar.setup_menu(self.main_window)

        # Get and set experimental UI descriptions
        experimental_metadata = file_readers.get_experimental_metadata(metadata_index)
        self.add_experiments(experimental_metadata)

        # Get and set basic UI descriptions
        self.ui_specification = file_readers.read_basic_ui(self.ui_path)
        self.add_base_group_box()

        # Get and set authors and
        self.authors = file_readers.read_author_list(self.ui_path)
        self.populate_author_list()

        # Add experiments to form
        self.populate_experimental_list()
        self.link_experimental_group_box()

    def add_experiments(self, experiment_description: dict):
        """Add experimental UI descriptions to self."""
        for experiment_name, description in experiment_description.items():
            if "_name" not in description:
                # Set to lower and remove any whitespace.
                _name = experiment_name.lower()
                _name = re.sub(r"\s+", "", experiment_name, flags=re.UNICODE)
                description["_name"] = _name
            self.experiments[experiment_name] = description

    def add_base_group_box(self):
        """Add a base group box that will contain all other widgets."""
        base_description = {"widget": "GroupBox",
                            "layout": "HBoxLayout",
                            "_name": "BaseGroupBox",
                            "children": self.ui_specification}
        self.group_box = custom_widgets.get_new_widget(self.scroll_area_contents, base_description)[0]
        self.group_box.setMinimumSize(600, 800)
        self.scroll_area_contents_layout.addWidget(self.group_box)

    def populate_author_list(self):
        """Populate the author combo_box with the names read from the authors file."""
        author_list_box = self.get_widget_by_name("name")
        affiliation_box = self.get_widget_by_name("affiliation")
        orcid_box = self.get_widget_by_name("orcid")

        author_list_box.addItem("")
        for name in self.authors:
            author_list_box.addItem(name)

        update_method = lambda name: slot_methods.update_author_details(name, affiliation_box, orcid_box, self.authors)
        author_list_box.currentIndexChanged[str].connect(update_method)

    def populate_experimental_list(self):
        """Take the names of the experiments and populate the selection box with them."""
        experiment_combo_box = self.get_widget_by_name("experiment_selection")
        for experiment in self.experiments:
            experiment_combo_box.addItem(experiment, experiment)

    def link_experimental_group_box(self):
        """Link the experimental combo box to the method for updating experimental data."""
        # The combo box which selects the experiment type
        combo_box = self.get_widget_by_name("experiment_selection")

        # The group box containing the experimental data
        experimental_group_box = self.get_widget_by_name("experimental_metadata")

        def update_method():
            slot_methods.update_experimental_metadata(experimental_group_box,
                                                      combo_box.itemData(combo_box.currentIndex()),
                                                      self.experiments)

        combo_box.currentIndexChanged[str].connect(update_method)

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

    def get_widget_by_name(self, name: str) -> Union[QtWidgets.QWidget, None]:
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
        self.main_window.move(window_horizontal, window_vertical)


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
