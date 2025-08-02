from src.markdown_to_data.to_python.convert_single_line_objects.convert_separators import convert_separators

def test_single_separator():
    input_data = [
        {'hr': '---', 'indent': 0}
    ]

    expected = [
        {'separator': '---', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_separators(input_data) == expected

def test_multiple_separators():
    input_data = [
        {'hr': '---', 'indent': 0},
        {'p': 'some text'},
        {'hr': '***', 'indent': 0}
    ]

    expected = [
        {'separator': '---', 'start_line': 0, 'end_line': 0},
        {'p': 'some text'},
        {'separator': '***', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_separators(input_data) == expected

def test_no_separators():
    input_data = [
        {'p': 'paragraph 1'},
        {'h1': 'heading'},
        {'p': 'paragraph 2'}
    ]

    expected = input_data.copy()

    assert convert_separators(input_data) == expected

def test_empty_input():
    input_data = []
    expected = []
    assert convert_separators(input_data) == expected

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
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a h1 header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'separator': '---', 'start_line': 0, 'end_line': 0},
        {'p': '', 'indent': 0},
        {'h2': 'Header level 2', 'indent': 0},
        {'p': '', 'indent': 0},
        {'p': 'A paragraph after a separator', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    assert convert_separators(input_data) == expected

def test_different_separator_styles():
    input_data = [
        {'hr': '---', 'indent': 0},
        {'p': 'text'},
        {'hr': '***', 'indent': 0},
        {'p': 'text'},
        {'hr': '___', 'indent': 0}
    ]

    expected = [
        {'separator': '---', 'start_line': 0, 'end_line': 0},
        {'p': 'text'},
        {'separator': '***', 'start_line': 0, 'end_line': 0},
        {'p': 'text'},
        {'separator': '___', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_separators(input_data) == expected
