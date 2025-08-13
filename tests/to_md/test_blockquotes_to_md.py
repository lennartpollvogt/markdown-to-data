from src.markdown_to_data.to_md.md_elements.to_md_blockquotes import blockquote_data_to_md

def test_simple_blockquote():
    data = {
        'blockquote': [
            {'content': 'A simple blockquote', 'items': []}
        ]
    }
    expected = "> A simple blockquote"
    assert blockquote_data_to_md(data) == expected

def test_multiline_blockquote():
    data = {
        'blockquote': [
            {'content': 'First line', 'items': []},
            {'content': 'Second line', 'items': []},
            {'content': 'Third line', 'items': []}
        ]
    }
    expected = "> First line\n> Second line\n> Third line"
    assert blockquote_data_to_md(data) == expected

def test_nested_blockquote():
    data = {
        'blockquote': [
            {
                'content': 'Level one',
                'items': [
                    {
                        'content': 'Level two',
                        'items': [
                            {
                                'content': 'Level three',
                                'items': []
                            }
                        ]
                    }
                ]
            }
        ]
    }
    expected = "> Level one\n>> Level two\n>>> Level three"
    assert blockquote_data_to_md(data) == expected

def test_mixed_nesting_levels():
    data = {
        'blockquote': [
            {
                'content': 'First level',
                'items': [
                    {'content': 'Second level', 'items': []}
                ]
            },
            {
                'content': 'Back to first',
                'items': [
                    {'content': 'Deep level', 'items': []}
                ]
            }
        ]
    }
    expected = "> First level\n>> Second level\n> Back to first\n>> Deep level"
    assert blockquote_data_to_md(data) == expected

def test_empty_blockquote():
    data = {'blockquote': [{'content': '', 'items': []}]}
    expected = "> "
    assert blockquote_data_to_md(data) == expected

def test_invalid_input():
    data = {}
    expected = ""
    assert blockquote_data_to_md(data) == expected

def test_deeply_nested_blockquote():
    data = {
        'blockquote': [
            {'content': 'Five levels deep', 'items': []}
        ]
    }
    expected = "> Five levels deep"
    assert blockquote_data_to_md(data) == expected

def test_mixed_content_types():
    data = {
        'blockquote': [
            {'content': 'String', 'items': []},
            {'content': '123', 'items': []},    # number as string
            {'content': 'True', 'items': []}    # boolean as string
        ]
    }
    expected = "> String\n> 123\n> True"
    assert blockquote_data_to_md(data) == expected

# Additional test cases for the new structure
def test_multiple_nested_levels():
    data = {
        'blockquote': [
            {
                'content': 'First',
                'items': [
                    {
                        'content': 'Second',
                        'items': [
                            {'content': 'Third', 'items': []}
                        ]
                    },
                    {'content': 'Back to second', 'items': []}
                ]
            }
        ]
    }
    expected = "> First\n>> Second\n>>> Third\n>> Back to second"
    assert blockquote_data_to_md(data) == expected

def test_empty_nested_items():
    data = {
        'blockquote': [
            {
                'content': 'Main content',
                'items': []
            }
        ]
    }
    expected = "> Main content"
    assert blockquote_data_to_md(data) == expected
