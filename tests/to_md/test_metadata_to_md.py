from src.markdown_to_data.to_md.md_elements.to_md_metadata import metadata_data_to_md

def test_basic_metadata():
    data = {
        'metadata': {
            'title': ['The', 'test', 'of', 'markdown-to-data'],
            'creation_date': '22.10.2024',
            'tags': ['python', 'markdown'],
            'last_modified': '04.11.2024'
        }
    }
    expected = (
        "---\n"
        "title: The, test, of, markdown-to-data\n"  # Note: simple list format
        "creation date: 22.10.2024\n"  # Note: underscore converted to space
        "tags: python, markdown\n"  # Note: simple list format
        "last modified: 04.11.2024\n"  # Note: underscore converted to space
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_empty_metadata():
    data = {'metadata': {}}
    assert metadata_data_to_md(data) == ''

def test_single_value_metadata():
    data = {
        'metadata': {
            'title': 'Simple Title'
        }
    }
    expected = (
        "---\n"
        "title: Simple Title\n"
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_urls():
    data = {
        'metadata': {
            'link': ['https://example.com', 'test', 'page'],
            'simple_url': 'https://example.com',
            'markdown': True,
            'JSON': True
        }
    }
    expected = (
        "---\n"
        'link: ["https://example.com", test, page]\n'
        'simple url: "https://example.com"\n'
        "markdown: True\n"
        "JSON: True\n"
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_special_characters():
    data = {
        'metadata': {
            'title': ['Special: Characters!', 'Test'],
            'tags': ['tag1', 'tag:2', 'tag#3']
        }
    }
    expected = (
        "---\n"
        'title: ["Special: Characters!", Test]\n'
        'tags: [tag1, "tag:2", "tag#3"]\n'
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_numbers():
    data = {
        'metadata': {
            'count': 42,
            'values': [1, 2, 3]
        }
    }
    expected = (
        "---\n"
        "count: 42\n"
        "values: 1, 2, 3\n"
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_mixed_types():
    data = {
        'metadata': {
            'title': ['Mixed', 'Types'],
            'number': 42,
            'tags': ['tag1', 'tag2'],
            'boolean': True
        }
    }
    expected = (
        "---\n"
        "title: Mixed, Types\n"
        "number: 42\n"
        "tags: tag1, tag2\n"
        "boolean: True\n"
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_numbers_and_decimals():
    data = {
        'metadata': {
            'number': 42,
            'numbers': [1, 4, 5, 6],
            'decimal': 71.5,
            'decimals': [1.2, 101.3, 45.34]
        }
    }
    expected = (
        "---\n"
        "number: 42\n"
        "numbers: 1, 4, 5, 6\n"
        "decimal: 71.5\n"
        "decimals: 1.2, 101.3, 45.34\n"
        "---"
    )
    assert metadata_data_to_md(data) == expected

def test_metadata_with_commas():
    data = {
        'metadata': {
            'description': 'This is a, complex description',
            'tags': ['web, development', 'python', 'markdown']
        }
    }
    expected = (
        "---\n"
        'description: "This is a, complex description"\n'
        'tags: ["web, development", python, markdown]\n'
        "---"
    )
    assert metadata_data_to_md(data) == expected
