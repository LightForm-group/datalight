# UI Design in Datalight

The user interface (UI) in Datalight is implemented using PyQt5.
In order to provide an extensible user interface, Datalight generates the 
UI from a YAML configuration file. This allows users to extend the UI for 
the collection of their own experiment specific metadata.

The ui YAML files are contained in the datalight/ui folder. The `minimum_ui.yaml` 
file captures the minimum metadata required to upload a record to Zenodo. The 
`advanced_ui.yaml` file captures optional Zenodo metadata elements, some of which are
more useful than others.

The `experiment_list.yaml` is a meta list of additional experimental files. Each line
represents an experiment type.

Custom experiment metadata can be added by adding an name and file name to the
 `experiment_list.yaml` file and adding a relevant `experiment_<NAME>.yaml` file.
 
# Description of the UI language

The YAML files have a specific structure which is interpreted by the code in Datalight.
This is a custom UI description language.

YAML files are organised hierarchically. Each element in the file represents an element
of the UI. The file is read from the top with the elements added in the 
order they appear in the file.

Each element in the YAML file must have a `widget` key-value pair. This describes what
kind of element will be displayed on the UI. Valid options are:
* `QComboBox` - A dropdown menu.
* `QPlainTextEdit` - A free text box.
* `QDateEdit` - A calendar element that allows selection of a date.
* `QGroupBox` - An element that allows the hierarchical organisation of other elements.

All elements have the mandatory property:
* `name` - The internal name of the element. If this is the same as the name of a
Zenodo metadata element, the data will be saved to that element. If not, it will be 
treated as general data and mashed into the `description` field.
* `optional` - Whether this element must be completed in order to send the 
record. This is useful if you want to force a user to insert data into this element.

All elements then have the further optional properties:
* `fancy_name` - The display name of the element
* `active_when` - Allows the activation or deactivation of another element depending on
the value of this element. Use this to have conditional fields which are active only
for some values of this element.
* `tooltip` - The help text that will be displayed when a user mouses over an element.

### QComboBox
An element with `widget: QComboBox` has the mandatory properties:
* `Values` - The values to display in the dropdown box
* `Editable` - If True, the user is allowed to type free text into the Combo box
if False, the user must select one of the pre-defined values.

### QPlainTextEdit
An element with `widget: QPlainTextEdit` has the optional properties:
* `default` - The text that is displayed in the element when the UI is initialised.

### QDateEdit
QDateEdit currently has no additional properties.

### QGroupBox
QGroupBox currently has no additional properties.