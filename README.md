# gum-parser

Python bindings for the Gum markup language parser, built with PyO3 and maturin.

## Installation

### From source

```bash
pip install maturin
maturin develop
```

### Building a wheel

```bash
maturin build --release
```

## Usage

```python
import gum_parser

# Parse a Gum document
doc = gum_parser.parse_gum('name = "Gum"\nversion = 1')
print(doc)

# Validate a document
errors = gum_parser.validate_gum('name = "first"\nname = "second"')
print(errors)  # ['Validation error: Duplicate key \'name\' at top level']

# Format a document
formatted = gum_parser.format_gum('name = "Gum"\nversion = 1')
print(formatted)
```

## API

### `parse_gum(input: str) -> dict`

Parse a Gum document string into a dictionary representing the AST.

**Args:**
- `input`: The Gum document string to parse.

**Returns:**
- A dictionary with the parsed document structure.

**Raises:**
- `ValueError`: If the input is malformed.

### `validate_gum(input: str) -> list[str]`

Validate a Gum document string for semantic correctness.

**Args:**
- `input`: The Gum document string to validate.

**Returns:**
- A list of validation error strings (empty if valid).

**Raises:**
- `ValueError`: If the input cannot be parsed.

### `format_gum(input: str) -> str`

Format a Gum document string to normalized output.

**Args:**
- `input`: The Gum document string to format.

**Returns:**
- The formatted Gum document string.

**Raises:**
- `ValueError`: If the input cannot be parsed.

## AST Structure

The parsed document is returned as a nested dictionary:

```python
{
    "type": "Document",
    "elements": [
        {
            "type": "Assignment",
            "key": {"type": "Bare", "value": "name"},
            "value": {"type": "String", "subtype": "Basic", "value": "Gum"}
        }
    ]
}
```

Key types: `Bare`, `Quoted`, `Dotted`
Value types: `String`, `Number`, `Boolean`, `Null`, `Table`, `List`

## Testing

```bash
pytest
```
