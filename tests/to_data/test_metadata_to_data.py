import pytest
from src.markdown_to_data.markdown_to_data import Markdown

def test_simple_metadata():
    markdown = """---
title: Test Document
author: John Doe
date: 2024-01-15
---

# Content starts here
"""
    md = Markdown(markdown)
    expected = {
        'title': 'Test Document',
        'author': 'John Doe',
        'date': '2024-01-15'
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_spaces():
    markdown = """---
title: This is a longer title with spaces
created by: John Doe
last modified: 2024-01-15
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'title': 'This is a longer title with spaces',
        'created_by': 'John Doe',
        'last_modified': '2024-01-15'
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_multiple_spaces():
    markdown = """---
title: This is a longer title with spaces
created-by: John Doe
last    modified: 2024-01-15
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'title': 'This is a longer title with spaces',
        'created-by': 'John Doe',
        'last_modified': '2024-01-15'
    }
    assert md.md_dict['metadata'] == expected

def test_no_metadata():
    markdown = """# Document without metadata

This is a regular document.
"""
    md = Markdown(markdown)
    assert 'metadata' not in md.md_dict

def test_empty_metadata():
    markdown = """---
---

# Content
"""
    md = Markdown(markdown)
    assert 'metadata' not in md.md_dict or md.md_dict['metadata'] == {}

def test_metadata_with_empty_values():
    markdown = """---
title:
author:
date:
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'title': None,
        'author': None,
        'date': None
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_colons_in_values():
    markdown = """---
title: Understanding Time: A Brief History
time: 15:30
url: https://example.com
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'title': 'Understanding Time: A Brief History',
        'time': '15:30',
        'url': 'https://example.com'
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_only():
    markdown = """---
title: Test Document
author: John Doe
---"""
    md = Markdown(markdown)
    expected = {
        'title': 'Test Document',
        'author': 'John Doe'
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_subsequent_content():
    markdown = """---
title: Test Document
author: John Doe
---
This is a paragraph right after metadata.

# First heading
"""
    md = Markdown(markdown)
    assert md.md_dict['metadata'] == {
        'title': 'Test Document',
        'author': 'John Doe'
    }
    # Optionally verify that the content after metadata is preserved
    assert 'First heading' in str(md.md_dict)


def test_metadata_with_bracketed_list():
    markdown = """---
labels: [python, testing, markdown]
categories: [documentation, tools]
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'labels': ['python', 'testing', 'markdown'],
        'categories': ['documentation', 'tools']
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_parentheses_list():
    markdown = """---
tags: (frontend, backend, api)
maintainers: (John Doe, Jane Smith)
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'tags': ['frontend', 'backend', 'api'],
        'maintainers': ['John Doe', 'Jane Smith']
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_comma_separated_list():
    markdown = """---
keywords: python, markdown, parser
authors: John Doe, Jane Smith, Bob Johnson
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'keywords': ['python', 'markdown', 'parser'],
        'authors': ['John Doe', 'Jane Smith', 'Bob Johnson']
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_mixed_formats():
    markdown = """---
title: Test Document
tags: [python, testing]
contributors: (John Doe, Jane Smith)
keywords: markdown, parser, data
version: 1.0.0
boolean: True
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'title': 'Test Document',
        'tags': ['python', 'testing'],
        'contributors': ['John Doe', 'Jane Smith'],
        'keywords': ['markdown', 'parser', 'data'],
        'version': '1.0.0',
        'boolean': True
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_single_item_lists():
    markdown = """---
tag: [python]
category: (testing)
language: markdown
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'tag': ['python'],
        'category': ['testing'],
        'language': 'markdown'
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_quoted_values():
    markdown = """---
description: "This is a, complex description"
quote: 'Single quoted, value with commas'
quote2: "Double quoted, value with commas"
tags: [python, "web, development", testing]
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'description': 'This is a, complex description',
        'quote': 'Single quoted, value with commas',
        'quote2': 'Double quoted, value with commas',
        'tags': ['python', 'web, development', 'testing']
    }
    assert md.md_dict['metadata'] == expected

def test_metadata_with_numbers_and_decimals():
    markdown = """---
number: 1
numbers: 1,2,3, 4
decimal: 1.4
deciamals: [11.333, 4.6, 7.3]
wrong_decimal: 1,2
---

# Content
"""
    md = Markdown(markdown)
    expected = {
        'number': 1,
        'numbers': [1, 2, 3, 4],
        'decimal': 1.4,
        'deciamals': [11.333, 4.6, 7.3],
        'wrong_decimal': [1, 2]
    }
    assert md.md_dict['metadata'] == expected
