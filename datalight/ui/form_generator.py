"""Generates the UI which is used to input data into Datalight"""
import re
import sys
import yaml
from PyQt5 import QtCore, QtWidgets, QtGui

from datalight.ui import add_widget


class GuiError(Exception):
    """An error raised by the GUI."""


# noinspection PyArgumentList
class UIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI."""
    def __init__(self):
        self.ui_specification = None
        self.num_widgets = 0
        self.widgets = []
        self.layouts = {}
        self.file_upload = {}
        self.group_boxes = {}
        self.central_widget = None
        self.ok_button = None

    def ui_setup(self, main_window):
        """ Initialise widgets on main window before display.

        :param main_window: (QtWidgets.QMainWindow) The main window.
        """
        self.set_up_main_window(main_window)

        # Set up file upload widgets
        self.set_up_file_upload()

        # Read ui description from YAML file
        self.read_basic_ui()

        self.set_up_basic_widgets()

        # self.add_ok_button()

        QtCore.QMetaObject.connectSlotsByName(main_window)

    def add_ok_button(self):
        """ Put in an OK button and attach its click method."""
        self.ok_button = QtWidgets.QPushButton(self.central_widget)
        self.ok_button.setObjectName("pushButton_2")
        self.ok_button.setText("OK")
        self.ok_button.clicked.connect(self.do_ok_button)
        self.form_layout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole,
                                   self.ok_button)
        self.num_widgets += 1

    def do_ok_button(self):
        """
        The on click method for the OK button. Take all data from the form and package
        it up into a dictionary.
        """
        output = {}
        for widget in self.widgets:
            if not isinstance(widget, QtWidgets.QLabel):
                name = widget.objectName()
                if isinstance(widget, QtWidgets.QComboBox):
                    output[name] = widget.currentText()
                elif isinstance(widget, QtWidgets.QPlainTextEdit):
                    output[name] = widget.toPlainText()
                elif isinstance(widget, QtWidgets.QDateEdit):
                    output[name] = widget.date()
                elif isinstance(widget, QtWidgets.QGroupBox):
                    pass
                else:
                    raise GuiError("Unknown widget type when summarising data.")
        print(output)

    def set_up_main_window(self, main_window):
        """ Set up the widgets on the main window.
        :param main_window: (QtWidgets.QMainWindow) The main window.
        :return:
        """
        # Get main window
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle("MainWindow")
        main_window.resize(506, 335)

        # Set up central widget
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")

        # Layout of central widget
        self.layouts["vertical_layout"] = QtWidgets.QVBoxLayout(self.central_widget)
        self.layouts["vertical_layout"].setObjectName("vertical_layout")

        main_window.setCentralWidget(self.central_widget)

    def read_basic_ui(self):
        with open("minimum_ui.yaml", 'r') as input_file:
            ui_design = yaml.load(input_file, Loader=yaml.FullLoader)
        self.ui_specification = ui_design

    def add_ui_element(self, element_description, location):
        """ Add a widget to the form.
        :param element_description: (dict) A description of the element to add.
        :param location: (QWidget) The parent widget of the new widget.
        """

        # Add a new widget and then add it to the layout form
        self.widgets.append(add_widget.add_new_widget(element_description, location))
        self.form_layout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole,
                                   self.widgets[-1])

        # Process widget dependencies
        if "activates_on" in element_description:
            self.widgets[-1].currentTextChanged.connect(
                lambda: self.enable_dependent_widget(element_description["activates_on"]))

        # Add a label for the new widget and position it next to the new widget
        if not isinstance(self.widgets[-1], QtWidgets.QGroupBox):
            self.widgets.append(add_widget.add_role_label(element_description, location))
            self.form_layout.setWidget(self.num_widgets, QtWidgets.QFormLayout.LabelRole,
                                       self.widgets[-1])

        self.num_widgets += 1

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

    def set_up_file_upload(self):

        self.group_boxes["upload"] = QtWidgets.QGroupBox(self.central_widget)
        self.group_boxes["upload"].setTitle("Upload Files")

        self.file_upload["list"] = QtWidgets.QListWidget(self.group_boxes["upload"])
        self.file_upload["list_model"] = QtGui.QStandardItemModel(self.file_upload["list"])

        self.file_upload["file_button"] = QtWidgets.QPushButton(self.group_boxes["upload"])
        self.file_upload["file_button"].setText("Select file to upload")
        self.file_upload["file_button"].clicked.connect(
            lambda: self.file_select_dialogue(directory=False))

        self.file_upload["folder_button"] = QtWidgets.QPushButton(self.group_boxes["upload"])
        self.file_upload["folder_button"].setText("Select folder to upload")
        self.file_upload["folder_button"].clicked.connect(
            lambda: self.file_select_dialogue(directory=True))

        self.file_upload["clear_button"] = QtWidgets.QPushButton(self.group_boxes["upload"])
        self.file_upload["clear_button"].setText("Remove selected files")
        self.file_upload["clear_button"].clicked.connect(
            self.remove_selected_items)

        self.layouts["upload_grid"] = QtWidgets.QGridLayout(self.group_boxes["upload"])

        # Position in grid given by: y-pos, x-pos, y-width, x-width.
        self.layouts["upload_grid"].addWidget(self.file_upload["list"], 0, 0, 1, 3)
        self.layouts["upload_grid"].addWidget(self.file_upload["file_button"], 1, 0, 1, 1)
        self.layouts["upload_grid"].addWidget(self.file_upload["folder_button"], 1, 1, 1, 1)
        self.layouts["upload_grid"].addWidget(self.file_upload["clear_button"], 1, 2, 1, 1)

        self.layouts["vertical_layout"].addWidget(self.group_boxes["upload"])

    def file_select_dialogue(self, directory):

        file_dialogue = QtWidgets.QFileDialog(self.group_boxes["upload"])
        if directory:
            file_dialogue.setFileMode(QtWidgets.QFileDialog.Directory)
            # file_dialogue.options(file_dialogue.ShowDirsOnly)
        else:
            file_dialogue.setFileMode(QtWidgets.QFileDialog.ExistingFiles)

        if file_dialogue.exec():
            for path in file_dialogue.selectedFiles():
                if not self.file_upload["list"].findItems(path, QtCore.Qt.MatchExactly):
                    self.file_upload["list"].addItem(path)
                else:
                    QtWidgets.QMessageBox.warning(self.central_widget, "Warning",
                                                  "File {}, already selected.".format(
                                                      re.split("[\\\/]", path)[-1]))

    def set_up_basic_widgets(self):

        self.group_boxes["basic_metadata"] = QtWidgets.QGroupBox(self.central_widget)
        self.group_boxes["basic_metadata"].setTitle("Basic Metadata")

        self.form_layout = QtWidgets.QFormLayout(self.group_boxes["basic_metadata"])

        # Iteratively insert each element onto the page
        for element_name in self.ui_specification:
            element_description = self.ui_specification[element_name]
            element_description["_name"] = element_name
            if "fancy_name" not in element_description:
                element_description["fancy_name"] = element_name
            if "widget" in element_description:
                self.add_ui_element(element_description, self.group_boxes["basic_metadata"])

        self.layouts["vertical_layout"].addWidget(self.group_boxes["basic_metadata"])

    def remove_selected_items(self):
        files = self.file_upload["list"].selectedItems()
        for item in files:
            row_index = self.file_upload["list"].row(item)
            self.file_upload["list"].takeItem(row_index)


# noinspection PyArgumentList
def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UIWindow()
    ui.ui_setup(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
