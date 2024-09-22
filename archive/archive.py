'''
A bunch of helper functions (e.g. for transformation task from python dict to JSON, YAML or XML).
Avoids the Markdown class to get too big and lose overview.
'''

from typing import Text, List, Any, Dict


def extract_table_from_markdown(md_content: Text) -> List[Dict[str, Any]]:
    # Step 1: Split the content by lines
    lines = md_content.splitlines()
    
    # Step 2: Find the table within the text
    table_lines: List[Text] = []
    in_table: bool = False
    
    for line in lines:
        # Detect table lines that start with a '|'
        if line.startswith('|'):
            in_table = True
        # When in_table is True, collect all lines until a blank line or end
        if in_table:
            table_lines.append(line)
            # Exit table extraction when an empty line or non-table line is detected
            if not line.strip() or not line.startswith('|'):
                break
    
    if not table_lines:
        return "No table found in the markdown file."
    
    # Step 3: Parse the header and rows
    headers = []
    rows = []
    
    for i, line in enumerate(table_lines):
        # Clean line and split by '|'
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        
        if i == 0:
            headers = cells  # First line is the header
        elif i == 1:
            continue  # Second line is the separator row (---)
        else:
            rows.append(cells)  # All other lines are table rows
    
    # Step 4: Convert rows to list of dictionaries
    table_data: List[Dict[str, Any]] = []
    for row in rows:
        if len(row) == len(headers):
            row_dict = dict(zip(headers, row))
            table_data.append(row_dict)
    
    # Step 5: Return JSON
    return table_data