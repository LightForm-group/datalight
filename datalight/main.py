"""Main module for datalight."""

import os
import sys

from PyQt5 import QtWidgets

from datalight import common
from datalight.ui import form_generator
from datalight.ui.form_generator import DatalightUIWindow
from datalight.zenodo import Zenodo as DataRepo


def upload_record(directory_name, metadata_path, zip_name="data.zip", publish=False, sandbox=True):
    """Run datalight scripts to upload file to data repository"""

    token = common.get_authentication_token(sandbox)
    if token is None:
        common.logger.error("Unable to load API token from datalight.config.")
        raise FileNotFoundError("Unable to load API token from datalight.config.")

    try:
        files = common.get_files_path(directory_name)
    except common.DatalightException:
        common.logger.error('Problem with the files to upload.')
        raise common.DatalightException

    if not os.path.exists(metadata_path):
        common.logger.error('Metadata file: {} does not exist.'.format(metadata_path))
        raise FileNotFoundError

    common.zip_data(files, zip_name)
    # Change the name of the files to upload for the zip file created
    files, directory = [zip_name], '.'

    data_repo = DataRepo(token=token, metadata_path=metadata_path, sandbox=sandbox)
    data_repo.deposit_record(files, directory, publish)


def main(ui_path):
    """The main function."""
    app = QtWidgets.QApplication(sys.argv)
    datalight_ui = DatalightUIWindow()
    datalight_ui.ui_setup(ui_path)
    datalight_ui.main_window.show()
    datalight_ui.set_window_position()
    form_generator.connect_button_methods(datalight_ui)
    sys.exit(app.exec_())


if __name__ == "__main__":
    UI_PATH = sys.argv[1]
    main(UI_PATH)

