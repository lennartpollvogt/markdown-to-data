import pytest
from markdown_to_data.markdown_to_data import MarkdownMapper

@pytest.fixture
def mapper() -> MarkdownMapper:
    return MarkdownMapper()

def test_extract_md_metadata_valid(mapper):
    markdown_with_metadata = """

---
title: My Document
author: John Doe
date: 2023-09-15
---

---
title: My Document
author: John Doe
date: 2023-09-15
---
# Introduction

This is a test document.
"""
    result = mapper._extract_md_metadata(markdown_with_metadata)
    expected = {
        'title': 'My Document',
        'author': 'John Doe',
        'date': '2023-09-15',
        #'date': datetime.date(2023, 9, 15)
    }
    assert result == expected, f"Expected {expected}, but got {result}"


def test_extract_md_metadata_valid_with_second_metadata(mapper):
    '''
    In this case only the first metadata should be extracted.
    '''
    markdown_with_metadata = """

---
title: My Document
author: John Doe
date: 2023-09-15
---

---
title: My Document
author: John Doe
date: 2023-09-20
---
# Introduction

This is a test document.
"""
    result = mapper._extract_md_metadata(markdown_with_metadata)
    expected = {
        'title': 'My Document',
        'author': 'John Doe',
        'date': '2023-09-15',
        #'date': datetime.date(2023, 9, 15)
    }
    assert result == expected, f"Expected {expected}, but got {result}"


def test_extract_md_metadata_invalid(mapper):
    markdown_without_metadata = """
# Introduction

This is a test document.
"""
    result = mapper._extract_md_metadata(markdown_without_metadata)
    assert result == {}, "Expected an empty dictionary for markdown without metadata."

def test_extract_md_metadata_malformed(mapper):
    malformed_metadata = """
---
title: My Document
author John Doe  # Missing colon after 'author'
date: 2023-09-15
---

# Introduction

This is a test document.
"""
    with pytest.raises(ValueError):
        mapper._extract_md_metadata(malformed_metadata)


# pytest test_metadata.py
