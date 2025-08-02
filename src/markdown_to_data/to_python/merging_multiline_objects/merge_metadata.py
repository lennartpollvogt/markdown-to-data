from typing import List, Dict, Any, Tuple
import re
from .line_utils import calculate_line_range, add_line_range_to_element

def _is_separator(item: Dict[str, Any]) -> bool:
    """Check if an item is a separator."""
    return 'separator' in item

def _is_paragraph(item: Dict[str, Any]) -> bool:
    """Check if an item is a paragraph."""
    return 'paragraph' in item

def _is_empty_paragraph(item: Dict[str, Any]) -> bool:
    """Check if an item is an empty paragraph."""
    return _is_paragraph(item) and not item['paragraph'].strip()

def _get_separator_type(item: Dict[str, Any]) -> str | None:
    """Get the separator type if item is a separator."""
    return item.get('separator') if _is_separator(item) else None

def _is_valid_key_value_pair(text: str) -> Tuple[bool, Tuple[str, str] | None]:
    """
    Check if a string is a valid key-value pair and return the parsed parts.
    Returns (is_valid, (key, value)) or (is_valid, None)
    """
    if ':' not in text:
        return False, None

    key, value = text.split(':', 1)
    key = key.strip()

    if not key:  # Empty key is invalid
        return False, None

    return True, (key, value.strip())

def _normalize_key(key: str) -> str:
    """Normalize metadata key by converting spaces to underscores."""
    return re.sub(r'\s+', '_', key.strip())

def _parse_list_value(value: str) -> List[Any]:
    """Parse a string value into a list, handling various formats."""
    # Remove brackets or parentheses if present
    value = value.strip()
    if value.startswith(('[', '(')) and value.endswith((']', ')')):
        value = value[1:-1]

    # Split by commas, but preserve commas in quotes
    items = []
    current_item = []
    in_quotes = False
    quote_char = None

    for char in value + ',':  # Add comma to handle last item
        if char in '"\'':
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            else:
                current_item.append(char)
        elif char == ',' and not in_quotes:
            items.append(''.join(current_item).strip())
            current_item = []
        else:
            current_item.append(char)

    # Filter out empty items and process each item
    return [_parse_single_value(item.strip()) for item in items if item.strip()]

def _parse_single_value(value: str) -> Any:
    """Parse a single value into its appropriate type."""
    value = value.strip()

    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Check for boolean
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False

    # Check for None
    if not value:
        return None

    # Check for number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    return value

def _parse_metadata_value(value: str) -> Any:
    """Parse metadata value into appropriate type."""
    value = value.strip()

    # Check if it's a list format
    if value.startswith(('[', '(')) and value.endswith((']', ')')):
        return _parse_list_value(value)

    # Check if it's a comma-separated list
    if ',' in value and not (value.startswith('"') or value.startswith("'")):
        return _parse_list_value(value)

    return _parse_single_value(value)

def _validate_metadata_block(items: List[Dict[str, Any]]) -> bool:
    """Validate that the metadata block is properly formed."""
    if not items:
        return False

    # Find first non-empty paragraph
    start_idx = 0
    while start_idx < len(items) and _is_empty_paragraph(items[start_idx]):
        start_idx += 1

    if start_idx >= len(items) or not _is_separator(items[start_idx]):
        return False

    # Get separator type
    separator_type = _get_separator_type(items[start_idx])

    # Find matching end separator
    end_idx = start_idx + 1
    while end_idx < len(items):
        if _is_separator(items[end_idx]):
            if _get_separator_type(items[end_idx]) != separator_type:
                return False
            break
        end_idx += 1
    else:
        return False

    # Validate content between separators
    for item in items[start_idx + 1:end_idx]:
        if not _is_paragraph(item):
            return False
        if not _is_empty_paragraph(item):
            is_valid, _ = _is_valid_key_value_pair(item['paragraph'])
            if not is_valid:
                return False

    return True

def merge_metadata(classified_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and merge metadata blocks in markdown content.
    Returns the original list if metadata is malformed.
    Keeps all content after the metadata block.
    """
    if not _validate_metadata_block(classified_list):
        return classified_list

    # Find metadata block boundaries
    start_idx = 0
    while start_idx < len(classified_list) and _is_empty_paragraph(classified_list[start_idx]):
        start_idx += 1

    end_idx = start_idx + 1
    while end_idx < len(classified_list) and not _is_separator(classified_list[end_idx]):
        end_idx += 1

    # Process metadata content
    metadata = {}
    for item in classified_list[start_idx + 1:end_idx]:
        if not _is_empty_paragraph(item):
            is_valid, kv_pair = _is_valid_key_value_pair(item['paragraph'])
            if is_valid and kv_pair is not None:
                key, value = kv_pair
                normalized_key = _normalize_key(key)
                parsed_value = _parse_metadata_value(value)
                metadata[normalized_key] = parsed_value

    # Calculate line range for metadata block
    metadata_elements = classified_list[start_idx:end_idx + 1]  # Include both separators
    start_line, end_line = calculate_line_range(metadata_elements)

    # Combine metadata with remaining content
    metadata_element = {'metadata': metadata}
    add_line_range_to_element(metadata_element, start_line, end_line)
    result = [metadata_element]

    # Add all content after the metadata block
    if end_idx + 1 < len(classified_list):
        result.extend(classified_list[end_idx + 1:])

    return result
