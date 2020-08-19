"""Methods for validation of widget values when user tries to uplad a record from the GUI"""
from typing import List, Dict, Union

from PyQt5 import QtWidgets

from datalight.common import logger
from datalight.ui import custom_widgets


def get_widget_values(widgets: List[QtWidgets.QWidget]) -> Dict[str, Union[str, bool]]:
    """Get the values from the widgets on the form.
    :param widgets: A list of form widgets to validate.
    """
    metadata_output = {}
    for widget in widgets:
        widget_name = widget.objectName()
        try:
            metadata_output[widget_name] = widget.get_value()
        except AttributeError:
            # If the widget does not have a get_value method then ignore the widget.
            pass
    return metadata_output


def validate_output_length(widgets: List[QtWidgets.QWidget]) -> Dict[str, bool]:
    """Check whether the widgets on the form have a valid output length.
    :param widgets: A list of form widgets to validate.
    """
    valid_length = {}
    for widget in widgets:
        widget_name = widget.objectName()
        try:
            valid_length[widget_name] = widget.check_length()
        except AttributeError:
            # If the widget does not have a check_length method
            pass
    return valid_length


def validate_widget_contents(widgets: List[QtWidgets.QWidget]) -> Dict[str, bool]:
    """Check whether the widgets on the form have valid values. This is mainly checking whether
    non-optional widgets have been completed.
    :param widgets: A list of form widgets to validate.
    """
    valid_output = {}
    for widget in widgets:
        widget_name = widget.objectName()
        try:
            valid_output[widget_name] = widget.validate_input()
        except AttributeError:
            # If the widget does not have a check_optional method then do not add it to the valid
            # output list.
            pass
    return valid_output


def process_validation_warnings(incomplete_widgets: List[str], short_widgets: List[str]):
    """If there are any problems with user input validation, alert the user by listing the affected widgets."""
    if incomplete_widgets:
        logger.warning("Has invalid output: {}".format(incomplete_widgets))
        warning_text = "Some mandatory fields have not been completed: \n"
        for item in incomplete_widgets:
            warning_text += "• {}\n".format(item)
        custom_widgets.message_box(warning_text, QtWidgets.QMessageBox.Warning)
    elif short_widgets:
        logger.warning("Has invalid length: {}".format(short_widgets))
        warning_text = "Some fields have a minimum length that has not been met: \n"
        for item in short_widgets:
            warning_text += "• {}\n".format(item)
        custom_widgets.message_box(warning_text, QtWidgets.QMessageBox.Warning)