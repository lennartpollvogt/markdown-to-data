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

def test_blockquote_with_header():
    """Test merging blockquotes containing headers."""
    input_data = [
        {
            'blockquote': {'h1': 'Header in blockquote', 'indent': 0},
            'level': 1,
            'line': 1
        },
        {
            'blockquote': {'p': 'Normal text in blockquote', 'indent': 0},
            'level': 1,
            'line': 2
        }
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'Header in blockquote',
                    'items': []
                },
                {
                    'content': 'Normal text in blockquote',
                    'items': []
                }
            ],
            'start_line': 1,
            'end_line': 2
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_blockquote_with_multiple_header_levels():
    """Test merging blockquotes with various header levels."""
    input_data = [
        {
            'blockquote': {'h1': 'H1 in quote', 'indent': 0},
            'level': 1,
            'line': 1
        },
        {
            'blockquote': {'h2': 'H2 in quote', 'indent': 0},
            'level': 1,
            'line': 2
        },
        {
            'blockquote': {'h3': 'H3 in quote', 'indent': 0},
            'level': 1,
            'line': 3
        },
        {
            'blockquote': {'p': 'Normal text', 'indent': 0},
            'level': 1,
            'line': 4
        }
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'H1 in quote',
                    'items': []
                },
                {
                    'content': 'H2 in quote',
                    'items': []
                },
                {
                    'content': 'H3 in quote',
                    'items': []
                },
                {
                    'content': 'Normal text',
                    'items': []
                }
            ],
            'start_line': 1,
            'end_line': 4
        }
    ]

    assert merge_blockquotes(input_data) == expected

def test_nested_blockquote_with_headers():
    """Test merging nested blockquotes containing headers."""
    input_data = [
        {
            'blockquote': {'h1': 'Main quote header', 'indent': 0},
            'level': 1,
            'line': 1
        },
        {
            'blockquote': {'h2': 'Nested quote header', 'indent': 0},
            'level': 2,
            'line': 2
        },
        {
            'blockquote': {'p': 'Nested text', 'indent': 0},
            'level': 2,
            'line': 3
        },
        {
            'blockquote': {'p': 'Back to main quote', 'indent': 0},
            'level': 1,
            'line': 4
        }
    ]

    expected = [
        {
            'blockquote': [
                {
                    'content': 'Main quote header',
                    'items': [
                        {
                            'content': 'Nested quote header',
                            'items': []
                        },
                        {
                            'content': 'Nested text',
                            'items': []
                        }
                    ]
                },
                {
                    'content': 'Back to main quote',
                    'items': []
                }
            ],
            'start_line': 1,
            'end_line': 4
        }
    ]

    assert merge_blockquotes(input_data) == expected
