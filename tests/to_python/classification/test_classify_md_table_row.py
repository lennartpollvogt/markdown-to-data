from src.markdown_to_data.to_python.classification.md_classification.classify_md_table_row import is_table_row

def test_basic_table():
    table_input = [
        "| Name | Age | City |",
        "|------|-----|------|",
        "| John | 25  | NYC  |",
        "| Jane | 30  | LA   |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0},
        {'tr': {'td_1': 'Jane', 'td_2': 30, 'td_3': 'LA'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_basic_table_without_separator():
    table_input = [
        "| Name | Age | City |",
        "| John | 25  | NYC  |",
        "| Jane | 30  | LA   |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0},
        {'tr': {'td_1': 'Jane', 'td_2': 30, 'td_3': 'LA'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_table_with_empty_cells():
    table_input = [
        "| Name | Age | City |",
        "|------|-----|------|",
        "| John |     | NYC  |",
        "|      | 30  |      |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': None, 'td_3': 'NYC'}, 'indent': 0},
        {'tr': {'td_1': None, 'td_2': 30, 'td_3': None}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_single_column_table():
    table_input = [
        "| Items |",
        "|-------|",
        "| Apple |",
        "| Banana|"
    ]
    expected_output = [
        {'tr': {'td_1': 'Items'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Apple'}, 'indent': 0},
        {'tr': {'td_1': 'Banana'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_numeric_and_mixed_types():
    table_input = [
        "| Product | Price | Quantity |",
        "|---------|-------|----------|",
        "| Apple   | 1.99  | 5        |",
        "| Banana  | 2.50  | 3.5      |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Product', 'td_2': 'Price', 'td_3': 'Quantity'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Apple', 'td_2': 1.99, 'td_3': 5}, 'indent': 0},
        {'tr': {'td_1': 'Banana', 'td_2': 2.50, 'td_3': 3.5}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_single_cell_merged():
    table_input = [
        "| This is a long cell spanning multiple columns |",
        "|---------------------------------------------|",
        "| Another long row of content                  |"
    ]
    expected_output = [
        {'tr': {'td_1': 'This is a long cell spanning multiple columns'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Another long row of content'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_extra_pipes():
    table_input = [
        "|| Name | Age ||",
        "||------|-----||",
        "|| John | 25  ||"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_inconsistent_columns():
    table_input = [
        "| A | B | C |",
        "|---|---|---|",
        "| 1 | 2 |",
        "| 1 | 2 | 3 | 4 |"
    ]
    expected_output = [
        {'tr': {'td_1': 'A', 'td_2': 'B', 'td_3': 'C'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 1, 'td_2': 2}, 'indent': 0},
        {'tr': {'td_1': 1, 'td_2': 2, 'td_3': 3, 'td_4': 4}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_spaces_around_pipes():
    table_input = [
        "| Name     |    Age    |   City    |",
        "|----------|-----------|-----------|",
        "| John     |    25     |    NYC    |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_minimal_pipes():
    table_input = [
        "Name|Age|City",
        "---|---|---",
        "John|25|NYC"
    ]
    expected_output = [
        {'tr': {'td_1': 'Name', 'td_2': 'Age', 'td_3': 'City'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'John', 'td_2': 25, 'td_3': 'NYC'}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_empty_table():
    table_input = [
        "| |",
        "|-|",
        "| |"
    ]
    expected_output = [
        {'tr': {'td_1': None}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': None}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output

def test_mixed_content_types():
    table_input = [
        "| Item | Count | Price |",
        "|------|-------|-------|",
        "| Apple| 5     | 1.99  |",
        "|      | 10    | null  |",
        "| Orange| none | 2.50  |"
    ]
    expected_output = [
        {'tr': {'td_1': 'Item', 'td_2': 'Count', 'td_3': 'Price'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'Apple', 'td_2': 5, 'td_3': 1.99}, 'indent': 0},
        {'tr': {'td_1': None, 'td_2': 10, 'td_3': 'null'}, 'indent': 0},
        {'tr': {'td_1': 'Orange', 'td_2': 'none', 'td_3': 2.50}, 'indent': 0}
    ]

    result = []
    for line in table_input:
        is_table, row_data = is_table_row(line)
        assert is_table
        result.append(row_data)

    assert result == expected_output
