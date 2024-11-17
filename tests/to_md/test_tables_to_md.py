import pytest
from src.markdown_to_data.to_md.md_elements.to_md_tables import table_data_to_md

def test_simple_table():
    data = {
        'table': [
            {
                'Name': 'John',
                'Age': '30',
                'City': 'New York'
            },
            {
                'Name': 'Alice',
                'Age': '25',
                'City': 'London'
            }
        ]
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
        'table': [
            {
                'Service': 'Cloud Services',
                'Q1 Sales ($)': '100,000',
                'Q2 Sales ($)': '150,000',
                'Total Sales ($)': '250,000',
                'Growth (%)': '50%'
            },
            {
                'Service': 'Maintenance',
                'Q1 Sales ($)': '80,000',
                'Q2 Sales ($)': '90,000',
                'Total Sales ($)': '170,000',
                'Growth (%)': '12.5%'
            }
        ]
    }
    expected = (
        "| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |\n"
        "|----------------|--------------|--------------|-----------------|------------|\n"
        "| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |\n"
        "| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |"
    )
    assert table_data_to_md(data) == expected

def test_empty_table():
    data = {'table': []}
    assert table_data_to_md(data) == ''

def test_invalid_input():
    data = {}
    assert table_data_to_md(data) == ''

def test_none_input():
    assert table_data_to_md(None) == ''

def test_single_row_table():
    data = {
        'table': [
            {
                'Header1': 'Value1',
                'Header2': 'Value2'
            }
        ]
    }
    expected = (
        "| Header1 | Header2 |\n"
        "|---------|---------|\n"
        "| Value1  | Value2  |"
    )
    assert table_data_to_md(data) == expected

def test_different_data_types():
    data = {
        'table': [
            {
                'String': 'text',
                'Number': 42,
                'Boolean': True,
                'None': None
            }
        ]
    }
    expected = (
        "| String | Number | Boolean | None |\n"
        "|--------|--------|---------|------|\n"
        "| text   | 42     | True    | None |"
    )
    assert table_data_to_md(data) == expected

def test_special_characters():
    data = {
        'table': [
            {
                'Column*': 'Value!',
                'Column#': 'Value@'
            }
        ]
    }
    expected = (
        "| Column* | Column# |\n"
        "|---------|---------|\n"
        "| Value!  | Value@  |"
    )
    assert table_data_to_md(data) == expected

def test_long_content():
    data = {
        'table': [
            {
                'Short': 'A',
                'Very Long Header': 'Short',
                'Normal': 'Content'
            },
            {
                'Short': 'B',
                'Very Long Header': 'Very long content here',
                'Normal': 'Content'
            }
        ]
    }
    expected = (
        "| Short | Very Long Header       | Normal  |\n"
        "|-------|------------------------|---------|\n"
        "| A     | Short                  | Content |\n"
        "| B     | Very long content here | Content |"
    )
    assert table_data_to_md(data) == expected

def test_direct_list_input():
    data = [
        {
            'Col1': 'Value1',
            'Col2': 'Value2'
        },
        {
            'Col1': 'Value3',
            'Col2': 'Value4'
        }
    ]
    expected = (
        "| Col1   | Col2   |\n"
        "|--------|--------|\n"
        "| Value1 | Value2 |\n"
        "| Value3 | Value4 |"
    )
    assert table_data_to_md(data) == expected

def test_whitespace_handling():
    data = {
        'table': [
            {
                'Header': 'Value with    spaces',
                'Other': 'Normal'
            }
        ]
    }
    expected = (
        "| Header               | Other  |\n"
        "|----------------------|--------|\n"
        "| Value with    spaces | Normal |"
    )
    assert table_data_to_md(data) == expected

def test_empty_cells():
    data = {
        'table': [
            {
                'Col1': '',
                'Col2': 'Value'
            }
        ]
    }
    expected = (
        "| Col1 | Col2  |\n"
        "|------|-------|\n"
        "|      | Value |"
    )
    assert table_data_to_md(data) == expected
