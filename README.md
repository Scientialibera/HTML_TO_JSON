# HTML to JSON Table Converter

Convert HTML and PDF tables to JSON format.

## Features

- ✅ HTML tables to JSON
- ✅ PDF table extraction
- ✅ Merged cells (rowspan/colspan)
- ✅ Nested tables
- ✅ Multi-row headers
- ✅ Multiple tables per file
- ✅ CLI support

## Installation

```bash
pip install -e .
```

## Quick Start

### Python

```python
from html_table_converter import HTMLTableConverter

converter = HTMLTableConverter()

# HTML
json_output = converter.convert_to_json(html_string)

# PDF
json_output = converter.convert_pdf_to_json('file.pdf')
```

### Command Line

```bash
python html_table_converter.py tables.html
python html_table_converter.py tables.pdf
```

## Output

### With Headers
```json
[
  {"Name": "Alice", "Age": "30", "City": "NYC"},
  {"Name": "Bob", "Age": "25", "City": "LA"}
]
```

### Without Headers
```json
[
  ["value1", "value2"],
  ["value3", "value4"]
]
```

### Multi-row Headers
```json
[
  {"Category - Year": "value", "Metric - Type": "value"}
]
```

## API

### `convert_to_json(html_content)`
Convert HTML to JSON. Returns JSON string.

### `convert_pdf_to_json(pdf_path, use_native_json=False)`
Convert PDF to JSON. Returns JSON string.

## Examples

See `examples/` folder for detailed examples:
- Basic extraction
- Metadata analysis  
- Table validation
- PDF analysis

Run examples:
```bash
cd examples
python pdf_metadata_examples.py
python enhanced_converter_metadata.py
python practical_metadata_validation.py
```

## Dependencies

- beautifulsoup4
- pdfplumber

## Supported Tables

- ✅ Simple tables with headers
- ✅ Tables without headers
- ✅ Merged cells (rowspan/colspan)
- ✅ Nested tables
- ✅ Multi-row headers
- ✅ Multiple tables in single file
- ✅ Digital PDF tables

## License

MIT
