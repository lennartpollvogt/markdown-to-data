from src.markdown_to_data.to_python.merging_multiline_objects.merge_list import merge_lists

def test_simple_unordered_list():
    """Test merging of a simple unordered list."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {
            'ul': {
                'li': {'p': 'item 2', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': None},
                    {'content': 'item 2', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_lists(classified_list) == expected

def test_nested_unordered_list():
    """Test merging of a nested unordered list."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {
            'ul': {
                'li': {'p': 'item 2', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {
            'ul': {
                'li': {'p': 'item 2.1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 6,
            'marker_indent': 4
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': None},
                    {
                        'content': 'item 2',
                        'items': [
                            {'content': 'item 2.1', 'items': [], 'task': None}
                        ],
                        'task': None
                    }
                ]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_lists(classified_list) == expected

def test_multiple_lists_separated_by_paragraph():
    """Test merging of multiple lists separated by empty paragraphs."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {'p': '', 'indent': 0},
        {
            'ul': {
                'li': {'p': 'item 2', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        },
        {'p': '', 'indent': 0},
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 2', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_lists(classified_list) == expected

def test_mixed_list_types():
    """Test merging of mixed list types (unordered and ordered)."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {'p': '', 'indent': 0},
        {
            'ol': {
                'li': {'p': 'item 2', 'indent': 0},
                'marker': '1.',
                'task': None
            },
            'item_indent': 3,
            'marker_indent': 0
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        },
        {'p': '', 'indent': 0},
        {
            'list': {
                'type': 'ol',
                'items': [
                    {'content': 'item 2', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_lists(classified_list) == expected

def test_task_list():
    """Test merging of task lists."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': 'checked'
            },
            'item_indent': 6,
            'marker_indent': 0
        },
        {
            'ul': {
                'li': {'p': 'item 2', 'indent': 0},
                'marker': '-',
                'task': 'unchecked'
            },
            'item_indent': 6,
            'marker_indent': 0
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': 'checked'},
                    {'content': 'item 2', 'items': [], 'task': 'unchecked'}
                ]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_lists(classified_list) == expected

def test_empty_input():
    """Test merging with empty input."""
    assert merge_lists([]) == []

def test_list_terminated_by_different_element():
    """Test list terminated by a different markdown element."""
    classified_list = [
        {
            'ul': {
                'li': {'p': 'item 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0
        },
        {'blockquote': 'some quote', 'indent': 0}
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'item 1', 'items': [], 'task': None}
                ]
            },
            'start_line': 0,
            'end_line': 0
        },
        {'blockquote': 'some quote', 'indent': 0}
    ]

    assert merge_lists(classified_list) == expected

def test_list_with_header_items():
    """Test merging of list items containing headers."""
    classified_list = [
        {
            'ul': {
                'li': {'h1': 'Header level 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 1
        },
        {
            'ul': {
                'li': {'p': 'normal item', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 2
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'Header level 1', 'items': [], 'task': None},
                    {'content': 'normal item', 'items': [], 'task': None}
                ]
            },
            'start_line': 1,
            'end_line': 2
        }
    ]

    assert merge_lists(classified_list) == expected

def test_list_with_multiple_header_levels():
    """Test merging of list items with various header levels (h1-h6)."""
    classified_list = [
        {
            'ul': {
                'li': {'h1': 'Header 1', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 1
        },
        {
            'ul': {
                'li': {'h2': 'Header 2', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 2
        },
        {
            'ul': {
                'li': {'h3': 'Header 3', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 3
        },
        {
            'ul': {
                'li': {'h6': 'Header 6', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 4
        },
        {
            'ul': {
                'li': {'p': 'normal paragraph', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 5
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'Header 1', 'items': [], 'task': None},
                    {'content': 'Header 2', 'items': [], 'task': None},
                    {'content': 'Header 3', 'items': [], 'task': None},
                    {'content': 'Header 6', 'items': [], 'task': None},
                    {'content': 'normal paragraph', 'items': [], 'task': None}
                ]
            },
            'start_line': 1,
            'end_line': 5
        }
    ]

    assert merge_lists(classified_list) == expected

def test_nested_list_with_headers():
    """Test merging of nested lists containing headers."""
    classified_list = [
        {
            'ul': {
                'li': {'h1': 'Main header', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 1
        },
        {
            'ul': {
                'li': {'h2': 'Nested header', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 6,
            'marker_indent': 4,
            'line': 2
        },
        {
            'ul': {
                'li': {'p': 'nested item', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 6,
            'marker_indent': 4,
            'line': 3
        },
        {
            'ul': {
                'li': {'p': 'Another item', 'indent': 0},
                'marker': '-',
                'task': None
            },
            'item_indent': 2,
            'marker_indent': 0,
            'line': 4
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {
                        'content': 'Main header',
                        'items': [
                            {'content': 'Nested header', 'items': [], 'task': None},
                            {'content': 'nested item', 'items': [], 'task': None}
                        ],
                        'task': None
                    },
                    {'content': 'Another item', 'items': [], 'task': None}
                ]
            },
            'start_line': 1,
            'end_line': 4
        }
    ]

    assert merge_lists(classified_list) == expected

def test_task_list_with_headers():
    """Test merging of task lists with headers."""
    classified_list = [
        {
            'ul': {
                'li': {'h1': 'Todo header', 'indent': 0},
                'marker': '-',
                'task': 'unchecked'
            },
            'item_indent': 6,
            'marker_indent': 0,
            'line': 1
        },
        {
            'ul': {
                'li': {'h2': 'Completed header', 'indent': 0},
                'marker': '-',
                'task': 'checked'
            },
            'item_indent': 6,
            'marker_indent': 0,
            'line': 2
        },
        {
            'ul': {
                'li': {'p': 'Normal todo', 'indent': 0},
                'marker': '-',
                'task': 'unchecked'
            },
            'item_indent': 6,
            'marker_indent': 0,
            'line': 3
        },
        {
            'ul': {
                'li': {'p': 'Normal completed', 'indent': 0},
                'marker': '-',
                'task': 'checked'
            },
            'item_indent': 6,
            'marker_indent': 0,
            'line': 4
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ul',
                'items': [
                    {'content': 'Todo header', 'items': [], 'task': 'unchecked'},
                    {'content': 'Completed header', 'items': [], 'task': 'checked'},
                    {'content': 'Normal todo', 'items': [], 'task': 'unchecked'},
                    {'content': 'Normal completed', 'items': [], 'task': 'checked'}
                ]
            },
            'start_line': 1,
            'end_line': 4
        }
    ]

    assert merge_lists(classified_list) == expected

def test_ordered_list_with_headers():
    """Test merging of ordered lists with headers."""
    classified_list = [
        {
            'ol': {
                'li': {'h1': 'First header', 'indent': 0},
                'marker': '1.',
                'task': None
            },
            'item_indent': 3,
            'marker_indent': 0,
            'line': 1
        },
        {
            'ol': {
                'li': {'h2': 'Second header', 'indent': 0},
                'marker': '2.',
                'task': None
            },
            'item_indent': 3,
            'marker_indent': 0,
            'line': 2
        },
        {
            'ol': {
                'li': {'p': 'Normal item', 'indent': 0},
                'marker': '3.',
                'task': None
            },
            'item_indent': 3,
            'marker_indent': 0,
            'line': 3
        }
    ]

    expected = [
        {
            'list': {
                'type': 'ol',
                'items': [
                    {'content': 'First header', 'items': [], 'task': None},
                    {'content': 'Second header', 'items': [], 'task': None},
                    {'content': 'Normal item', 'items': [], 'task': None}
                ]
            },
            'start_line': 1,
            'end_line': 3
        }
    ]

    assert merge_lists(classified_list) == expected
