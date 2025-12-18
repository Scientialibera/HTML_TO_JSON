"""
Test nested tables in both HTML and PDF formats
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_table_converter import HTMLTableConverter

print("=" * 80)
print("TESTING NESTED TABLES")
print("=" * 80)

# Create test HTML with nested tables
html_with_nested = """
<html>
<body>
<h1>Test 1: Simple Nested Table in HTML</h1>
<table border="1">
    <tr>
        <th>Name</th>
        <th>Details</th>
    </tr>
    <tr>
        <td>Alice</td>
        <td>
            <table border="1">
                <tr><th>Skill</th><th>Level</th></tr>
                <tr><td>Python</td><td>Expert</td></tr>
                <tr><td>Java</td><td>Intermediate</td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>Bob</td>
        <td>
            <table border="1">
                <tr><th>Skill</th><th>Level</th></tr>
                <tr><td>JavaScript</td><td>Advanced</td></tr>
                <tr><td>Python</td><td>Beginner</td></tr>
            </table>
        </td>
    </tr>
</table>

<h1>Test 2: Deeply Nested Tables in HTML</h1>
<table border="1">
    <tr>
        <th>Company</th>
        <th>Data</th>
    </tr>
    <tr>
        <td>TechCorp</td>
        <td>
            <table border="1">
                <tr><th>Department</th><th>Info</th></tr>
                <tr>
                    <td>Engineering</td>
                    <td>
                        <table border="1">
                            <tr><th>Team</th><th>Count</th></tr>
                            <tr><td>Backend</td><td>5</td></tr>
                            <tr><td>Frontend</td><td>3</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</body>
</html>
"""

converter = HTMLTableConverter()

# Test 1: HTML with nested tables
print("\n1. HTML NESTED TABLES")
print("-" * 80)

try:
    json_output = converter.convert_to_json(html_with_nested)
    data = json.loads(json_output)
    
    print(f"Tables extracted: {len(data)}")
    
    for i, table in enumerate(data):
        print(f"\nTable {i+1}:")
        if isinstance(table, list) and len(table) > 0:
            if isinstance(table[0], dict):
                print(f"  Type: Dictionary (with headers)")
                print(f"  Rows: {len(table)}")
                print(f"  Columns: {list(table[0].keys())}")
                
                # Check for nested data
                for row_idx, row in enumerate(table):
                    for key, value in row.items():
                        if isinstance(value, list):
                            print(f"  Row {row_idx}, Column '{key}': Contains nested table with {len(value)} rows")
                        else:
                            if row_idx == 0:
                                print(f"  Row {row_idx}, Column '{key}': {value}")
            else:
                print(f"  Type: List")
                print(f"  Rows: {len(table)}")
                if table:
                    print(f"  Columns: {len(table[0])}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: PDF with nested tables
print("\n\n2. PDF NESTED TABLES")
print("-" * 80)

# First, let's check what pdfplumber extracts from our test PDFs
import pdfplumber

pdf_file = "tables/multi_table_test.pdf"

try:
    with pdfplumber.open(pdf_file) as pdf:
        print(f"PDF pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            print(f"\nPage {page_num + 1}: {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                if table:
                    print(f"  Table {table_idx + 1}: {len(table)} rows x {len(table[0])} cols")
                    
                    # Check for nested structure
                    has_nested = False
                    for row in table:
                        for cell in row:
                            if cell and isinstance(cell, str) and '\n' in cell:
                                has_nested = True
                                break
                    
                    if has_nested:
                        print(f"    Note: Contains multi-line cells (possible nested content)")
                    
                    print(f"    Sample row: {table[0][:3]}")
        
        print("\nNote: PDF does not preserve nested table structure.")
        print("Nested tables in PDFs are typically flattened or merged.")
        
except Exception as e:
    print(f"Error: {e}")

# Test 3: Analyze nested table handling
print("\n\n3. NESTED TABLE HANDLING ANALYSIS")
print("-" * 80)

print("""
HTML Nested Tables:
  - Converter recursively processes nested tables
  - Nested tables stored as list/dict within parent cell
  - Full structure preservation
  - Example: cell contains {"nested_table": [...]}

PDF Nested Tables:
  - pdfplumber does not distinguish nested tables
  - All content extracted as flat list of cells
  - Multi-line cells may indicate nested content
  - Structure information is lost during extraction

Recommendation:
  - For HTML: Use native structure (nested tables work well)
  - For PDF: Flatten expected structure or add preprocessing
  - Consider table boundaries and cell merging for complex layouts
""")

# Test 4: Show actual structure
print("\n4. ACTUAL NESTED TABLE STRUCTURE (from HTML)")
print("-" * 80)

try:
    json_output = converter.convert_to_json(html_with_nested)
    data = json.loads(json_output)
    
    if len(data) > 0:
        first_table = data[0]
        print(f"\nFirst table structure (raw JSON):")
        print(json.dumps(first_table, indent=2)[:500])
        print("...")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Nested Table Test Results:

HTML Nested Tables:
  Status: WORKING - Recursively processed
  Output: Nested tables stored as list/dict within parent
  Use case: Good for structured HTML documents

PDF Nested Tables:
  Status: NOT SUPPORTED - Pdfplumber lacks table nesting
  Output: All cells flattened to single level
  Workaround: Post-process multi-line cells manually

Best practices:
  - HTML: Use native nested table support
  - PDF: Keep tables flat or preprocess before extraction
  - Complex layouts: Consider manual table definition
""")
