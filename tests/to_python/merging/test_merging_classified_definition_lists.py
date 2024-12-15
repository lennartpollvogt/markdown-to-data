from src.markdown_to_data.to_python.merging_multiline_objects.merge_definition_list import merge_definition_lists

def test_single_term_single_definition():
    input_data = [
        {'dt': 'term', 'indent': 0},
        {'dd': 'definition', 'indent': 0}
    ]

    expected = [
        {
            'def_list': {
                'term': 'term',
                'list': ['definition']
            }
        }
    ]

    assert merge_definition_lists(input_data) == expected

def test_single_term_multiple_definitions():
    input_data = [
        {'dt': 'term', 'indent': 0},
        {'dd': 'definition 1', 'indent': 0},
        {'dd': 'definition 2', 'indent': 0},
        {'dd': 'definition 3', 'indent': 0}
    ]

    expected = [
        {
            'def_list': {
                'term': 'term',
                'list': ['definition 1', 'definition 2', 'definition 3']
            }
        }
    ]

    assert merge_definition_lists(input_data) == expected

def test_multiple_terms_with_definitions():
    input_data = [
        {'dt': 'term 1', 'indent': 0},
        {'dd': 'definition 1.1', 'indent': 0},
        {'dd': 'definition 1.2', 'indent': 0},
        {'dt': 'term 2', 'indent': 0},
        {'dd': 'definition 2.1', 'indent': 0}
    ]

    expected = [
        {
            'def_list': {
                'term': 'term 1',
                'list': ['definition 1.1', 'definition 1.2']
            }
        },
        {
            'def_list': {
                'term': 'term 2',
                'list': ['definition 2.1']
            }
        }
    ]

    assert merge_definition_lists(input_data) == expected

def test_mixed_content():
    input_data = [
        {'p': 'A paragraph'},
        {'dt': 'term', 'indent': 0},
        {'dd': 'definition', 'indent': 0},
        {'h1': 'A heading'}
    ]

    expected = [
        {'p': 'A paragraph'},
        {
            'def_list': {
                'term': 'term',
                'list': ['definition']
            }
        },
        {'h1': 'A heading'}
    ]

    assert merge_definition_lists(input_data) == expected

def test_example_from_docstring():
    input_data = [
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'dt': 'term 1', 'indent': 0},
        {'dd': 'definition 1', 'indent': 0},
        {'dd': 'definition 2', 'indent': 0},
        {'p': '', 'indent': 0},
        {'dt': 'term 2', 'indent': 0},
        {'dd': 'definition 1', 'indent': 0},
        {'dd': 'definition 2', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    expected = [
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {
            'def_list': {
                'term': 'term 1',
                'list': ['definition 1', 'definition 2']
            }
        },
        {'p': '', 'indent': 0},
        {
            'def_list': {
                'term': 'term 2',
                'list': ['definition 1', 'definition 2']
            }
        },
        {'p': '', 'indent': 0}
    ]

    assert merge_definition_lists(input_data) == expected

def test_empty_input():
    input_data = []
    expected = []
    assert merge_definition_lists(input_data) == expected

def test_no_definition_lists():
    input_data = [
        {'p': 'paragraph 1'},
        {'h1': 'heading'},
        {'p': 'paragraph 2'}
    ]
    expected = input_data.copy()
    assert merge_definition_lists(input_data) == expected

def test_term_without_definition():
    input_data = [
        {'dt': 'lonely term', 'indent': 0},
        {'p': 'A paragraph'}
    ]

    expected = [
        {
            'def_list': {
                'term': 'lonely term',
                'list': []
            }
        },
        {'p': 'A paragraph'}
    ]

    assert merge_definition_lists(input_data) == expected
