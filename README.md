# HTML Table to JSON Converter

A robust Python module to convert HTML tables into JSON format. It handles complex table structures including merged cells (rowspan/colspan), nested tables, and jagged rows.

## Features

- Converts HTML tables to JSON.
- Supports `rowspan` and `colspan` by filling the grid structure.
- Handles nested tables recursively.
- Detects headers automatically from `<thead>` or `<th>` elements.
- Outputs a list of dictionaries (if headers exist) or a list of lists.
- Command Line Interface (CLI) support.

## Requirements

- Python 3.x
- beautifulsoup4

Install dependencies:
```bash
pip install beautifulsoup4
```

## Usage

### Python

```python
from html_table_converter import HTMLTableConverter

html_content = """
<table>
    <thead>
        <tr><th>Name</th><th>Age</th></tr>
    </thead>
    <tbody>
        <tr><td>Alice</td><td>30</td></tr>
    </tbody>
</table>
"""

converter = HTMLTableConverter()
json_output = converter.convert_to_json(html_content)
print(json_output)
```

### Command Line

```bash
python html_table_converter.py path/to/file.html
```

## Example

### Input HTML

```html
<table border="1">
    <tr>
        <th rowspan="2">Name</th>
        <th colspan="2">Contact</th>
    </tr>
    <tr>
        <th>Email</th>
        <th>Phone</th>
    </tr>
    <tr>
        <td>John Doe</td>
        <td>john@example.com</td>
        <td>555-1234</td>
    </tr>
</table>
```

### Output JSON

```json
[
    [
        {
            "Name": "Name",
            "Contact": "Email",
            "Contact_1": "Phone"
        },
        {
            "Name": "John Doe",
            "Contact": "john@example.com",
            "Contact_1": "555-1234"
        }
    ]
]
```
