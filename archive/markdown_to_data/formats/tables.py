import re
from typing import Text, List, Any, Dict, Union
import xml.etree.ElementTree as ET

# TABLES
# MD TO PYTHON 
def parse_table(table_lines: List[Text]) -> List[Dict[str, Any]]:
    headers = []
    rows = []

    for i, line in enumerate(table_lines):
        # Remove leading/trailing whitespace and pipe characters
        line = line.strip().strip('|')
        cells = [cell.strip() for cell in line.split('|')]
        
        if i == 0:
            headers = cells  # First line is the header
        elif i == 1:
            continue  # Second line is the separator row (---)
        else:
            rows.append(cells)  # All other lines are table rows

    table_data: List[Dict[str, Any]] = []
    for row in rows:
        row_dict: Dict[str, Any] = {}
        for j, header in enumerate(headers):
            if j < len(row):
                row_dict[header] = row[j] if row[j] else None
            else:
                row_dict[header] = None
        table_data.append(row_dict)

    return table_data

def extract_tables_from_markdown(markdown: Text) -> List[List[Dict[str, Any]]]:
    # Step 1: Split the content by lines
    lines = markdown.splitlines()

    # Step 2: Find all tables within the text
    tables: List[List[Dict[str, Any]]] = []
    table_lines: List[Text] = []
    in_table: bool = False

    for line in lines:
        # Detect table lines that start with a '|'
        if line.startswith('|'):
            in_table = True
            table_lines.append(line)
        # When in_table is True, collect all lines until a blank line or end
        elif in_table:
            if not line.strip():
                # End of table detected
                if table_lines:
                    tables.append(parse_table(table_lines))
                    table_lines.clear()
                in_table = False
            else:
                table_lines.append(line)

    # Handle the case where the markdown ends with a table
    if table_lines:
        tables.append(parse_table(table_lines))

    return tables


