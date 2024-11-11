import pytest
from markdown_to_data import Markdown, to_md_parser

def test_markdown_conversion_and_parsing():
    # Test data
    example = [
        {
            'metadata': {
                'title': 'Test Document',
                'date': '2024-01-01',
                'boolean': True,
                'JSON': True
            }
        },
        {'h1': 'Main Title'},
        {'paragraph': 'Sample paragraph'},
        {'h2': 'Subtitle'},
        {'list': {
            'type': 'ul',
            'list': ['Item 1', 'Item 2']
        }}
    ]

    # Test conversion from data to markdown
    markdown_string = to_md_parser(data=example, spacer=1)

    # Test parsing markdown back to data
    markdowner = Markdown(markdown=markdown_string)
    parsed_data = markdowner.md_list

    # Test conversion back to markdown
    markdown_string2 = markdowner.to_md()

    # Assertions
    assert parsed_data == example, "Parsed data should match original example"
    assert markdown_string == markdown_string2, "Generated markdown strings should match"

    # Test second markdown instance
    markdowner2 = Markdown(markdown=markdown_string).to_md()
    assert markdowner2 == markdown_string, "Second markdown conversion should match original"

    # Test JSON conversion (if needed)
    json_output = markdowner.to_json()
    assert json_output is not None, "JSON conversion should not return None"
