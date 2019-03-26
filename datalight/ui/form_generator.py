import datetime
import time

import yaml
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.ui_design = None
        self.num_widgets = 0
        self.widgets = []

    def setupUi(self, MainWindow):

        # Set up main window
        self.set_up_main_window(MainWindow)

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

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def add_ok_button(self):
        # Put in an OK button
        self.OK_button = QtWidgets.QPushButton(self.centralwidget)
        self.OK_button.setObjectName("pushButton_2")
        self.OK_button.setText("OK")
        self.OK_button.clicked.connect(self.do_ok_button)
        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole, self.OK_button)
        self.num_widgets += 1

    @staticmethod
    def do_ok_button(self):
        print("Ahoy!")

    def set_up_main_window(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("MainWindow")
        MainWindow.resize(506, 335)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName("formLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 506, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

    def read_ui(self):
        with open("minimum_ui.yaml", 'r') as input_file:
            ui_design = yaml.load(input_file, Loader=yaml.FullLoader)
        self.ui_design = ui_design

    def add_ui_element(self, element_description):
        """ Add a widget to the form.
        :param element_description: (dict) A description of the element to add.
        """
        widget_type = element_description["widget"]
        if widget_type == "QComboBox":
            self.add_combo_box(element_description)
        elif widget_type == "QPlainTextEdit":
            self.add_plain_text_edit(element_description)
        elif widget_type == "QDateEdit":
            self.add_date_edit(element_description)
        else:
            raise TypeError("No method to add element {}.".format(widget_type))

        # Once a widget has been added to self.widgets, add it to the layout form
        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.FieldRole,
                                  self.widgets[-1])

        # Set widget properties common to all widgets
        if "tooltip" in element_description:
            self.widgets[-1].setToolTip = element_description["tooltip"]
        if "active_when" in element_description:
            self.widgets[-1].setEnabled(False)
        self.add_role_label(element_description["fancy_name"])
        self.num_widgets += 1

    def add_combo_box(self, element_description):
        self.widgets.append(QtWidgets.QComboBox(self.centralwidget))
        name = element_description["_name"]
        self.widgets[-1].setObjectName("combo_{}".format(name))

        if "editable" in element_description:
            self.widgets[-1].setEditable(element_description["editable"])

        if "values" in element_description:
            for item in element_description["values"]:
                self.widgets[-1].addItem(item)

    def add_plain_text_edit(self, element_description):
        self.widgets.append(QtWidgets.QPlainTextEdit(self.centralwidget))
        name = element_description["_name"]
        self.widgets[-1].setObjectName("plain_text_{}".format(name))

    def add_role_label(self, name):
        self.widgets.append(QtWidgets.QLabel(self.centralwidget))
        self.widgets[-1].setText(name)
        self.widgets[-1].setObjectName("label_{}".format(name))

        self.formLayout.setWidget(self.num_widgets, QtWidgets.QFormLayout.LabelRole,
                                  self.widgets[-1])

    def add_date_edit(self, element_description):
        self.widgets.append(QtWidgets.QDateEdit(self.centralwidget))
        name = element_description["_name"]
        self.widgets[-1].setObjectName("date_edit{}".format(name))
        self.widgets[-1].setCalendarPopup(True)
        self.widgets[-1].setDate(datetime.date.today())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
