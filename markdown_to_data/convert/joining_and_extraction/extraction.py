from typing import List, Dict, Any, Text
import re


class MarkdownExtractor:
    '''
    This class contains the functions to map a markdown based on its buildig blocks and return the final markdown data within a dicitonary.
    '''
    # TODO: Improve to detect additional top header rows
    # USED
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

        def parse_list(lines: List[str], index: int, current_indent: int) -> List[Any]:
            """Recursively parse list items and their nesting."""
            result = []
            list_type = None

            while index < len(lines):
                line = lines[index]
                if is_list_item(line):
                    indent, current_list_type = get_list_item_marker(line)
                    content = line.strip().split(' ', 1)[1]  # Get content after the marker

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
                    # Stop if we encounter a non-list item (e.g., a paragraph or empty line)
                    if line.strip() == "" or not is_list_item(line):
                        break
                    index += 1
            return result, index

        # Split the markdown into lines
        lines = markdown_snippet.splitlines()

        # Extract the first coherent list
        index = 0
        while index < len(lines):
            line = lines[index]

            if is_list_item(line):
                parsed_list, _ = parse_list(lines, index, -1)
                _, list_type = get_list_item_marker(line)
                return {"type": list_type, "list": parsed_list}
            index += 1

        return {}


    # USED
    def _extract_md_code(self, markdown_snippet: str) -> Dict[str, Any]:
        '''
        Extracts a markdown code block out of the given markdown text snippet.
        The first appearing markdown code block is extracted while others are ignored.
        '''
        # Regular expression to match code blocks
        pattern = r'^\s*```\s*([^"\n]+)?\s*\n(.*?)^\s*```$'

        pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)

        match = pattern.search(markdown_snippet)

        if match:
            language = match.group(1).strip() if match.group(1) else None
            content = match.group(2).rstrip()

            # Check if the language is actually part of the content
            if language and language.startswith('#'):
                language = None
                content = f"{match.group(1)}\n{content}"

            return {
                "language": language.lower() if language else None,
                "content": content
            }

        return {}

    # USED
    def _extract_md_blockquote(self, markdown_text: Text) -> List[List[Text]]:
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
        result_list: List[Text] = []
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

    def _extract_metadata_kv(self, line: str) -> tuple[str | None , str | None]:
        """Extract key-value pairs from metadata lines."""
        if match := re.match(r'^([^:]+):\s*(.*)?$', line):
            key = match.group(1).strip()
            value = match.group(2).strip() if match.group(2) else None
            return key, value
        return None, None
