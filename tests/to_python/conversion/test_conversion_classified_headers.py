from src.markdown_to_data.to_python.convert_single_line_objects.convert_headers import convert_headers

def test_single_h1():
    input_data = [
        {'h1': 'Main Header', 'indent': 0}
    ]

    expected = [
        {
            'header': {
                'level': 1,
                'content': 'Main Header'
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert convert_headers(input_data) == expected

def test_all_header_levels():
    input_data = [
        {'h1': 'Header 1', 'indent': 0},
        {'h2': 'Header 2', 'indent': 0},
        {'h3': 'Header 3', 'indent': 0},
        {'h4': 'Header 4', 'indent': 0},
        {'h5': 'Header 5', 'indent': 0},
        {'h6': 'Header 6', 'indent': 0}
    ]

    expected = [
        {'header': {'level': 1, 'content': 'Header 1'}, 'start_line': 0, 'end_line': 0},
        {'header': {'level': 2, 'content': 'Header 2'}, 'start_line': 0, 'end_line': 0},
        {'header': {'level': 3, 'content': 'Header 3'}, 'start_line': 0, 'end_line': 0},
        {'header': {'level': 4, 'content': 'Header 4'}, 'start_line': 0, 'end_line': 0},
        {'header': {'level': 5, 'content': 'Header 5'}, 'start_line': 0, 'end_line': 0},
        {'header': {'level': 6, 'content': 'Header 6'}, 'start_line': 0, 'end_line': 0}
    ]

    assert convert_headers(input_data) == expected

def test_mixed_content():
    input_data = [
        {'h1': 'Title', 'indent': 0},
        {'p': 'Some text'},
        {'h2': 'Subtitle', 'indent': 0},
        {'p': 'More text'}
    ]

    expected = [
        {'header': {'level': 1, 'content': 'Title'}, 'start_line': 0, 'end_line': 0},
        {'p': 'Some text'},
        {'header': {'level': 2, 'content': 'Subtitle'}, 'start_line': 0, 'end_line': 0},
        {'p': 'More text'}
    ]

    assert convert_headers(input_data) == expected

def test_no_headers():
    input_data = [
        {'p': 'paragraph 1'},
        {'hr': '---'},
        {'p': 'paragraph 2'}
    ]

    expected = input_data.copy()

    assert convert_headers(input_data) == expected

def test_empty_input():
    input_data = []
    expected = []
    assert convert_headers(input_data) == expected

def test_example_from_docstring():
    input_data = [
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a h1 header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'p': '', 'indent': 0},
        {'h2': 'Header level 2', 'indent': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a separator', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    expected = [
        {'header': {'level': 1, 'content': 'Header'}, 'start_line': 0, 'end_line': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a h1 header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'p': '', 'indent': 0},
        {'header': {'level': 2, 'content': 'Header level 2'}, 'start_line': 0, 'end_line': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a separator', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    assert convert_headers(input_data) == expected
