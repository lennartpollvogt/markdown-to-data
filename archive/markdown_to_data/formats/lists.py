import re
from typing import Text, List, Any, Dict
import xml.etree.ElementTree as ET

# LISTS
# MD TO PYTHON
def extract_lists_from_markdown(markdown: str) -> Text:
    def is_list_item(line: str):
        """Check if a line is a list item (unordered or ordered)."""
        return bool(re.match(r'(\s*)[-+*] ', line)) or bool(re.match(r'(\s*)\d+(\.\d+)?[.)] ', line))
    
    def get_list_item_marker(line: str):
        """Extract the indentation and marker type."""
        unordered_match = re.match(r'(\s*)([-+*]) ', line)
        ordered_match = re.match(r'(\s*)(\d+(\.\d+)?)[.)] ', line)
        if unordered_match:
            return len(unordered_match.group(1))
        elif ordered_match:
            return len(ordered_match.group(1))
        return 0

    def parse_list(lines, index, current_indent):
        """Recursively parse list items and their nesting."""
        result = []
        while index < len(lines):
            line: str = lines[index]
            if is_list_item(line):
                indent = get_list_item_marker(line)
                content = line.strip().split(' ', 1)[1]  # Get content after the marker
                
                # If the current line is less or equally indented than the parent, stop nesting
                if indent <= current_indent:
                    return result, index

                # Check for nested lists
                next_index = index + 1
                nested_list = []
                if next_index < len(lines):
                    next_indent = get_list_item_marker(lines[next_index])
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
    lines = markdown.splitlines()

    # Store all extracted lists
    extracted_lists = []
    index = 0
    while index < len(lines):
        line = lines[index]
        
        if is_list_item(line):
            parsed_list, index = parse_list(lines, index, -1)
            extracted_lists.append(parsed_list)
        else:
            index += 1

    return extracted_lists

# PYTHON TO XML
def lists_to_xml(lists, root_tag="lists", list_tag="list", item_tag="item", sublist_tag="sublist", indent=None):
    # Create the root element
    root = ET.Element(root_tag)

    # Recursive function to parse lists and sublists
    def build_xml(parent, items):
        for item in items:
            if isinstance(item, list):
                # Check if any of the items in the list are lists (i.e., it's a sublist)
                if all(isinstance(i, list) for i in item):
                    # If all items are lists, treat it as a sublist
                    sublist = ET.SubElement(parent, sublist_tag)
                    build_xml(sublist, item)
                else:
                    # Handle regular list items
                    for sub_item in item:
                        if isinstance(sub_item, list):
                            # If the sub-item is a list, it's a sublist of this item
                            sublist = ET.SubElement(parent, sublist_tag)
                            build_xml(sublist, sub_item)
                        else:
                            # It's a regular item, not a sublist
                            item_element = ET.SubElement(parent, item_tag)
                            item_element.text = sub_item
            else:
                # Handle single string items (non-nested)
                item_element = ET.SubElement(parent, item_tag)
                item_element.text = item

    # Process the top-level lists
    for lst in lists:
        list_element = ET.SubElement(root, list_tag)
        build_xml(list_element, lst)

    # Function to prettify the XML with the specified indent
    def prettify_with_indent(elem, indent):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, encoding='unicode')
        from xml.dom import minidom
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent=" " * indent)

    # Convert the ElementTree to an XML string, with or without indent
    if indent is not None:
        return prettify_with_indent(root, indent)
    else:
        return ET.tostring(root, encoding='unicode', method='xml')