# Methods for populating the menu bar and its actions.
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

import datalight.ui.slot_methods as slot_methods

if TYPE_CHECKING:
    from datalight.ui.main_form import DatalightUIWindow


def setup_file_menu(main_menu: QtWidgets.QMenuBar, datalight_ui: "DatalightUIWindow"):
    main_window = datalight_ui.main_window

    file_menu = main_menu.addMenu('&File')

    # Exit entry
    exit_action = QtWidgets.QAction('&Exit', main_window)
    exit_action.setStatusTip('Exit application')
    exit_action.triggered.connect(QtWidgets.QApplication.quit)
    file_menu.addAction(exit_action)


def setup_about_menu(menu_bar: QtWidgets.QMenuBar, datalight_ui: "DatalightUIWindow"):
    about_menu = menu_bar.addMenu('&About')

    # Author entry
    author_action = QtWidgets.QAction('&Add Author Details', datalight_ui.main_window)
    author_action.setStatusTip('&Add default author details')
    def author_function(): slot_methods.author_menu_action(datalight_ui)
    author_action.triggered.connect(author_function)
    about_menu.addAction(author_action)

    # About entry
    about_action = QtWidgets.QAction('&About', datalight_ui.main_window)
    about_action.setStatusTip('&About Datalight')
    def about_function(): slot_methods.about_menu_action(datalight_ui.ui_path)
    about_action.triggered.connect(about_function)
    about_menu.addAction(about_action)
