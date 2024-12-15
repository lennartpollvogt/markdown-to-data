from src.markdown_to_data.to_python.merging_multiline_objects.merge_metadata import merge_metadata

def test_basic_metadata():
    """Test basic metadata with simple key-value pairs (Example 1)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title: Test Document'},
        {'paragraph': 'author: John Doe'},
        {'paragraph': 'date: 2024-01-15'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': 'Test Document',
                'author': 'John Doe',
                'date': '2024-01-15'
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_spaces():
    """Test metadata with spaces in values and keys (Example 2)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title: This is a longer title with spaces'},
        {'paragraph': 'created by: John Doe'},
        {'paragraph': 'last modified: 2024-01-15'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': 'This is a longer title with spaces',
                'created_by': 'John Doe',
                'last_modified': '2024-01-15'
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_special_characters():
    """Test metadata with hyphens and multiple spaces (Example 3)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title: This is a longer title with spaces'},
        {'paragraph': 'created-by: John Doe'},
        {'paragraph': 'last    modified: 2024-01-15'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': 'This is a longer title with spaces',
                'created-by': 'John Doe',
                'last_modified': '2024-01-15'
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_empty_metadata_values():
    """Test metadata with empty values (Example 4)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title:'},
        {'paragraph': 'author:'},
        {'paragraph': 'date:'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': None,
                'author': None,
                'date': None
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_special_values():
    """Test metadata with time, URL values (Example 5)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title: Understanding Time: A Brief History'},
        {'paragraph': 'time: 15:30'},
        {'paragraph': 'url: https://example.com'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': 'Understanding Time: A Brief History',
                'time': '15:30',
                'url': 'https://example.com'
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_lists():
    """Test metadata with comma-separated lists (Example 6)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'keywords: python, markdown, parser'},
        {'paragraph': 'authors: John Doe, Jane Smith, Bob Johnson'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'keywords': ['python', 'markdown', 'parser'],
                'authors': ['John Doe', 'Jane Smith', 'Bob Johnson']
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_mixed_types():
    """Test metadata with various data types (Example 7)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'title: Test Document'},
        {'paragraph': 'tags: [python, testing]'},
        {'paragraph': 'contributors: (John Doe, Jane Smith)'},
        {'paragraph': 'keywords: markdown, parser, data'},
        {'paragraph': 'version: 1.0.0'},
        {'paragraph': 'boolean: True'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'title': 'Test Document',
                'tags': ['python', 'testing'],
                'contributors': ['John Doe', 'Jane Smith'],
                'keywords': ['markdown', 'parser', 'data'],
                'version': '1.0.0',
                'boolean': True
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_quoted_values():
    """Test metadata with quoted values (Example 8)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'description: "This is a, complex description"'},
        {'paragraph': "quote: 'Single quoted, value with commas'"},
        {'paragraph': 'quote2: "Double quoted, value with commas"'},
        {'paragraph': 'tags: [python, "web, development", testing]'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'description': 'This is a, complex description',
                'quote': 'Single quoted, value with commas',
                'quote2': 'Double quoted, value with commas',
                'tags': ['python', 'web, development', 'testing']
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_metadata_with_numbers():
    """Test metadata with numeric values (Example 9)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'number: 1'},
        {'paragraph': 'numbers: 1,2,3, 4'},
        {'paragraph': 'decimal: 1.4'},
        {'paragraph': 'deciamals: [11.333, 4.6, 7.3]'},
        {'paragraph': 'wrong_decimal: 1,2'},
        {'separator': '---'}
    ]

    expected = [
        {
            'metadata': {
                'number': 1,
                'numbers': [1, 2, 3, 4],
                'decimal': 1.4,
                'deciamals': [11.333, 4.6, 7.3],
                'wrong_decimal': [1, 2]
            }
        }
    ]

    assert merge_metadata(input_data) == expected

def test_malformed_metadata():
    """Test metadata with numeric values (Example 9)"""
    input_data = [
        {'separator': '---'},
        {'paragraph': 'number 1'},
        {'paragraph': 'numbers 1,2,3, 4'},
        {'paragraph': 'decimal: 1.4'},
        {'paragraph': 'deciamals [11.333, 4.6, 7.3]'},
        {'paragraph': 'wrong_decimal: 1,2'},
        {'separator': '---'}
    ]

    expected = [
        {'separator': '---'},
        {'paragraph': 'number 1'},
        {'paragraph': 'numbers 1,2,3, 4'},
        {'paragraph': 'decimal: 1.4'},
        {'paragraph': 'deciamals [11.333, 4.6, 7.3]'},
        {'paragraph': 'wrong_decimal: 1,2'},
        {'separator': '---'}
    ]

    assert merge_metadata(input_data) == expected
