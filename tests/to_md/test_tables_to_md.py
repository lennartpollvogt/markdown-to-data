from src.markdown_to_data.to_md.md_elements.to_md_tables import table_data_to_md

def test_basic_table():
    data = {
        'table': {
            'Name': ['John', 'Alice'],
            'Age': [30, 25],
            'City': ['New York', 'London']
        }
    }
    expected = (
        "| Name  | Age | City     |\n"
        "|-------|-----|----------|\n"
        "| John  | 30  | New York |\n"
        "| Alice | 25  | London   |"
    )
    assert table_data_to_md(data) == expected

def test_complex_sales_table():
    data = {
        'table': {
            'Service': ['Cloud Services', 'Maintenance'],
            'Q1 Sales ($)': [100000, 80000],
            'Q2 Sales ($)': [150000, 90000],
            'Total Sales ($)': [250000, 170000],
            'Growth (%)': ['50%', '12.5%']
        }
    }
    expected = (
        "| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |\n"
        "|----------------|--------------|--------------|-----------------|------------|\n"
        "| Cloud Services | 100000       | 150000       | 250000          | 50%        |\n"
        "| Maintenance    | 80000        | 90000        | 170000          | 12.5%      |"
    )
    assert table_data_to_md(data) == expected

def test_empty_table():
    data = {'table': {}}
    assert table_data_to_md(data) == ''

def test_invalid_input():
    data = {}
    assert table_data_to_md(data) == ''

def test_none_input():
    assert table_data_to_md(None) == ''

def test_single_row_table():
    data = {
        'table': {
            'Header1': ['Value1'],
            'Header2': ['Value2']
        }
    }
    expected = (
        "| Header1 | Header2 |\n"
        "|---------|---------|\n"
        "| Value1  | Value2  |"
    )
    assert table_data_to_md(data) == expected

def test_different_data_types():
    data = {
        'table': {
            'String': ['text'],
            'Number': [42],
            'Boolean': [True],
            'None': [None]
        }
    }
    expected = (
        "| String | Number | Boolean | None |\n"
        "|--------|--------|---------|------|\n"
        "| text   | 42     | True    | None |"
    )
    assert table_data_to_md(data) == expected

def test_table_with_missing_values():
    data = {
        'table': {
            'A': [1, 1],
            'B': [2, 2],
            'C': [None, 3],
            'col_4': [None, 4]
        }
    }
    expected = (
        "| A | B | C    | col_4 |\n"
        "|---|---|------|-------|\n"
        "| 1 | 2 | None | None  |\n"
        "| 1 | 2 | 3    | 4     |"
    )
    assert table_data_to_md(data) == expected

def test_table_without_headers():
    data = {
        'table': {
            'col_1': ['John', 'Jane'],
            'col_2': [25, 30],
            'col_3': ['NYC', 'LA']
        }
    }
    expected = (
        "| col_1 | col_2 | col_3 |\n"
        "|-------|-------|-------|\n"
        "| John  | 25    | NYC   |\n"
        "| Jane  | 30    | LA    |"
    )
    assert table_data_to_md(data) == expected
