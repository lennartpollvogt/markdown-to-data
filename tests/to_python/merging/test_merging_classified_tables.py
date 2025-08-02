from src.markdown_to_data.to_python.merging_multiline_objects.merge_table import merge_tables

def test_basic_table_with_headers():
    """Test basic table with headers and separator."""
    input_data = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0},
        {'tr': {'td_1': 'Jane', 'td_2': 30, 'td_3': 'LA'}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'Name': ['John', 'Jane'],
                'Age': [25, 30],
                'City': ['NYC', 'LA']
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_table_without_headers():
    """Test table without headers (no separator)."""
    input_data = [
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0},
        {'tr': {'td_1': 'Jane', 'td_2': 30, 'td_3': 'LA'}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'col_1': ['John', 'Jane'],
                'col_2': [25, 30],
                'col_3': ['NYC', 'LA']
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_inconsistent_columns():
    """Test table with inconsistent column counts."""
    input_data = [
        {'tr': {'td_1': 'A', 'td_2': 'B', 'td_3': 'C'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 1, 'td_2': 2}, 'indent': 0},
        {'tr': {'td_1': 1, 'td_2': 2, 'td_3': 3, 'td_4': 4}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'A': [1, 1],
                'B': [2, 2],
                'C': [None, 3],
                'col_4': [None, 4]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_mixed_content():
    """Test mixing tables with other markdown elements."""
    input_data = [
        {'p': 'Some text'},
        {'tr': {'td_1': 'A', 'td_2': 'B'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 1, 'td_2': 2}, 'indent': 0},
        {'h1': 'Header'}
    ]

    expected = [
        {'p': 'Some text'},
        {
            'table': {
                'A': [1],
                'B': [2]
            },
            'start_line': 0,
            'end_line': 0
        },
        {'h1': 'Header'}
    ]

    assert merge_tables(input_data) == expected

def test_empty_table():
    """Test table with empty cells."""
    input_data = [
        {'tr': {'td_1': 'Header'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': None}, 'indent': 0},
        {'tr': {'td_1': ''}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'Header': [None, None]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_multiple_tables():
    """Test multiple tables in the input."""
    input_data = [
        {'tr': {'td_1': 'A'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 1}, 'indent': 0},
        {'p': 'Between tables'},
        {'tr': {'td_1': 'X'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Y'}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'A': [1]
            },
            'start_line': 0,
            'end_line': 0
        },
        {'p': 'Between tables'},
        {
            'table': {
                'X': ['Y']
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_single_row_table():
    """Test table with single row."""
    input_data = [
        {'tr': {'td_1': 'Single', 'td_2': 'Row'}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'col_1': ['Single'],
                'col_2': ['Row']
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected

def test_table_with_mixed_types():
    """Test table with mixed data types."""
    input_data = [
        {'tr': {'td_1': 'Item', 'td_2': 'Count', 'td_3': 'Price'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Apple', 'td_2': 5, 'td_3': 1.99}, 'indent': 0},
        {'tr': {'td_1': 'Orange', 'td_2': None, 'td_3': 2.50}, 'indent': 0}
    ]

    expected = [
        {
            'table': {
                'Item': ['Apple', 'Orange'],
                'Count': [5, None],
                'Price': [1.99, 2.50]
            },
            'start_line': 0,
            'end_line': 0
        }
    ]

    assert merge_tables(input_data) == expected
