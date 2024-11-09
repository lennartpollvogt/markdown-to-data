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
        '''
        Extracts a markdown list out of the given markdown text snippet.
        The first appearing coherent markdown list is extracted while others are ignored.
        '''
        def is_list_item(line: str):
            """Check if a line is a list item (unordered or ordered)."""
            return bool(re.match(r'(\s*)[-+*] ', line)) or bool(re.match(r'(\s*)\d+[.)] ', line))

        def get_list_item_marker(line: str):
            """Extract the indentation and marker type (unordered or ordered)."""
            unordered_match = re.match(r'(\s*)([-+*]) ', line)
            ordered_match = re.match(r'(\s*)(\d+[.)]) ', line)
            if unordered_match:
                return len(unordered_match.group(1)), 'ul'
            elif ordered_match:
                return len(ordered_match.group(1)), 'ol'
            return 0, None

        def parse_list(lines: List[str], index: int, current_indent: int) -> Tuple[List[Any], int]:
            """Recursively parse list items and their nesting."""
            result = []
            list_type = None

            while index < len(lines):
                line = lines[index].rstrip()

                # Stop if we encounter an empty line
                if not line:
                    break

                if is_list_item(line):
                    indent, current_list_type = get_list_item_marker(line)
                    content = line.strip().split(' ', 1)[1]

                    # Set list type for the first detected list item
                    if list_type is None:
                        list_type = current_list_type

                    # If the current line is less or equally indented than the parent, stop nesting
                    if indent <= current_indent:
                        return result, index

                    # Check for nested lists
                    next_index = index + 1
                    nested_list = []
                    if next_index < len(lines):
                        next_indent, _ = get_list_item_marker(lines[next_index])
                        if is_list_item(lines[next_index]) and next_indent > indent:
                            nested_list, next_index = parse_list(lines, next_index, indent)

                    if nested_list:
                        result.append([content, nested_list])
                    else:
                        result.append([content])
                    index = next_index
                else:
                    break

            return result, index

        # Split the markdown into lines
        lines = markdown_snippet.splitlines()

        # Extract the first coherent list
        index = 0
        while index < len(lines):
            line = lines[index].rstrip()

            # Skip empty lines at the start
            if not line:
                index += 1
                continue

            if is_list_item(line):
                parsed_list, _ = parse_list(lines, index, -1)
                _, list_type = get_list_item_marker(line)
                return {"type": list_type, "list": parsed_list}

            index += 1

        return {}


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
    def _extract_md_blockquote(self, markdown_text: Text) -> List[List[Text] | Any]:
        '''
        Extracts the first appearing coherent markdown blockquote out of the given markdown text snippet.
        '''
        # Step 1: Split all lines of the markdown and store each line into a list
        lines: List[Text] = markdown_text.split('\n')

        # Step 2: Extract only the first coherent blockquote and delete everything else from the list
        blockquote_lines: List[Text] = []
        in_blockquote: bool = False
        for line in lines:
            stripped_line: Text = line.strip()
            if stripped_line.startswith('>'):
                in_blockquote = True
                if stripped_line != '>':  # Ignore empty blockquote lines
                    blockquote_lines.append(stripped_line)
            elif in_blockquote:
                break

        # Step 3: Process the blockquote lines
        result_list: List[List[Text] | Any] = []
        for line in blockquote_lines:
            level = len(line) - len(line.lstrip('>'))  # Count the number of '>' characters
            content = line.strip().lstrip('>').strip()  # Remove '>' and surrounding whitespace

            if content:  # Ignore empty lines
                # Create nested lists based on the level
                nested_list = [content]
                for _ in range(level - 1):
                    nested_list = [nested_list]
                result_list.append(nested_list)

        return result_list

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
