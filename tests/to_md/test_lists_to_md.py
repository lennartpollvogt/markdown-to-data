from src.markdown_to_data.to_md.md_elements.to_md_lists import list_data_to_md

def test_simple_unordered_list():
    """Test conversion of a simple unordered list."""
    data = {
        'list': {
            'type': 'ul',
            'items': [
                {'content': 'item 1', 'items': [], 'task': None},
                {'content': 'item 2', 'items': [], 'task': None}
            ]
        }
    }
    expected = (
        "- item 1\n"
        "- item 2"
    )
    assert list_data_to_md(data) == expected

def test_nested_unordered_list():
    """Test conversion of a nested unordered list."""
    data = {
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
        }
    }
    expected = (
        "- item 1\n"
        "- item 2\n"
        "    - item 2.1"
    )
    assert list_data_to_md(data) == expected

def test_task_list():
    """Test conversion of a task list."""
    data = {
        'list': {
            'type': 'ul',
            'items': [
                {'content': 'item 1', 'items': [], 'task': 'checked'},
                {'content': 'item 2', 'items': [], 'task': 'unchecked'}
            ]
        }
    }
    expected = (
        "- [x] item 1\n"
        "- [ ] item 2"
    )
    assert list_data_to_md(data) == expected

def test_ordered_list():
    """Test conversion of an ordered list."""
    data = {
        'list': {
            'type': 'ol',
            'items': [
                {'content': 'item 1', 'items': [], 'task': None},
                {'content': 'item 2', 'items': [], 'task': None}
            ]
        }
    }
    expected = (
        "1. item 1\n"
        "2. item 2"
    )
    assert list_data_to_md(data) == expected

def test_deeply_nested_list():
    """Test conversion of a deeply nested list."""
    data = {
        'list': {
            'type': 'ul',
            'items': [
                {
                    'content': 'item 1',
                    'items': [
                        {
                            'content': 'item 1.1',
                            'items': [
                                {'content': 'item 1.1.1', 'items': [], 'task': None}
                            ],
                            'task': None
                        }
                    ],
                    'task': None
                }
            ]
        }
    }
    expected = (
        "- item 1\n"
        "    - item 1.1\n"
        "        - item 1.1.1"
    )
    assert list_data_to_md(data) == expected

def test_mixed_nested_lists():
    """Test conversion of mixed nested lists with tasks."""
    data = {
        'list': {
            'type': 'ol',
            'items': [
                {'content': 'item 1', 'items': [], 'task': None},
                {
                    'content': 'item 2',
                    'items': [
                        {'content': 'item 2.1', 'items': [], 'task': 'checked'},
                        {
                            'content': 'item 2.2',
                            'items': [
                                {'content': 'item 2.2.1', 'items': [], 'task': 'unchecked'}
                            ],
                            'task': None
                        }
                    ],
                    'task': None
                }
            ]
        }
    }
    expected = (
        "1. item 1\n"
        "2. item 2\n"
        "    1. [x] item 2.1\n"
        "    2. item 2.2\n"
        "        1. [ ] item 2.2.1"
    )
    assert list_data_to_md(data) == expected

def test_empty_list():
    """Test conversion of an empty list."""
    data = {
        'list': {
            'type': 'ul',
            'items': []
        }
    }
    assert list_data_to_md(data) == ''

def test_invalid_input():
    """Test handling of invalid input."""
    assert list_data_to_md({}) == ''
    assert list_data_to_md({'list': {}}) == ''
    assert list_data_to_md({'list': {'type': 'ul'}}) == ''

def test_task_list_spacing():
    """Test correct spacing in task lists."""
    data = {
        'list': {
            'type': 'ul',
            'items': [
                {'content': 'Completed task', 'items': [], 'task': 'checked'},
                {'content': 'Pending task', 'items': [], 'task': 'unchecked'}
            ]
        }
    }
    expected = (
        "- [x] Completed task\n"
        "- [ ] Pending task"
    )
    result = list_data_to_md(data)
    assert result == expected
    # Specifically check there's exactly one space between - and [
    assert "- [" in result and not "-  [" in result


def test_task_list_1():
    data = {
        'list': {
            'type': 'ul',
            'items': [
                {'content': 'Completed task', 'items': [], 'task': 'checked'},
                {
                    'content': 'Pending task',
                    'items': [
                        {
                            'content': 'Nested completed task',
                            'items': [],
                            'task': 'checked'
                        },
                        {
                            'content': 'Nested pending task',
                            'items': [],
                            'task': 'unchecked'
                        }
                    ],
                    'task': 'unchecked'
                }
            ]
        }
    }
    expected = (
        "- [x] Completed task\n"
        "- [ ] Pending task\n"
        "    - [x] Nested completed task\n"
        "    - [ ] Nested pending task"
    )
    result = list_data_to_md(data)
    assert result == expected
