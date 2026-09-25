import pytest
import gum_parser
import json
import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
VALID_DIR = os.path.join(TESTS_DIR, "valid")
INVALID_DIR = os.path.join(TESTS_DIR, "invalid")


def get_gum_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".gum")]


def parse_json(result):
    """Helper to parse JSON string from gum_parser functions."""
    return json.loads(result)


def find_element(doc, variant_name):
    """Find an element with the given variant name in the document."""
    for elem in doc["elements"]:
        if variant_name in elem:
            return elem[variant_name]
    return None


class TestParse:
    def test_parse_basic(self):
        result = gum_parser.parse_gum('name = "Gum"\nversion = 1')
        doc = parse_json(result)
        assert "elements" in doc
        assert len(doc["elements"]) == 2

    def test_parse_valid_files(self):
        for filename in get_gum_files(VALID_DIR):
            filepath = os.path.join(VALID_DIR, filename)
            with open(filepath, "r") as f:
                content = f.read()
            result = gum_parser.parse_gum(content)
            doc = parse_json(result)
            assert "elements" in doc
            assert len(doc["elements"]) > 0

    def test_parse_invalid_files(self):
        for filename in get_gum_files(INVALID_DIR):
            filepath = os.path.join(INVALID_DIR, filename)
            with open(filepath, "r") as f:
                content = f.read()
            with pytest.raises(ValueError):
                gum_parser.parse_gum(content)

    def test_parse_empty_string(self):
        result = gum_parser.parse_gum("")
        doc = parse_json(result)
        assert "elements" in doc
        assert len(doc["elements"]) == 0

    def test_parse_string_value(self):
        result = gum_parser.parse_gum('name = "test"')
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "String" in value
        assert value["String"] == {"Basic": "test"}

    def test_parse_integer_value(self):
        result = gum_parser.parse_gum("count = 42")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Number" in value
        assert "Integer" in value["Number"]
        assert value["Number"]["Integer"] == 42

    def test_parse_float_value(self):
        result = gum_parser.parse_gum("pi = 3.14")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Number" in value
        assert "Float" in value["Number"]
        assert value["Number"]["Float"] == pytest.approx(3.14)

    def test_parse_boolean_true(self):
        result = gum_parser.parse_gum("enabled = true")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Boolean" in value
        assert value["Boolean"] is True

    def test_parse_boolean_false(self):
        result = gum_parser.parse_gum("disabled = false")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Boolean" in value
        assert value["Boolean"] is False

    def test_parse_null(self):
        result = gum_parser.parse_gum("value = null")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Null" in value

    def test_parse_list(self):
        result = gum_parser.parse_gum("items = [1, 2, 3]")
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "List" in value
        assert len(value["List"]["elements"]) == 3

    def test_parse_table(self):
        result = gum_parser.parse_gum('config = { name = "test" }')
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        value = assignment["value"]
        assert "Table" in value
        assert len(value["Table"]["entries"]) == 1

    def test_parse_bare_key(self):
        result = gum_parser.parse_gum('name = "test"')
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        key = assignment["key"]
        assert "Bare" in key
        assert key["Bare"] == "name"

    def test_parse_quoted_key(self):
        result = gum_parser.parse_gum('"my-key" = "test"')
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        key = assignment["key"]
        assert "Quoted" in key
        assert key["Quoted"] == "my-key"

    def test_parse_dotted_key(self):
        result = gum_parser.parse_gum('a.b.c = "test"')
        doc = parse_json(result)
        assignment = find_element(doc, "Assignment")
        assert assignment is not None
        key = assignment["key"]
        assert "Dotted" in key
        assert len(key["Dotted"]) == 3

    def test_parse_error_message(self):
        with pytest.raises(ValueError) as exc_info:
            gum_parser.parse_gum('name = "unclosed')
        assert "Parse error" in str(exc_info.value) or "line" in str(exc_info.value).lower()


class TestValidate:
    def test_validate_valid_document(self):
        result = gum_parser.validate_gum('name = "Gum"\nversion = 1')
        errors = parse_json(result)
        assert errors == []

    def test_validate_valid_files(self):
        for filename in get_gum_files(VALID_DIR):
            filepath = os.path.join(VALID_DIR, filename)
            with open(filepath, "r") as f:
                content = f.read()
            result = gum_parser.validate_gum(content)
            errors = parse_json(result)
            assert errors == [], f"Expected no errors for {filename}, got: {errors}"

    def test_validate_duplicate_keys(self):
        result = gum_parser.validate_gum('name = "first"\nname = "second"')
        errors = parse_json(result)
        assert len(errors) == 1
        error = errors[0]
        assert "ValidationError" in error
        assert "Duplicate key" in error["ValidationError"]["message"]

    def test_validate_parse_error(self):
        with pytest.raises(ValueError):
            gum_parser.validate_gum('name = "unclosed')


class TestFormat:
    def test_format_basic(self):
        result = gum_parser.format_gum('name = "Gum"')
        assert "name" in result
        assert "Gum" in result

    def test_format_valid_files(self):
        for filename in get_gum_files(VALID_DIR):
            filepath = os.path.join(VALID_DIR, filename)
            with open(filepath, "r") as f:
                content = f.read()
            formatted = gum_parser.format_gum(content)
            assert len(formatted) > 0

    def test_roundtrip(self):
        original = 'name = "Gum"\nversion = 1\nenabled = true\nvalue = null'
        formatted = gum_parser.format_gum(original)
        doc1 = parse_json(gum_parser.parse_gum(original))
        doc2 = parse_json(gum_parser.parse_gum(formatted))
        assert doc1 == doc2

    def test_format_roundtrip_complex(self):
        content = """title = "Test"
version = 1

server = {
    host = "localhost"
    port = 8080
}

items = [1, 2, 3]
"""
        formatted = gum_parser.format_gum(content)
        doc1 = parse_json(gum_parser.parse_gum(content))
        doc2 = parse_json(gum_parser.parse_gum(formatted))
        assert doc1 == doc2

    def test_format_parse_error(self):
        with pytest.raises(ValueError):
            gum_parser.format_gum('name = "unclosed')
