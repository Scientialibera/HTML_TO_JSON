from bs4 import BeautifulSoup
import json
import pdfplumber
from typing import List, Dict, Any, Tuple

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

    def convert_pdf_to_json(self, pdf_path, use_native_json=True):
        """
        Extracts tables from a PDF file and converts them to JSON.
        
        Args:
            pdf_path: Path to the PDF file
            use_native_json: If True, uses pdfplumber's native JSON extraction
                           If False, uses extract_tables() method
        
        Returns:
            A JSON string representing a list of tables
        """
        results = []
        
        if use_native_json:
            # Use pdfplumber's native JSON extraction
            with pdfplumber.open(pdf_path) as pdf:
                # Extract raw PDF JSON
                pdf_json_str = pdf.to_json()
                pdf_data = json.loads(pdf_json_str)
                
                # Process each page
                for page_data in pdf_data.get('pages', []):
                    page_tables = self._extract_tables_from_pdf_json(page_data)
                    results.extend(page_tables)
        else:
            # Use pdfplumber's extract_tables() method (original approach)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    if not tables:
                        continue
                    
                    for table in tables:
                        if not table or len(table) == 0:
                            continue
                        
                        processed_table = self._process_pdf_table(table)
                        results.append(processed_table)
        
        return json.dumps(results, indent=4)

    def _process_pdf_table(self, table):
        """
        Process a table extracted from PDF (already a list of lists).
        Detect headers and convert to dict format if possible.
        Intelligently merges multi-row headers into composite column names.
        """
        if not table or len(table) == 0:
            return []
        
        # Clean up None values and whitespace
        cleaned_table = []
        for row in table:
            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
            cleaned_table.append(cleaned_row)
        
        # Assume first row is header, check if it's a multi-row header
        if len(cleaned_table) > 1:
            # Detect if we have a multi-row header by checking if second row looks like sub-headers
            header_row_count = 1
            
            # Check if first row contains mostly empty or merged-cell remnants
            first_row_empty_count = sum(1 for cell in cleaned_table[0] if not cell or cell == "")
            second_row_empty_count = sum(1 for cell in cleaned_table[1] if not cell or cell == "")
            
            # Simple heuristic: if second row has more non-empty values and none are repeating
            # category names, it's likely a sub-header row (like years)
            if (len(cleaned_table) > 2 and 
                second_row_empty_count < first_row_empty_count and
                second_row_empty_count < len(cleaned_table[1]) * 0.5):
                header_row_count = 2
            
            header_rows = cleaned_table[:header_row_count]
            data_rows = cleaned_table[header_row_count:]
            
            # Merge multi-row headers
            headers = self._merge_header_rows(header_rows)
            unique_headers = self._make_unique(headers)
            
            json_data = []
            for row in data_rows:
                record = {}
                for h_idx, h in enumerate(unique_headers):
                    if h_idx < len(row):
                        record[h] = row[h_idx]
                    else:
                        record[h] = None
                json_data.append(record)
            return json_data
        else:
            # Return as list of lists if only one row
            return cleaned_table

        return json.dumps(results, indent=4)

    def _extract_tables_from_pdf_json(self, page_data: Dict[str, Any]) -> List[List[Dict]]:
        """
        Extract table structures from pdfplumber's native JSON output.
        Uses chars positioned in a grid pattern to identify tables.
        """
        chars = page_data.get('chars', [])
        
        if not chars:
            return []
        
        # Try character-based grid extraction (most reliable for PDFs)
        return self._extract_tables_by_character_grid(chars)

    def _detect_table_regions(self, rects: List[Dict], lines: List[Dict]) -> List[Dict]:
        """
        Detect table regions using rectangles and lines in the PDF.
        Returns a list of bounding boxes for detected tables.
        """
        if not rects and not lines:
            return []
        
        # Collect all boundary coordinates
        boundaries = []
        
        # Add rect boundaries
        for rect in rects:
            boundaries.append({
                'x0': rect['x0'],
                'y0': rect['y0'],
                'x1': rect['x1'],
                'y1': rect['y1'],
                'type': 'rect'
            })
        
        # Add line boundaries (useful for detecting cell divisions)
        for line in lines:
            if 'x0' in line and 'y0' in line and 'x1' in line and 'y1' in line:
                # Approximate line as thin rectangle
                if line['x0'] == line['x1']:  # Vertical line
                    boundaries.append({
                        'x0': line['x0'] - 1,
                        'y0': min(line['y0'], line['y1']),
                        'x1': line['x0'] + 1,
                        'y1': max(line['y0'], line['y1']),
                        'type': 'line'
                    })
                elif line['y0'] == line['y1']:  # Horizontal line
                    boundaries.append({
                        'x0': min(line['x0'], line['x1']),
                        'y0': line['y0'] - 1,
                        'x1': max(line['x0'], line['x1']),
                        'y1': line['y0'] + 1,
                        'type': 'line'
                    })
        
        # Group overlapping/nearby boundaries to find tables
        tables = []
        if boundaries:
            # Simple approach: find bounding box of all boundaries (indicates table region)
            all_x0 = [b['x0'] for b in boundaries]
            all_y0 = [b['y0'] for b in boundaries]
            all_x1 = [b['x1'] for b in boundaries]
            all_y1 = [b['y1'] for b in boundaries]
            
            if all_x0 and all_y0:
                # Create one large table region
                table_region = {
                    'x0': min(all_x0),
                    'y0': min(all_y0),
                    'x1': max(all_x1),
                    'y1': max(all_y1)
                }
                tables.append(table_region)
        
        return tables

    def _extract_table_from_region(self, chars: List[Dict], region: Dict) -> List[List]:
        """
        Extract characters within a table region and organize them into a grid.
        """
        # Filter characters within region
        region_chars = [c for c in chars 
                       if region['x0'] <= c.get('x0', 0) <= region['x1'] and
                          region['y0'] <= c.get('top', 0) <= region['y1']]
        
        if not region_chars:
            return []
        
        # Sort characters by position (top-left to bottom-right)
        sorted_chars = sorted(region_chars, key=lambda c: (c.get('top', 0), c.get('x0', 0)))
        
        # Group characters into rows (based on y-coordinate)
        rows = self._group_characters_into_rows(sorted_chars)
        
        # Group row characters into cells (based on x-coordinate)
        table = []
        for row_chars in rows:
            cells = self._group_characters_into_cells(row_chars)
            row_data = [''.join(c['text'] for c in cell).strip() for cell in cells]
            table.append(row_data)
        
        # Process into structured format with headers
        if table:
            return self._process_pdf_table(table)
        
        return []

    def _extract_tables_by_character_grid(self, chars: List[Dict]) -> List[List]:
        """
        Fallback method: Extract tables by analyzing character positioning directly.
        Groups characters into a grid based on their x/y coordinates.
        """
        if not chars:
            return []
        
        # Sort by position
        sorted_chars = sorted(chars, key=lambda c: (c.get('top', 0), c.get('x0', 0)))
        
        # Group into rows
        rows = self._group_characters_into_rows(sorted_chars)
        
        # Group into cells and reconstruct table
        table = []
        for row_chars in rows:
            cells = self._group_characters_into_cells(row_chars)
            row_data = [''.join(c['text'] for c in cell).strip() for cell in cells]
            table.append(row_data)
        
        # Filter out likely non-table content (single-column or very short)
        if len(table) > 2:
            table_data = self._process_pdf_table(table)
            return [table_data] if table_data else []
        
        return []

    def _group_characters_into_rows(self, chars: List[Dict], row_threshold: float = 5) -> List[List[Dict]]:
        """
        Group characters into rows based on their vertical position (top coordinate).
        """
        if not chars:
            return []
        
        rows = []
        current_row = [chars[0]]
        current_top = chars[0].get('top', 0)
        
        for char in chars[1:]:
            char_top = char.get('top', 0)
            # If character is within threshold of current row, add to row
            if abs(char_top - current_top) <= row_threshold:
                current_row.append(char)
            else:
                rows.append(current_row)
                current_row = [char]
                current_top = char_top
        
        if current_row:
            rows.append(current_row)
        
        return rows

    def _group_characters_into_cells(self, chars: List[Dict], cell_threshold: float = 10) -> List[List[Dict]]:
        """
        Group characters into cells based on their horizontal position (x0 coordinate).
        """
        if not chars:
            return []
        
        # Sort by x position
        sorted_chars = sorted(chars, key=lambda c: c.get('x0', 0))
        
        cells = []
        current_cell = [sorted_chars[0]]
        current_x = sorted_chars[0].get('x0', 0)
        
        for char in sorted_chars[1:]:
            char_x = char.get('x0', 0)
            # If character is close to current cell, add to cell
            if abs(char_x - current_x) <= cell_threshold:
                current_cell.append(char)
            else:
                cells.append(current_cell)
                current_cell = [char]
                current_x = char_x
        
        if current_cell:
            cells.append(current_cell)
        
        return cells

    def _process_table(self, table):
        """
        Process a single table element handling rowspan, colspan, and nested tables.
        Intelligently merges multi-row headers into composite column names.
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
        grid = {}
        max_row = 0
        max_col = 0
        occupied_cells = set()
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
                    cell_data = []
                    for nt in nested_tables:
                        cell_data.append(self._process_table(nt))
                    
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

        # Detect header rows and data start
        headers = []
        data_start_index = 0
        
        thead = table.find('thead', recursive=False)
        if thead:
            thead_rows = thead.find_all('tr', recursive=False)
            if thead_rows:
                # Extract header rows from matrix
                header_row_count = len(thead_rows)
                header_rows = table_matrix[:header_row_count]
                data_start_index = header_row_count
                
                # Merge multi-row headers
                headers = self._merge_header_rows(header_rows)
        else:
            # No explicit thead. Check if first row is all <th>
            if rows:
                first_tr = rows[0]
                if all(c.name == 'th' for c in first_tr.find_all(['td', 'th'], recursive=False)):
                    # Single row header
                    headers = table_matrix[0]
                    data_start_index = 1
                    
                    # Check if second row is also all <th> (multi-row header)
                    if len(rows) > 1:
                        second_tr = rows[1]
                        if all(c.name == 'th' for c in second_tr.find_all(['td', 'th'], recursive=False)):
                            # Multi-row header detected
                            header_rows = table_matrix[:2]
                            headers = self._merge_header_rows(header_rows)
                            data_start_index = 2

        if headers:
            # Create list of dicts
            json_data = []
            unique_headers = self._make_unique(headers)
            
            for i in range(data_start_index, len(table_matrix)):
                row = table_matrix[i]
                record = {}
                for h_idx, h in enumerate(unique_headers):
                    if h_idx < len(row):
                        record[h] = row[h_idx]
                    else:
                        record[h] = None
                json_data.append(record)
            return json_data
        else:
            # Return list of lists if no headers detected
            return table_matrix

    def _merge_header_rows(self, header_rows):
        """
        Merge multiple header rows into composite column names.
        For example, ["Category", "Year1"] + ["", "1989"] -> "Category Year1 - 1989"
        """
        if len(header_rows) == 1:
            return header_rows[0]
        
        if len(header_rows) < 1:
            return []
        
        num_cols = max(len(row) for row in header_rows) if header_rows else 0
        merged_headers = []
        
        for col_idx in range(num_cols):
            # Collect all non-empty values in this column across all header rows
            col_values = []
            for row_idx, row in enumerate(header_rows):
                if col_idx < len(row):
                    val = str(row[col_idx]).strip()
                    if val:  # Only add non-empty values
                        col_values.append(val)
            
            # Join them with " - " separator
            merged_header = " - ".join(col_values) if col_values else ""
            merged_headers.append(merged_header)
        
        return merged_headers

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
        print("Usage: python html_table_converter.py <path_to_file>")
        print("  Supported formats: .html, .pdf")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    converter = HTMLTableConverter()
    
    # Determine file type
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        json_output = converter.convert_pdf_to_json(file_path)
    elif ext in ['.html', '.htm']:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        json_output = converter.convert_to_json(html_content)
    else:
        print(f"Error: Unsupported file format '{ext}'. Supported: .html, .pdf")
        sys.exit(1)
    
    print(json_output)
