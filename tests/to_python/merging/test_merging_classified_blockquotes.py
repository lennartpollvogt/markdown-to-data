from src.markdown_to_data.to_python.merging_multiline_objects.merge_blockquote import merge_blockquotes

def test_single_line_blockquote():
    input_data = [
        {'blockquote': {'p': 'a single line blockquote', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'a single line blockquote',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_multiline_blockquote():
    input_data = [
        {'blockquote': {'p': 'first line', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'second line', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'third line', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'first line',
                    'items': []
                },
                {
                    'content': 'second line',
                    'items': []
                },
                {
                    'content': 'third line',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_nested_blockquote():
    input_data = [
        {'blockquote': {'p': 'outer line', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'nested line', 'indent': 0}, 'level': 2},
        {'blockquote': {'p': 'final line', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'outer line',
                    'items': [
                        {
                            'content': 'nested line',
                            'items': []
                        }
                    ]
                },
                {
                    'content': 'final line',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_multiple_separate_blockquotes():
    input_data = [
        {'blockquote': {'p': 'first quote', 'indent': 0}, 'level': 1},
        {'p': 'normal paragraph'},
        {'blockquote': {'p': 'second quote', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'first quote',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        },
        {'p': 'normal paragraph'},
        {
            'blockquote': [
                {
                    'content': 'second quote',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_complex_nested_blockquote():
    input_data = [
        {'blockquote': {'p': 'level 1', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'level 2', 'indent': 0}, 'level': 2},
        {'blockquote': {'p': 'level 3', 'indent': 0}, 'level': 3},
        {'blockquote': {'p': 'back to level 2', 'indent': 0}, 'level': 2},
        {'blockquote': {'p': 'back to level 1', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'level 1',
                    'items': [
                        {
                            'content': 'level 2',
                            'items': [
                                {
                                    'content': 'level 3',
                                    'items': []
                                }
                            ]
                        },
                        {
                            'content': 'back to level 2',
                            'items': []
                        }
                    ]
                },
                {
                    'content': 'back to level 1',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_empty_input():
    input_data = []
    expected = []
    assert merge_blockquotes(input_data) == expected

def test_no_blockquotes():
    input_data = [
        {'p': 'paragraph 1'},
        {'h1': 'heading'},
        {'p': 'paragraph 2'}
    ]
    expected = input_data.copy()
    assert merge_blockquotes(input_data) == expected

def test_example_from_docstring():
    input_data = [
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'blockquote': {'p': 'a single line blockquote', 'indent': 0}, 'level': 1},
        {'p': '', 'indent': 0},
        {'blockquote': {'p': 'a nested blockquote', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'with multiline', 'indent': 0}, 'level': 1},
        {'blockquote': {'p': 'the nested part', 'indent': 0}, 'level': 2},
        {'blockquote': {'p': 'last line of the blockquote', 'indent': 0}, 'level': 1}
    ]

    expected = [
        {'h1': 'Header', 'indent': 0},
        {'p': '', 'indent': 0},
        {
            'blockquote': [
                {
                    'content': 'a single line blockquote',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        },
        {'p': '', 'indent': 0},
        {
            'blockquote': [
                {
                    'content': 'a nested blockquote',
                    'items': []
                },
                {
                    'content': 'with multiline',
                    'items': [
                        {
                            'content': 'the nested part',
                            'items': []
                        }
                    ]
                },
                {
                    'content': 'last line of the blockquote',
                    'items': []
                }
            ],
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_blockquotes(input_data) == expected
