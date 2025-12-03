from bs4 import BeautifulSoup
import json

class HTMLTableConverter:
    def __init__(self):
        pass

    def convert_to_json(self, html_content):
        """
        Parses HTML content, finds tables, and converts them to a JSON structure.
        Returns a list of tables, where each table is represented as a list of dictionaries (if headers exist)
        or a list of lists.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        results = []

        for table in tables:
            # Skip nested tables (they are processed within their parent table)
            if table.find_parent('table'):
                continue

            table_data = self._process_table(table)
            results.append(table_data)
        
        return json.dumps(results, indent=4)

    def _process_table(self, table):
        """
        Process a single table element handling rowspan, colspan, and nested tables.
        """
        # Collect rows only from the immediate table (exclude nested tables' rows)
        rows = []
        # Direct tr children
        rows.extend(table.find_all('tr', recursive=False))
        # tr children inside thead, tbody, tfoot
        for section in table.find_all(['thead', 'tbody', 'tfoot'], recursive=False):
            rows.extend(section.find_all('tr', recursive=False))
            
        if not rows:
            return []

        # 1. Determine grid dimensions and pre-fill
        # We can't easily know dimensions upfront without a pass, 
        # but we can grow the grid dynamically or do a sparse matrix approach.
        # A dictionary (row, col) -> value is easiest for sparse filling.
        grid = {}
        max_row = 0
        max_col = 0

        # We need to track skip offsets for rowspans from previous rows
        # skip_map: row_index -> set of col_indices that are occupied
        occupied_cells = set() # (row, col)

        current_row_idx = 0
        
        for tr in rows:
            current_col_idx = 0
            cells = tr.find_all(['td', 'th'], recursive=False)
            
            for cell in cells:
                # Skip columns that are already occupied by a rowspan from above
                while (current_row_idx, current_col_idx) in occupied_cells:
                    current_col_idx += 1
                
                # Get span attributes
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                
                # Handle nested tables or just text
                nested_tables = cell.find_all('table')
                if nested_tables:
                    # Recursively process nested tables
                    cell_data = []
                    for nt in nested_tables:
                        cell_data.append(self._process_table(nt))
                    
                    # If there's also text, we might want to include it, 
                    # but for structure, the table is usually the important part.
                    # Let's return the list of tables if multiple, or single if one.
                    if len(cell_data) == 1:
                        cell_value = cell_data[0]
                    else:
                        cell_value = cell_data
                else:
                    cell_value = cell.get_text(strip=True)
                
                # Fill the grid
                for r in range(rowspan):
                    for c in range(colspan):
                        r_idx = current_row_idx + r
                        c_idx = current_col_idx + c
                        grid[(r_idx, c_idx)] = cell_value
                        occupied_cells.add((r_idx, c_idx))
                        
                        max_row = max(max_row, r_idx)
                        max_col = max(max_col, c_idx)
                
                current_col_idx += colspan
            
            current_row_idx += 1

        # Convert grid to list of lists
        table_matrix = []
        for r in range(max_row + 1):
            row_data = []
            for c in range(max_col + 1):
                row_data.append(grid.get((r, c), ""))
            table_matrix.append(row_data)

        # Heuristic to determine if first row is header
        # If <thead> exists, use it.
        headers = []
        data_start_index = 0
        
        thead = table.find('thead', recursive=False)
        if thead:
            # If there is a thead, the rows inside it are headers.
            thead_rows = thead.find_all('tr', recursive=False)
            if thead_rows:
                # Use the first row of thead as headers for simplicity
                # (Complex multi-row headers are hard to map to simple JSON dict keys without flattening)
                # We grab the first row from our matrix which corresponds to the first row of thead
                if len(table_matrix) > 0:
                    headers = table_matrix[0]
                    data_start_index = len(thead_rows)
        else:
            # No explicit thead. Check if first row is all <th>
            if rows:
                first_tr = rows[0]
                if all(c.name == 'th' for c in first_tr.find_all(['td', 'th'], recursive=False)):
                    if len(table_matrix) > 0:
                        headers = table_matrix[0]
                        data_start_index = 1

        if headers:
            # Create list of dicts
            json_data = []
            # Handle duplicate headers?
            unique_headers = self._make_unique(headers)
            
            for i in range(data_start_index, len(table_matrix)):
                row = table_matrix[i]
                record = {}
                # Zip will stop at the shortest list. 
                # If row is longer than headers, extra data is lost.
                # If row is shorter, we miss keys.
                # Let's ensure we capture everything we can.
                for h_idx, h in enumerate(unique_headers):
                    if h_idx < len(row):
                        record[h] = row[h_idx]
                    else:
                        record[h] = None # or ""
                json_data.append(record)
            return json_data
        else:
            # Return list of lists if no headers detected
            return table_matrix

    def _make_unique(self, headers):
        seen = {}
        new_headers = []
        for h in headers:
            if h in seen:
                seen[h] += 1
                new_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 0
                new_headers.append(h)
        return new_headers

if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python html_table_converter.py <path_to_html_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    converter = HTMLTableConverter()
    json_output = converter.convert_to_json(html_content)
    print(json_output)
