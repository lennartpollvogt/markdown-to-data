from src.markdown_to_data import Markdown


class TestEnhancedMdElements:

    def test_basic_elements_count_and_positions(self):
        """Test basic functionality of count and positions tracking."""
        markdown = """
# Header 1

- List item 1
- List item 2

```python
print("code")
```

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert elements['header']['count'] == 1
        assert elements['header']['positions'] == [0]
        assert elements['list']['count'] == 1
        assert elements['list']['positions'] == [1]
        assert elements['code']['count'] == 1
        assert elements['code']['positions'] == [2]
        assert elements['table']['count'] == 1
        assert elements['table']['positions'] == [3]

    def test_header_variants_and_summary(self):
        """Test header level variants and summary statistics."""
        markdown = """
# Main Title
## Section A
### Subsection
## Section B
#### Deep Section
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'header' in elements
        assert elements['header']['count'] == 5
        assert set(elements['header']['variants']) == {'h1', 'h2', 'h3', 'h4'}
        assert elements['header']['summary']['levels'] == {1: 1, 2: 2, 3: 1, 4: 1}

    def test_list_task_variants_and_summary(self):
        """Test task list detection and statistics."""
        markdown = """
- Regular item
- [x] Completed task
  - [ ] Pending subtask
  - [x] Another completed
- [ ] Incomplete task

1. Ordered item
   1. Nested ordered
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'list' in elements
        assert elements['list']['count'] == 2
        assert 'task' in elements['list']['variants']
        assert 'ul' in elements['list']['variants']
        assert 'ol' in elements['list']['variants']

        # Check task statistics for the first list (which has tasks)
        task_stats = elements['list']['summary']['task_stats']
        assert task_stats['checked'] == 2
        assert task_stats['unchecked'] == 2
        assert task_stats['total_tasks'] == 4

    def test_code_variants_and_summary(self):
        """Test code block language detection and statistics."""
        markdown = """
```python
def hello():
    pass
```

```javascript
console.log("hello");
```

```
# No language
echo "test"
```

```python
# Another python block
print("test")
```
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'code' in elements
        assert elements['code']['count'] == 4
        assert set(elements['code']['variants']) == {'python', 'javascript', None}

        lang_stats = elements['code']['summary']['languages']
        assert lang_stats['python'] == 2
        assert lang_stats['javascript'] == 1
        assert lang_stats['no_language'] == 1

    def test_table_variants_and_summary(self):
        """Test table column count variants and cell statistics."""
        markdown = """
| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |

| Name | Age | City | Country |
|------|-----|------|---------|
| John | 25  | NYC  | USA     |
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'table' in elements
        assert elements['table']['count'] == 2
        assert set(elements['table']['variants']) == {'2_columns', '4_columns'}
        assert elements['table']['summary']['column_counts'] == [2, 4]
        assert elements['table']['summary']['total_cells'] == 8  # 4 + 4

    def test_blockquote_variants_and_summary(self):
        """Test blockquote nesting depth detection."""
        markdown = """
> Simple quote

> Nested quote
>> Level 2
>>> Level 3
>> Back to 2
> Back to 1
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'blockquote' in elements
        assert elements['blockquote']['count'] == 2
        assert 'depth_1' in elements['blockquote']['variants']
        assert 'depth_3' in elements['blockquote']['variants']
        assert elements['blockquote']['summary']['max_nesting_depth'] == 3

    def test_definition_list_variants(self):
        """Test definition list variants tracking."""
        markdown = """
Term 1
: Definition 1
: Definition 2

Term 2
: Single definition

Term 3
: Def 1
: Def 2
: Def 3
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'def_list' in elements
        assert elements['def_list']['count'] == 3
        assert set(elements['def_list']['variants']) == {'1_definitions', '2_definitions', '3_definitions'}

    def test_metadata_variants(self):
        """Test metadata field count tracking."""
        markdown = """
---
title: Test
author: John Doe
tags: [test, markdown]
version: 1.0
---

# Content
"""
        md = Markdown(markdown)
        elements = md.md_elements

        assert 'metadata' in elements
        assert elements['metadata']['count'] == 1
        assert elements['metadata']['variants'] == ['4_fields']

    def test_performance_optimization(self):
        """Test that the implementation is efficient and uses caching."""
        markdown = """
# Header 1
## Header 2
### Header 3

- Item 1
- Item 2
- Item 3
"""
        md = Markdown(markdown)

        # First access should compute the elements
        elements1 = md.md_elements

        # Second access should use cached version
        elements2 = md.md_elements

        # Should be the same object (cached)
        assert elements1 is elements2

        # Verify the content is correct
        assert elements1['header']['count'] == 3
        assert elements1['list']['count'] == 1

    def test_empty_markdown(self):
        """Test behavior with empty markdown."""
        md = Markdown("")
        elements = md.md_elements

        assert elements == {}

    def test_variants_are_sorted_lists(self):
        """Test that variants are returned as sorted lists, not sets."""
        markdown = """
```python
code1
```

```bash
code2
```

```python
code3
```
"""
        md = Markdown(markdown)
        elements = md.md_elements

        variants = elements['code']['variants']
        assert isinstance(variants, list)
        assert variants == ['bash', 'python']  # Should be sorted

    def test_none_values_in_variants(self):
        """Test handling of None values in variants (e.g., code without language)."""
        markdown = """
```python
code_with_lang
```

```
code_without_lang
```
"""
        md = Markdown(markdown)
        elements = md.md_elements

        variants = elements['code']['variants']
        assert isinstance(variants, list)
        assert 'python' in variants
        assert None in variants
        # None should be at the end after sorting
        assert variants.index('python') < variants.index(None)

    def test_comprehensive_document(self):
        """Test with a comprehensive document containing all element types."""
        markdown = """
---
title: Comprehensive Test
author: Test Author
---

# Main Title

## Section A

- [x] Task 1
  - [ ] Subtask
- Regular item

### Code Examples

```python
def example():
    return True
```

| Feature | Status |
|---------|--------|
| A       | Done   |

> Important note
>> Nested note

Term
: Definition

---

## Section B

Paragraph content.
"""
        md = Markdown(markdown)
        elements = md.md_elements

        # Verify all major element types are detected
        expected_elements = {'metadata', 'header', 'list', 'code', 'table', 'blockquote', 'def_list', 'separator', 'paragraph'}
        assert set(elements.keys()) == expected_elements

        # Verify some key statistics
        assert elements['header']['count'] == 4
        assert elements['header']['summary']['levels'] == {1: 1, 2: 2, 3: 1}
        assert 'task' in elements['list']['variants']
        assert elements['metadata']['variants'] == ['2_fields']
