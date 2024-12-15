from typing import Dict, Any
import re

from .classify_md_paragraph import is_paragraph

def is_header_or_paragraph(stripped_line: str, line: str, indent: int) -> Dict[str, Any]:
    """Detect header line or paragraph."""
    match = re.match(r'^(#+)\s+(.*)', stripped_line)
    if match:
        level = len(match.group(1))
        header_text = match.group(2)
        if level > 6:
            return is_paragraph(line, indent)
        return {f'h{level}': header_text, 'indent': indent}
    return is_paragraph(line, indent)
