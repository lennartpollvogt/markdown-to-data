from typing import Any, Dict, List, Tuple


def convert_cell_value(value: str) -> Any:
    """Convert cell value to appropriate type."""
    value = value.strip()
    if not value:
        return None

    # Try numeric conversion
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    return value


def is_separator_row(line: str) -> bool:
    """Check if a line is a table separator row (supports alignment markers)."""
    # Remove leading/trailing pipes and spaces
    cleaned = line.strip("| \t")
    if not cleaned:  # Empty line
        return False

    # Must contain at least one hyphen
    if "-" not in cleaned:
        return False

    # Split into cells and check each cell
    cells = [cell.strip() for cell in cleaned.split("|")]
    for cell in cells:
        if not cell:  # Empty cell in separator
            continue

        # Allow optional alignment markers ":" at start/end
        stripped = cell.strip()
        if stripped.startswith(":"):
            stripped = stripped[1:]
        if stripped.endswith(":"):
            stripped = stripped[:-1]

        # After removing alignment markers, allow only hyphens/spaces
        if not stripped or not all(c in "- " for c in stripped):
            return False

    return True


def split_table_cells(line: str) -> List[str]:
    """Split a table row into cells and clean whitespace.

    Pipes inside inline code (backticks) are not treated as cell separators.
    """
    cleaned = line.strip("|")
    if not cleaned:
        return []

    cells: List[str] = []
    current: List[str] = []
    in_code = False
    i = 0
    while i < len(cleaned):
        ch = cleaned[i]
        if ch == "`":
            in_code = not in_code
            current.append(ch)
        elif ch == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1

    cells.append("".join(current).strip())
    return cells


def is_table_row(line: str, is_header: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if line is a table row and return formatted dictionary.

    Args:
        line (str): The line to check
        is_header (bool): Whether this row should be treated as header

    Returns:
        Tuple[bool, Dict[str, Any]]: (is_table, row_data)
    """
    stripped_line = line.strip()
    indent = len(line) - len(line.lstrip())

    # Must contain at least one pipe
    if "|" not in line:
        return False, {}

    # Check if it's a separator row
    if is_separator_row(stripped_line):
        return True, {"tr": "table_separator", "indent": indent}

    # Split into cells
    cells = split_table_cells(stripped_line)
    if not cells:
        return False, {}

    # Create row dictionary
    row_dict = {"tr": {}, "indent": indent}
    cell_type = "th" if is_header else "td"

    # Handle single cell (merged columns)
    # if len(cells) == 1:
    # row_dict['tr'][cell_type] = convert_cell_value(cells[0])
    # else:
    # Multiple cells
    for i, cell in enumerate(cells):
        row_dict["tr"][f"{cell_type}_{i + 1}"] = convert_cell_value(cell)

    return True, row_dict
