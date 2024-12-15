from typing import Dict, Any

def is_paragraph(line: str, indent: int) -> Dict[str, Any]:
    """Create a paragraph dictionary entry."""
    return {'p': line, 'indent': indent}
