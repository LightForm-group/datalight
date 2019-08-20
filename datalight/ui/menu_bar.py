# Methods for populating the menu bar and its actions.


from PyQt5 import QtWidgets, QtGui, QtCore


def setup_menu(main_window: QtWidgets.QMainWindow):
    """Add the menu bar to the form."""
    main_menu = main_window.menuBar()

    setup_file_menu(main_menu, main_window)
    setup_about_menu(main_menu, main_window)


def setup_file_menu(main_menu: QtWidgets.QMenu, main_window: QtWidgets.QMainWindow):
    file_menu = main_menu.addMenu('&File')

    # Exit entry
    exit_action = QtWidgets.QAction('&Exit', main_window)
    exit_action.setStatusTip('Exit application')
    exit_action.triggered.connect(QtWidgets.QApplication.quit)
    file_menu.addAction(exit_action)


def setup_about_menu(menu_bar: QtWidgets.QMenu, main_window: QtWidgets.QMainWindow):
    about_menu = menu_bar.addMenu('&About')

    # About entry
    about_action = QtWidgets.QAction('&About', main_window)
    about_action.setStatusTip('&About Datalight')
    about_action.triggered.connect(about_menu_action)
    about_menu.addAction(about_action)


def about_menu_action():
    about_widget = QtWidgets.QMessageBox()
    datalight_icon = QtGui.QPixmap("ui/images/icon.png").scaledToHeight(150, QtCore.Qt.SmoothTransformation)
    about_widget.setIconPixmap(datalight_icon)
    about_widget.setTextFormat(QtCore.Qt.RichText)
    about_widget.setText("<a href='https://github.com/LightForm-group/datalight'>Click here to find out more about DataLight</a><br><br>"
                         "<a href='https://datalight.readthedocs.io'>Click here for documentation.</a><br><br>"
                         "Peter Crowther 2019.")
    about_widget.setWindowTitle("About Datalight")
    about_widget.exec()
