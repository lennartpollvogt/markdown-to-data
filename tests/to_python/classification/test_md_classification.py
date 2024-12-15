from src.markdown_to_data.to_python.classification.classification import classify_markdown_line_by_line


markdown = """
---
title: A test Markdown
tags: python, markdown, md, data
author: the owner
---

# Header 1
#No header just a paragraph to test header

> blockquote
 >this is also a blockquote
>> level 2

| column1 | column2 |
|---------|---------|
| cell 1  | cell 2  |
| cell 3  | cell 4
"""


def test_md_classification():
    result = classify_markdown_line_by_line(markdown=markdown)

    expected_result = [
        {'hr': '---', 'indent': 0},
        {'p': 'title: A test Markdown', 'indent': 0},
        {'p': 'tags: python, markdown, md, data', 'indent': 0},
        {'p': 'author: the owner', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'p': '', 'indent': 0},
        {'h1': 'Header 1', 'indent': 0},
        {'p': '#No header just a paragraph to test header', 'indent': 0},
        {'p': '', 'indent': 0},
        {'blockquote': 'blockquote', 'level': 1},
        {'blockquote': 'this is also a blockquote', 'level': 1},
        {'blockquote': 'level 2', 'level': 2},
        {'p': '', 'indent': 0},
        {'tr': {'td_1': 'column1', 'td_2': 'column2'}, 'indent': 0},
        {'tr': 'table_separator', 'indent': 0},
        {'tr': {'td_1': 'cell 1', 'td_2': 'cell 2'}, 'indent': 0},
        {'tr': {'td_1': 'cell 3', 'td_2': 'cell 4'}, 'indent': 0},
    ]

    assert result == expected_result
