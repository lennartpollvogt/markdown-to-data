import pytest
from markdown_to_data.convert.joining_and_extraction.extraction import MarkdownExtractor

# pytest test_tables.py

@pytest.fixture
def mapper():
    return MarkdownExtractor()

def test_extract_md_table_valid_from_two(mapper):
    markdown_with_table = """
| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |
| Consulting     | 50,000       | 70,000       | 120,000         | 40%        |
Second table:
| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |
| Consulting     | 50,000       | 70,000       | 120,000         | 40%        |
    """

    result = mapper._extract_md_table(markdown_with_table)
    expected = [
        {
            "Service": "Cloud Services",
            "Q1 Sales ($)": "100,000",
            "Q2 Sales ($)": "150,000",
            "Total Sales ($)": "250,000",
            "Growth (%)": "50%"
        },
        {
            "Service": "Maintenance",
            "Q1 Sales ($)": "80,000",
            "Q2 Sales ($)": "90,000",
            "Total Sales ($)": "170,000",
            "Growth (%)": "12.5%"
        },
        {
            "Service": "Consulting",
            "Q1 Sales ($)": "50,000",
            "Q2 Sales ($)": "70,000",
            "Total Sales ($)": "120,000",
            "Growth (%)": "40%"
        }
    ]
    assert result == expected, f"Expected {expected}, but got {result}"

'''
def test_extract_md_table_valid_with_additional_top_row(mapper):
    markdown_with_table = """
|                                Sales Overview                               |
| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    | 80,000       | 90,000       | 170,000         | 12.5%      |
| Consulting     | 50,000       | 70,000       | 120,000         | 40%        |
    """

    result = mapper._extract_md_table(markdown_with_table)
    expected = [
        {
            "Service": "Cloud Services",
            "Q1 Sales ($)": "100,000",
            "Q2 Sales ($)": "150,000",
            "Total Sales ($)": "250,000",
            "Growth (%)": "50%"
        },
        {
            "Service": "Maintenance",
            "Q1 Sales ($)": "80,000",
            "Q2 Sales ($)": "90,000",
            "Total Sales ($)": "170,000",
            "Growth (%)": "12.5%"
        },
        {
            "Service": "Consulting",
            "Q1 Sales ($)": "50,000",
            "Q2 Sales ($)": "70,000",
            "Total Sales ($)": "120,000",
            "Growth (%)": "40%"
        }
    ]
    assert result == expected, f"Expected {expected}, but got {result}"
'''


def test_extract_md_table_empty(mapper):
    markdown_with_empty_table = """
| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
    """

    result = mapper._extract_md_table(markdown_with_empty_table)
    expected = []
    assert result == expected, f"Expected empty list, but got {result}"

def test_extract_md_table_missing_data(mapper):
    markdown_with_missing_data = """
| Service        | Q1 Sales ($) | Q2 Sales ($) | Total Sales ($) | Growth (%) |
|----------------|--------------|--------------|-----------------|------------|
| Cloud Services | 100,000      | 150,000      | 250,000         | 50%        |
| Maintenance    |              | 90,000       | 170,000         |            |
    """

    result = mapper._extract_md_table(markdown_with_missing_data)
    expected = [
        {
            "Service": "Cloud Services",
            "Q1 Sales ($)": "100,000",
            "Q2 Sales ($)": "150,000",
            "Total Sales ($)": "250,000",
            "Growth (%)": "50%"
        },
        {
            "Service": "Maintenance",
            "Q1 Sales ($)": None,
            "Q2 Sales ($)": "90,000",
            "Total Sales ($)": "170,000",
            "Growth (%)": None
        }
    ]
    assert result == expected, f"Expected {expected}, but got {result}"

def test_extract_md_table_no_table(mapper):
    markdown_without_table = """
# No Table Here
This is a markdown snippet without any table.
    """

    result = mapper._extract_md_table(markdown_without_table)
    expected = []
    assert result == expected, f"Expected empty list, but got {result}"
