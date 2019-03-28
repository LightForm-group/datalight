"""Generates the UI which is used to input data into Datalight"""
import sys
import yaml
from PyQt5 import QtCore, QtWidgets

from datalight.ui import add_widget


class GuiError(Exception):
    """An error raised by the GUI."""


# noinspection PyArgumentList
class UIWindow:
    """The main class for the UI Window. Stores a list of widgets which are associated
    with the UI."""
    def __init__(self):
        self.ui_design = None
        self.num_widgets = 0
        self.widgets = []
        self.central_widget = None
        self.form_layout = None
        self.menu_bar = None
        self.status_bar = None
        self.ok_button = None

    def ui_setup(self, main_window):
        """ Initialise widgets on main window before display.

        :param main_window: (QtWidgets.QMainWindow) The main window.
        """
        self.set_up_main_window(main_window)

        # Read ui description from YAML file
        self.read_ui()

        # Set up file upload widgets
        #self.set_up_file_upload(main_window)

        # Iteratively insert each element onto the page
        for element_name in self.ui_design:
            element_description = self.ui_design[element_name]
            element_description["_name"] = element_name
            if "fancy_name" not in element_description:
                element_description["fancy_name"] = element_name
            if "widget" in element_description:
                self.add_ui_element(element_description)

        self.add_ok_button()

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
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle("MainWindow")
        main_window.resize(506, 335)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.form_layout = QtWidgets.QFormLayout(self.central_widget)
        self.form_layout.setObjectName("formLayout")
        main_window.setCentralWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 506, 21))
        self.menu_bar.setObjectName("menubar")
        main_window.setMenuBar(self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName("statusbar")
        main_window.setStatusBar(self.status_bar)

    def read_ui(self):
        with open("minimum_ui.yaml", 'r') as input_file:
            ui_design = yaml.load(input_file, Loader=yaml.FullLoader)
        self.ui_design = ui_design

    def add_ui_element(self, element_description):
        """ Add a widget to the form.
        :param element_description: (dict) A description of the element to add.
        """

        # Add a new widget and then add it to the layout form
        self.widgets.append(add_widget.add_new_widget(element_description, self.central_widget))
        self.form_layout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole,
                                   self.widgets[-1])

        # Process widget dependencies
        if "activates_on" in element_description:
            self.widgets[-1].currentTextChanged.connect(
                lambda: self.enable_dependent_widget(element_description["activates_on"]))

        # Add a label for the new widget and position it next to the new widget
        if not isinstance(self.widgets[-1], QtWidgets.QGroupBox):
            self.widgets.append(add_widget.add_role_label(element_description, self.central_widget))
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

    def set_up_file_upload(self, main_window):
        self.upload_files_group_box = QtWidgets.QGroupBox(main_window)
        self.upload_files_group_box.setObjectName("upload_files_group_box")

        self.file_upload_list_view = QtWidgets.QListView(self.upload_files_group_box)
        self.file_upload_list_view.setObjectName("file_upload_list_view")

        self.select_file_button = QtWidgets.QPushButton(self.upload_files_group_box)
        self.select_file_button.setObjectName("select_file_button")

        self.select_folder_button = QtWidgets.QPushButton(self.upload_files_group_box)
        self.select_folder_button.setObjectName("select_folder_button")

        self.clear_files_button = QtWidgets.QPushButton(self.upload_files_group_box)
        self.clear_files_button.setObjectName("clear_files_button")

        self.gridLayout = QtWidgets.QGridLayout(self.upload_files_group_box)
        self.gridLayout.setObjectName("group_box_grid")
        self.gridLayout.addWidget(self.file_upload_list_view, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.select_file_button, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.select_folder_button, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.clear_files_button, 1, 2, 1, 1)

        self.verticalLayout = QtWidgets.QVBoxLayout(main_window)
        self.verticalLayout.setObjectName("main_form_vertical_layout")
        self.verticalLayout.addWidget(self.upload_files_group_box)


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
