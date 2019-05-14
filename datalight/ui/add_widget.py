"""Methods to prepare widgets for addition to a UI form"""

from datalight.ui import custom_widgets
from datalight.ui.form_generator import Container


def add_ui_element(parent_container: Container, element_description: dict, parent):
    """Add a non-GroupBox widget to the form.
    :param parent_container: (Container) Where the widget instance will be stored.
    :param element_description: (dict) A description of the element to add.
    :param parent: (QWidget) The instance of the parent widget of the new widget.
    """

    if element_description["widget"] == "QGroupBox":
        # If it is a group box then add a new Container to the parent
        name = element_description["_name"]
        new_container = Container(element_description, parent)
        parent_container.add_container(name, new_container)
    else:
        label = None
        grid_layout = None
        new_widget = get_new_widget(element_description, parent)
        if "label" in element_description:
            label = element_description["label"]
        if "grid_layout" in element_description:
            grid_layout = element_description["grid_layout"].split(",")
            grid_layout = [int(x) for x in grid_layout]
        parent_container.add_widget(new_widget, label, grid_layout)


def get_new_widget(element_description, parent_widget):
    """Return a new non-Group box widget."""
    widget_type = element_description["widget"]

    try:
        new_widget = getattr(custom_widgets, widget_type)(parent_widget, element_description)
    except AttributeError:
        raise AttributeError("No method to add element {}.".format(widget_type))

    # Set widget properties common to all widgets
    if "tooltip" in element_description:
        new_widget.setToolTip = element_description["tooltip"]

    return new_widget
