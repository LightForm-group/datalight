"""Tests for zenodo_metadata.py"""

import pathlib
import pytest

import datalight.zenodo_metadata as zenodo_metadata

# Path where the tests are located
test_directory = pathlib.Path(__file__).parent

# Path where sample metadata files are located
metadata_path = test_directory / pathlib.Path('metadata/minimum_valid.yml')
invalid_metadata_path = test_directory / pathlib.Path('metadata/invalid_metadata.yml')
non_open_license_path = test_directory / pathlib.Path('metadata/non_open_license.yml')
closed_record_path = test_directory / pathlib.Path('metadata/closed_record.yml')
extra_properties_path = test_directory / pathlib.Path('metadata/extra_properties.yml')


class TestZenodoMetadata:
    """Tests for the ZenodoMetadata class."""

    @staticmethod
    def test_read_schema():
        """A valid schema can be read from a file."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_schema()

        assert isinstance(metadata_reader.schema, dict)
        assert metadata_reader.schema["title"] == 'Zenodo API upload metadata schema'

    @staticmethod
    def test_schema_not_found():
        """Schema_path must be a valid path type."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.schema_path = "AAA"
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            metadata_reader.set_schema()

    @staticmethod
    def test_read_metadata():
        """Metadata can be read from a valid file."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata = metadata_reader._read_metadata(metadata_path)
        assert isinstance(metadata, dict)
        assert metadata["title"] == "Title of the dataset"

    @staticmethod
    def test_read_bad_metadata():
        """Metadata_path must be a path type."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            _ = metadata_reader._read_metadata("AAA")

    @staticmethod
    def test_set_metadata():
        """Metadata can be read from a valid file."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(metadata_path)
        assert isinstance(metadata_reader.metadata, dict)
        assert metadata_reader.metadata["title"] == "Title of the dataset"

    @staticmethod
    def test_set_bad_metadata():
        """Metadata_path must be a path type."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        with pytest.raises(TypeError):
            metadata_reader.set_metadata({"Title": "hi"})

    @staticmethod
    def test_validate_valid_metadata():
        """Valid metadata should not raise an exception."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(metadata_path)
        metadata_reader.set_schema()
        metadata_reader.validate_metadata()
        assert metadata_reader.metadata_validated is True

    @staticmethod
    def test_validate_no_metadata():
        """Metadata must be provided."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_schema()
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            metadata_reader.validate_metadata()

    @staticmethod
    def test_validate_no_schema():
        """A schema must be provided for validation."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(metadata_path)
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            metadata_reader.validate_metadata()

    @staticmethod
    def test_validate_metadata_missing_key():
        """All required metadata must be present or an exeption should be raised."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(invalid_metadata_path)
        metadata_reader.set_schema()
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            metadata_reader.validate_metadata()

    @staticmethod
    def test_validate_invalid_license():
        """An open or embargoed recode must have an open license."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(non_open_license_path)
        metadata_reader.set_schema()
        with pytest.raises(zenodo_metadata.ZenodoMetadataException):
            metadata_reader.validate_metadata()

    @staticmethod
    def test_validate_closed_access():
        """A closed record is allowed to have a non open license."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(closed_record_path)
        metadata_reader.set_schema()
        metadata_reader.validate_metadata()
        assert metadata_reader.metadata_validated is True
        assert metadata_reader.metadata["title"] == "Sample metadata"

    @staticmethod
    def test_remove_extra_properties():
        """Test removing non-valid properties from a metadata record."""
        metadata_reader = zenodo_metadata.ZenodoMetadata()
        metadata_reader.set_metadata(extra_properties_path)
        metadata_reader.set_schema()
        metadata_reader.validate_metadata()
        assert metadata_reader.metadata_validated is True
        assert metadata_reader.metadata["title"] == "Sample metadata"
        assert "extra_data" not in metadata_reader.metadata.keys()
        assert "number_of_cats_confused" not in metadata_reader.metadata.keys()


class TestLicenceValidation:
    """Most of this class has already been tested by the validation tests
    of the ZenodoMetadata class."""
    @staticmethod
    def test_read_local_licenses():
        """Check that the local license file can be read in the event
        of not being able to connect to the internet."""
        license_checker = zenodo_metadata._LicenseStatus("cc-by-4.0", "open")
        open_licenses = license_checker._get_local_open_licenses()
        assert isinstance(open_licenses, dict)
