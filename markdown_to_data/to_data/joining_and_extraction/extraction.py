from typing import List, Dict, Any, Text, Tuple
import re


class MarkdownExtractor:
    '''
    This class contains the functions to map a markdown based on its buildig blocks and return the final markdown data within a dicitonary.
    '''
    # TODO: Improve to detect additional top header rows

    # USED
    # TABLES
    def __parse_table(self, table_lines: List[Text]) -> List[Dict[str, Any]]:
        headers = []
        rows = []

        for i, line in enumerate(table_lines):
            # Remove leading/trailing whitespace and pipe characters
            line = line.strip().strip('|')
            cells = [cell.strip() for cell in line.split('|')]

            if i == 0:
                headers = cells  # First line is the header
            elif i == 1: # TODO: could be risky, when not detecting `-` explicitly
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

    # USED
    def _extract_md_table(self, markdown_snippet: Text) -> List[Dict[str, Any]]:
        '''
        Extracts a markdown table out of the given markdown text snippet.
        The first appearing markdown table is extracted while others are ignored.
        '''
        lines = markdown_snippet.splitlines()
        table_lines: List[Text] = []
        in_table: bool = False

        for line in lines:
            # Detect table lines that start with a '|'
            if line.startswith('|'):
                in_table = True
                table_lines.append(line)
            elif in_table:
                # If we hit a blank line or non-table line, end the table
                if not line.strip() or not line.startswith('|'):
                    break
                else:
                    table_lines.append(line)

        if table_lines:
            return self.__parse_table(table_lines)

        return []

    # USED
    # LISTS
    def _extract_md_list(self, markdown_snippet: Text) -> Dict[str, Any]:
        def get_indent_level(line: Text) -> int:
            return (len(line) - len(line.lstrip())) // 2

        def get_list_type(line: Text) -> Tuple[str, str]:
            line = line.lstrip()
            if re.match(r'^\d+[.)] ', line):
                return 'ol', line.split(' ', 1)[1]
            elif re.match(r'^[-+*] ', line):
                return 'ul', line.split(' ', 1)[1]
            return '', ''

        def parse_lines(lines: List[Tuple[Text, int, str]], current_indent: int = -1) -> List[Any]:
            result = []
            i = 0
            while i < len(lines):
                current_line, indent, content = lines[i]

                if indent <= current_indent:
                    break

                children = []
                j = i + 1
                while j < len(lines) and lines[j][1] > indent:
                    j += 1

                if j > i + 1:
                    child_items = parse_lines(lines[i+1:j], indent)
                    result.append({content: child_items})
                else:
                    result.append(content)

                i = j if j > i + 1 else i + 1

            return result

        # Process input text
        lines = markdown_snippet.strip().split('\n')
        processed_lines = []
        list_type = None
        empty_line_encountered = False

        # Collect valid list items with their properties, stop at first empty line
        for line in lines:
            if not line.strip():
                if processed_lines:  # Only set flag if we've already found list items
                    empty_line_encountered = True
                continue

            current_type, content = get_list_type(line.strip())
            if current_type:
                if empty_line_encountered:
                    # If we've seen an empty line and already have items, stop processing
                    break
                if not list_type:
                    list_type = current_type
                indent = get_indent_level(line)
                processed_lines.append((line, indent, content))

        if not processed_lines:
            return {}

        return {
            'type': list_type,
            'list': parse_lines(processed_lines)
        }


    # USED
    # CODE
    def _extract_md_code(self, markdown_snippet: str) -> Dict[str, Any]:
        '''
        Extracts a markdown code block out of the given markdown text snippet.
        The first appearing markdown code block is extracted while others are ignored.
        '''
        lines = markdown_snippet.splitlines()
        in_code_block = False
        code_block_lines = []
        potential_language = None
        code_block_found = False

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('```'):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    code_block_found = True
                    # Get potential language identifier
                    potential_language = stripped_line[3:].strip()
                    continue
                else:
                    # End of code block
                    break
            if in_code_block:
                code_block_lines.append(line)

        if code_block_found:  # Changed from if code_block_lines
            # Process the content
            # Find common indentation
            non_empty_lines = [line for line in code_block_lines if line.strip()]
            if non_empty_lines:
                min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                # Remove common indentation
                content = '\n'.join(line[min_indent:] if line.strip() else ''
                                  for line in code_block_lines).strip()
            else:
                content = ''

            # Validate language identifier
            if potential_language and re.match(r'^[a-zA-Z0-9+-]+$', potential_language):
                language = potential_language.lower()
            else:
                language = None
                if potential_language:
                    content = f"{potential_language}\n{content}"

            return {
                "language": language,
                "content": content
            }

        return {}

    # USED
    # BLOCKQUOTES
    def _extract_md_blockquote(self, markdown_text: Text) -> Dict[str, List[Any]]:
        '''
        Extracts the first appearing coherent markdown blockquote out of the given markdown text snippet.
        Returns a dictionary with nested structure representing blockquote hierarchy.
        '''
        def parse_lines(lines: List[Tuple[int, str]], current_level: int = 1) -> List[Any]:
            result = []
            i = 0
            while i < len(lines):
                level, content = lines[i]

                # Skip if this line belongs to a higher level
                if level < current_level:
                    break

                # Look ahead for children (higher levels)
                children = []
                j = i + 1
                while j < len(lines) and lines[j][0] > level:
                    children.append(lines[j])
                    j += 1

                if children:
                    # We have children, create nested structure
                    if len(children) == 1:
                        # Single child
                        result.append({content: [children[0][1]]})
                    else:
                        # Multiple children or deeper nesting
                        child_items = parse_lines(children, level + 1)
                        result.append({content: child_items})
                else:
                    # No children, add as simple string
                    result.append(content)

                i = j if children else i + 1

            return result

        # Process input text
        lines = markdown_text.split('\n')
        processed_lines = []
        in_blockquote = False

        # Collect blockquote lines with their levels
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('>'):
                in_blockquote = True
                # Count the number of '>' characters for level
                level = len(stripped_line) - len(stripped_line.lstrip('>'))
                # Extract content after '>' characters
                content = stripped_line.lstrip('>').strip()

                if content:  # Ignore empty blockquote lines
                    processed_lines.append((level, content))
            elif in_blockquote:
                # Stop at first non-blockquote line after blockquote started
                break

        if not processed_lines:
            return {}

        return {
            'blockquote': parse_lines(processed_lines)
        }

    # METADATA
    def _extract_metadata_kv(self, line: str) -> tuple[str | None, Any]:
        """Extract and process key-value pairs from metadata lines."""
        if not (match := re.match(r'^([^:]+):\s*(.*)?$', line)):
            return None, None

        # Process the key: replace multiple spaces with single underscore
        key = match.group(1).strip()
        key = re.sub(r'\s+', '_', key)

        value = match.group(2).strip() if match.group(2) else None

        if not value:
            return key, value

        # Process the value based on its format
        return key, self._process_metadata_value(value)

    def _process_metadata_value(self, value: str) -> Any:
        """Process metadata value to handle different list formats, quoted values, numbers, and booleans."""
        # Handle boolean values first
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False

        # Then try to convert single value to number if possible
        if not any(char in value for char in '[]()"\''):
            numeric_value = self._try_convert_to_number(value)
            if numeric_value is not None:
                return numeric_value

        # Check for bracketed or parentheses lists
        list_match = re.match(r'^\s*[\[\(](.*?)[\]\)]\s*$', value)

        if list_match:
            # Process content within brackets/parentheses
            return self._split_and_convert_numbers(list_match.group(1))

        # Check if the value contains commas and isn't entirely quoted
        if ',' in value and not (
            (value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))
        ):
            return self._split_and_convert_numbers(value)

        # Remove outer quotes if present
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        return value

    def _try_convert_to_number(self, value: str) -> Any:
        """Try to convert a string to int or float."""
        # Remove any whitespace
        value = value.strip()

        try:
            # First try converting to int
            if value.isdigit():
                return int(value)
            # Then try converting to float
            if '.' in value:
                return float(value)
        except ValueError:
            pass
        return None

    def _split_and_convert_numbers(self, value: str) -> List[Any]:
        """Split a string by commas and convert numeric values."""
        items = self._split_considering_quotes(value)
        converted_items = []

        for item in items:
            # Try converting each item to a number
            numeric_value = self._try_convert_to_number(item)
            if numeric_value is not None:
                converted_items.append(numeric_value)
            else:
                # If conversion fails, use the original string
                converted_items.append(item)

        return converted_items

    def _split_considering_quotes(self, value: str) -> List[str]:
        """Split a string by commas while respecting quoted values."""
        result = []
        current = []
        in_quotes = False
        quote_char = None

        for char in value:
            if char in '"\'':
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current.append(char)
            elif char == ',' and not in_quotes:
                if current:
                    result.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)

        if current:
            result.append(''.join(current).strip())

        # Process each item to remove unnecessary quotes
        return [
            item[1:-1] if (
                (item.startswith('"') and item.endswith('"')) or
                (item.startswith("'") and item.endswith("'"))
            ) else item
            for item in result
        ]
