import yaml
from PyQt5 import QtCore, QtWidgets

from datalight.ui import add_widget


class UIWindow:
    def __init__(self):
        self.ui_design = None
        self.num_widgets = 0
        self.widgets = []
        self.central_widget = None
        self.formLayout = None
        self.menubar = None
        self.statusbar = None
        self.OK_button = None

    def ui_setup(self, main_window):
        # Set up main window
        self.set_up_main_window(main_window)

        # Read ui description from YAML
        self.read_ui()

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
        # Put in an OK button
        self.OK_button = QtWidgets.QPushButton(self.central_widget)
        self.OK_button.setObjectName("pushButton_2")
        self.OK_button.setText("OK")
        self.OK_button.clicked.connect(self.do_ok_button)
        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole, self.OK_button)
        self.num_widgets += 1

    @staticmethod
    def do_ok_button(self):
        print("Ahoy!")

    def set_up_main_window(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle("MainWindow")
        main_window.resize(506, 335)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.formLayout = QtWidgets.QFormLayout(self.central_widget)
        self.formLayout.setObjectName("formLayout")
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 506, 21))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

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
        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole,
                                  self.widgets[-1])

        # Add a label for the new widget and position it next to the new widget
        name = element_description["_name"]
        self.widgets.append(add_widget.add_role_label(name, self.central_widget))
        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.LabelRole,
                                  self.widgets[-1])

        # Process widget dependencies
        if "activates_on" in element_description:
            self.widgets[-2].currentTextChanged.connect(lambda: self.enable_dependent_widget(element_description["activates_on"]))

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
        """Return the widget in self.widgets whose objectName ends with name."""
        for widget in self.widgets:
            if widget.objectName().endswith(name):
                return widget


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UIWindow()
    ui.ui_setup(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
