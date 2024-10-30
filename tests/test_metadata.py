import pytest
from markdown_to_data.markdown_to_data import Markdown

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
        'created by': 'John Doe',
        'last modified': '2024-01-15'
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
