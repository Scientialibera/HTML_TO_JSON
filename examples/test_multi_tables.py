import json
from html_table_converter import HTMLTableConverter

print("=" * 80)
print("TESTING MULTIPLE TABLES")
print("=" * 80)

converter = HTMLTableConverter()

# Test HTML
print("\n" + "=" * 80)
print("HTML FILE TEST")
print("=" * 80)

html_json = converter.convert_to_json(open("multi_table_test.html").read())
html_data = json.loads(html_json)

print(f"\nTotal tables found in HTML: {len(html_data)}")

for idx, table in enumerate(html_data):
    print(f"\n{'='*40}")
    print(f"TABLE {idx + 1}")
    print(f"{'='*40}")
    
    if isinstance(table, list) and len(table) > 0:
        if isinstance(table[0], dict):
            print(f"Type: Structured (dict rows)")
            print(f"Rows: {len(table)}")
            print(f"Columns: {len(table[0]) if table else 0}")
            print(f"Headers: {list(table[0].keys())[:3]}...")
            print(f"\nFirst row sample:")
            first_row = table[0]
            for i, (k, v) in enumerate(first_row.items()):
                if i < 3:
                    print(f"  {k}: {v}")
                else:
                    break
        else:
            print(f"Type: List of lists (no headers)")
            print(f"Rows: {len(table)}")
            print(f"Cols: {len(table[0]) if table else 0}")
            print(f"First row: {table[0]}")
    else:
        print(f"Type: Empty table")

# Test PDF
print("\n" + "=" * 80)
print("PDF FILE TEST")
print("=" * 80)

pdf_json = converter.convert_pdf_to_json("multi_table_test.pdf")
pdf_data = json.loads(pdf_json)

print(f"\nTotal tables found in PDF: {len(pdf_data)}")

for idx, table in enumerate(pdf_data):
    print(f"\n{'='*40}")
    print(f"TABLE {idx + 1}")
    print(f"{'='*40}")
    
    if isinstance(table, list) and len(table) > 0:
        if isinstance(table[0], dict):
            print(f"Type: Structured (dict rows)")
            print(f"Rows: {len(table)}")
            print(f"Columns: {len(table[0]) if table else 0}")
            print(f"Headers: {list(table[0].keys())[:3]}...")
            print(f"\nFirst row sample:")
            first_row = table[0]
            for i, (k, v) in enumerate(first_row.items()):
                if i < 3:
                    print(f"  {k}: {v}")
                else:
                    break
        else:
            print(f"Type: List of lists (no headers)")
            print(f"Rows: {len(table)}")
            print(f"Cols: {len(table[0]) if table else 0}")
            print(f"First row: {table[0]}")
    else:
        print(f"Type: Empty table")

# Verification
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

print(f"\nHTML tables: {len(html_data)}")
print(f"PDF tables: {len(pdf_data)}")

if len(html_data) == len(pdf_data):
    print("[OK] Same number of tables in both formats")
else:
    print(f"[FAIL] Different number of tables: HTML={len(html_data)}, PDF={len(pdf_data)}")

# Detailed checks
print("\nDetailed checks:")
print(f"  HTML Table 1 (Simple): {len(html_data[0])} rows")
print(f"  HTML Table 2 (Merged): {len(html_data[1])} rows")
print(f"  HTML Table 3 (Complex): {len(html_data[2])} rows")
print(f"  HTML Table 4 (No headers): {len(html_data[3])} rows")

print(f"\n  PDF Table 1 (Simple): {len(pdf_data[0])} rows")
print(f"  PDF Table 2 (Merged): {len(pdf_data[1])} rows")
print(f"  PDF Table 3 (Complex): {len(pdf_data[2])} rows")
print(f"  PDF Table 4 (No headers): {len(pdf_data[3])} rows")
