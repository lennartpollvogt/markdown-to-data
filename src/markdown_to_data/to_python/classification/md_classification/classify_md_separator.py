

def is_separator(line: str) -> bool:
    """Check if a line is a valid separator (---, ***, ___)."""
    # Check if there are no more than 3 leading spaces
    if len(line) - len(line.lstrip()) > 3:
        return False

    # Get the first non-space character
    stripped = line.lstrip()
    if not stripped:
        return False

    marker = stripped[0]
    if marker not in ('-', '*', '_'):
        return False

    # Count the markers
    marker_count = sum(1 for char in stripped if char == marker)
    if marker_count < 3:
        return False

    # Check if all non-space characters are the same marker
    return all(char == marker or char.isspace() for char in stripped)
