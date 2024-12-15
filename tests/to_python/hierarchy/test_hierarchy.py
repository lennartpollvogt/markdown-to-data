import pytest
from src.markdown_to_data.to_python.hierarchy.hierarchy import build_hierarchy_for_dict

@pytest.fixture
def basic_markdown_list():
    return [
        {
            'metadata': {
                'title': 'Test Document',
                'author': 'John Doe'
            }
        },
        {
            'header': {
                'level': 1,
                'content': 'Main Title'
            }
        },
        {'paragraph': 'Some text under main title'},
        {
            'header': {
                'level': 2,
                'content': 'Subsection'
            }
        },
        {'paragraph': 'Text in subsection'},
        {
            'table': {
                'headers': ['A', 'B'],
                'data': [[1, 2], [3, 4]]
            }
        }
    ]

@pytest.fixture
def complex_markdown_list():
    return [
        {
            'header': {
                'level': 1,
                'content': 'First H1'
            }
        },
        {'paragraph': 'Text under first H1'},
        {
            'header': {
                'level': 2,
                'content': 'H2 Section'
            }
        },
        {'paragraph': 'Text under H2'},
        {
            'header': {
                'level': 3,
                'content': 'H3 Section'
            }
        },
        {'paragraph': 'Deep nested text'},
        {
            'header': {
                'level': 2,
                'content': 'Second H2'
            }
        },
        {'paragraph': 'Text under second H2'},
        {
            'header': {
                'level': 1,
                'content': 'Second H1'
            }
        },
        {'paragraph': 'Final text'}
    ]

def test_basic_hierarchy():
    """Test basic hierarchy structure with metadata, headers, and content"""
    input_list = [
        {
            'metadata': {
                'title': 'Test'
            }
        },
        {
            'header': {
                'level': 1,
                'content': 'Title'
            }
        },
        {'paragraph': 'Text'}
    ]

    expected = {
        'metadata': {'title': 'Test'},
        'Title': {
            'paragraph_1': 'Text'
        }
    }

    result = build_hierarchy_for_dict(input_list)
    assert result == expected

def test_nested_headers():
    """Test nested header hierarchy"""
    input_list = [
        {
            'header': {
                'level': 1,
                'content': 'H1'
            }
        },
        {
            'header': {
                'level': 2,
                'content': 'H2'
            }
        },
        {
            'header': {
                'level': 3,
                'content': 'H3'
            }
        }
    ]

    expected = {
        'H1': {
            'H2': {
                'H3': {}
            }
        }
    }

    result = build_hierarchy_for_dict(input_list)
    assert result == expected

def test_multiple_elements_same_type(basic_markdown_list):
    """Test handling of multiple elements of the same type"""
    input_list = [
        {
            'header': {
                'level': 1,
                'content': 'Title'
            }
        },
        {'paragraph': 'First paragraph'},
        {'paragraph': 'Second paragraph'}
    ]

    expected = {
        'Title': {
            'paragraph_1': 'First paragraph',
            'paragraph_2': 'Second paragraph'
        }
    }

    result = build_hierarchy_for_dict(input_list)
    assert result == expected

def test_complete_document_structure(basic_markdown_list):
    """Test a complete document structure with metadata, headers, and various content types"""
    expected = {
        'metadata': {
            'title': 'Test Document',
            'author': 'John Doe'
        },
        'Main Title': {
            'paragraph_1': 'Some text under main title',
            'Subsection': {
                'paragraph_1': 'Text in subsection',
                'table_1': {
                    'headers': ['A', 'B'],
                    'data': [[1, 2], [3, 4]]
                }
            }
        }
    }

    result = build_hierarchy_for_dict(basic_markdown_list)
    assert result == expected

def test_complex_hierarchy(complex_markdown_list):
    """Test complex hierarchy with multiple levels and siblings"""
    expected = {
        'First H1': {
            'paragraph_1': 'Text under first H1',
            'H2 Section': {
                'paragraph_1': 'Text under H2',
                'H3 Section': {
                    'paragraph_1': 'Deep nested text'
                }
            },
            'Second H2': {
                'paragraph_1': 'Text under second H2'
            }
        },
        'Second H1': {
            'paragraph_1': 'Final text'
        }
    }

    result = build_hierarchy_for_dict(complex_markdown_list)
    assert result == expected

def test_empty_list():
    """Test handling of empty input"""
    result = build_hierarchy_for_dict([])
    assert result == {}

def test_skip_levels():
    """Test handling of skipped header levels (e.g., h1 to h3)"""
    input_list = [
        {
            'header': {
                'level': 1,
                'content': 'H1'
            }
        },
        {
            'header': {
                'level': 3,
                'content': 'H3'
            }
        }
    ]

    expected = {
        'H1': {
            'H3': {}
        }
    }

    result = build_hierarchy_for_dict(input_list)
    assert result == expected
