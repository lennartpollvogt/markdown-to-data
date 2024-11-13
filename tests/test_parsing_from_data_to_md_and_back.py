import pytest
from markdown_to_data import Markdown, to_md_parser

# Test data as fixture for reuse
@pytest.fixture
def example_data():
    return [
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

def test_markdown_conversion_and_parsing(example_data):
    # Test conversion from data to markdown
    markdown_string = to_md_parser(data=example_data, spacer=1)

    # Test parsing markdown back to data
    markdowner = Markdown(markdown=markdown_string)
    parsed_data = markdowner.md_list

    # Test conversion back to markdown
    markdown_string2 = markdowner.to_md()

    # Assertions
    assert parsed_data == example_data, "Parsed data should match original example"
    assert markdown_string == markdown_string2, "Generated markdown strings should match"

    # Test second markdown instance
    markdowner2 = Markdown(markdown=markdown_string).to_md()
    assert markdowner2 == markdown_string, "Second markdown conversion should match original"

    # Test JSON conversion
    json_output = markdowner.to_json()
    assert json_output is not None, "JSON conversion should not return None"

def test_index_based_inclusion(example_data):
    # Test including specific indices
    result = to_md_parser(data=example_data, include=[0, 1])
    markdowner = Markdown(result)
    assert len(markdowner.md_list) == 2, "Should only include two elements"
    assert 'metadata' in markdowner.md_list[0], "First element should be metadata"
    assert 'h1' in markdowner.md_list[1], "Second element should be h1"

def test_index_based_exclusion(example_data):
    # Test excluding specific indices
    result = to_md_parser(data=example_data, exclude=[2, 3])
    markdowner = Markdown(result)
    assert len(markdowner.md_list) == 3, "Should exclude two elements"
    assert 'paragraph' not in markdowner.md_elements, "Should not contain paragraph"
    assert 'h2' not in markdowner.md_elements, "Should not contain h2"

def test_mixed_inclusion(example_data):
    # Test including both types and indices
    result = to_md_parser(data=example_data, include=['h1', 0, 'list'])
    markdowner = Markdown(result)
    assert 'metadata' in markdowner.md_elements, "Should include metadata (index 0)"
    assert 'h1' in markdowner.md_elements, "Should include h1"
    assert 'list' in markdowner.md_elements, "Should include list"
    assert 'h2' not in markdowner.md_elements, "Should not include h2"

def test_mixed_exclusion(example_data):
    # Test excluding both types and indices
    result = to_md_parser(data=example_data, exclude=['h2', 2])
    markdowner = Markdown(result)
    assert 'h2' not in markdowner.md_elements, "Should not include h2"
    assert 'paragraph' not in markdowner.md_elements, "Should not include paragraph (index 2)"

def test_include_exclude_combination(example_data):
    # Test combining include and exclude
    result = to_md_parser(
        data=example_data,
        include=['h1', 'h2', 0, 4],
        exclude=['h2', 0]
    )
    markdowner = Markdown(result)
    assert 'metadata' not in markdowner.md_elements, "Should exclude metadata (index 0)"
    assert 'h1' in markdowner.md_elements, "Should include h1"
    assert 'h2' not in markdowner.md_elements, "Should exclude h2"
    assert 'list' in markdowner.md_elements, "Should include list (index 4)"

def test_edge_cases(example_data):
    # Test empty include list
    result1 = to_md_parser(data=example_data, include=[])
    assert result1 == "", "Empty include list should return empty string"

    # Test all indices out of range
    result2 = to_md_parser(data=example_data, include=[10, 11])
    assert result2 == "", "Out of range indices should return empty string"

    # Test invalid element types
    result3 = to_md_parser(data=example_data, include=['invalid_type'])
    assert len(Markdown(result3).md_list) == 0, "Invalid element types should be ignored"

    # Test exclude all
    result4 = to_md_parser(data=example_data, exclude=['all'])
    assert result4 == "", "Excluding 'all' should return empty string"

def test_spacer_with_filtered_content(example_data):
    # Test spacer with included indices
    result1 = to_md_parser(data=example_data, include=[0, 1], spacer=2)
    assert result1.count('\n\n\n') == 1, "Should have double spacing between elements"

    # Test spacer with excluded indices
    result2 = to_md_parser(data=example_data, exclude=[1, 2], spacer=0)
    assert '\n\n' not in result2, "Should have no extra spacing between elements"
