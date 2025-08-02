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
