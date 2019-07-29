import sys

from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self):
        self.main_window = QtWidgets.QMainWindow()

        # Set central widget
        self.centralwidget = QtWidgets.QWidget(self.main_window)
        self.main_window.setCentralWidget(self.centralwidget)

        # central widget layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        # scroll area
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.horizontalLayout.addWidget(self.scrollArea)

        # scroll area contents
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 628, 818))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # Scroll area contents layout
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)

        # Actual content
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setMinimumSize(QtCore.QSize(600, 800))
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setText("Hello")
        self.horizontalLayout_3.addWidget(self.pushButton_2)



def main():
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = Ui_MainWindow()
    datalight_ui.setupUi()
    datalight_ui.main_window.show()

    sys.exit(app.exec_())

main()