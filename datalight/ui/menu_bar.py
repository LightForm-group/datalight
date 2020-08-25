# Methods for populating the menu bar and its actions.

from PyQt5 import QtWidgets

from datalight.ui.slot_methods import about_menu_action, author_menu_action


def setup_menu(main_window: QtWidgets.QMainWindow, ui_path: str):
    """Add the menu bar to the form."""
    main_menu = main_window.menuBar()

    setup_file_menu(main_menu, main_window)
    setup_about_menu(main_menu, main_window, ui_path)


def setup_file_menu(main_menu: QtWidgets.QMenuBar, main_window: QtWidgets.QMainWindow):
    file_menu = main_menu.addMenu('&File')

    # Exit entry
    exit_action = QtWidgets.QAction('&Exit', main_window)
    exit_action.setStatusTip('Exit application')
    exit_action.triggered.connect(QtWidgets.QApplication.quit)
    file_menu.addAction(exit_action)


def setup_about_menu(menu_bar: QtWidgets.QMenuBar, main_window: QtWidgets.QMainWindow,
                     ui_path: str):
    about_menu = menu_bar.addMenu('&About')

    # Author entry
    author_action = QtWidgets.QAction('&Add Author Details', main_window)
    author_action.setStatusTip('&Add default author details')
    def author_function(path: str): author_menu_action(ui_path)
    author_action.triggered.connect(author_function)
    about_menu.addAction(author_action)

    # About entry
    about_action = QtWidgets.QAction('&About', main_window)
    about_action.setStatusTip('&About Datalight')
    about_action.triggered.connect(about_menu_action)
    about_menu.addAction(about_action)
