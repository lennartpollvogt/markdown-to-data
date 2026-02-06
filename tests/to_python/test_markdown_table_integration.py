from src.markdown_to_data import Markdown


def test_aligned_table_headers_end_to_end():
    markdown = """
| Name1 | Name2 | Name3 |
| :---- | ----: | :---: |
| cell1 | cell2 | cell3 |
| cell4 | cell5 | cell6 |
"""
    md = Markdown(markdown)

    assert md.md_list == [
        {
            "table": {
                "Name1": ["cell1", "cell4"],
                "Name2": ["cell2", "cell5"],
                "Name3": ["cell3", "cell6"],
            },
            "start_line": 2,
            "end_line": 5,
        }
    ]
