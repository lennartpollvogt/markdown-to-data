from src.markdown_to_data.to_python.convert_single_line_objects.convert_paragraphs import convert_paragraphs

def test_single_paragraph():
    input_data = [
        {'p': 'This is a simple paragraph', 'indent': 0}
    ]

    expected = [
        {'paragraph': 'This is a simple paragraph', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_multiple_paragraphs():
    input_data = [
        {'p': 'First paragraph', 'indent': 0},
        {'p': 'Second paragraph', 'indent': 0},
        {'p': 'Third paragraph', 'indent': 0}
    ]

    expected = [
        {'paragraph': 'First paragraph', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Second paragraph', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Third paragraph', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_empty_paragraphs():
    input_data = [
        {'p': '', 'indent': 0},
        {'p': 'Some content', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    expected = [
        {'paragraph': '', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Some content', 'start_line': 0, 'end_line': 0},
        {'paragraph': '', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_mixed_content():
    input_data = [
        {'h1': 'Header', 'indent': 0},
        {'p': 'A paragraph', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'p': 'Another paragraph', 'indent': 0}
    ]

    expected = [
        {'h1': 'Header', 'indent': 0},
        {'paragraph': 'A paragraph', 'start_line': 0, 'end_line': 0},
        {'hr': '---', 'indent': 0},
        {'paragraph': 'Another paragraph', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_no_paragraphs():
    input_data = [
        {'h1': 'Header', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'h2': 'Subheader', 'indent': 0}
    ]

    expected = input_data.copy()

    assert convert_paragraphs(input_data) == expected

def test_empty_input():
    input_data = []
    expected = []
    assert convert_paragraphs(input_data) == expected

def test_paragraphs_with_special_characters():
    input_data = [
        {'p': 'Paragraph with *asterisks* and _underscores_', 'indent': 0},
        {'p': 'Paragraph with [links](http://example.com)', 'indent': 0},
        {'p': 'Paragraph with `code`', 'indent': 0}
    ]

    expected = [
        {'paragraph': 'Paragraph with *asterisks* and _underscores_', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Paragraph with [links](http://example.com)', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Paragraph with `code`', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_paragraphs_with_different_indents():
    input_data = [
        {'p': 'No indent', 'indent': 0},
        {'p': 'Single indent', 'indent': 1},
        {'p': 'Double indent', 'indent': 2}
    ]

    expected = [
        {'paragraph': 'No indent', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Single indent', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Double indent', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected

def test_complex_document_structure():
    input_data = [
        {'h1': 'Title', 'indent': 0},
        {'p': '', 'indent': 0},
        {'p': 'Introduction paragraph', 'indent': 0},
        {'p': '', 'indent': 0},
        {'h2': 'Section', 'indent': 0},
        {'p': 'Section content', 'indent': 0},
        {'hr': '---', 'indent': 0},
        {'p': 'Conclusion', 'indent': 0}
    ]

    expected = [
        {'h1': 'Title', 'indent': 0},
        {'paragraph': '', 'start_line': 0, 'end_line': 0},
        {'paragraph': 'Introduction paragraph', 'start_line': 0, 'end_line': 0},
        {'paragraph': '', 'start_line': 0, 'end_line': 0},
        {'h2': 'Section', 'indent': 0},
        {'paragraph': 'Section content', 'start_line': 0, 'end_line': 0},
        {'hr': '---', 'indent': 0},
        {'paragraph': 'Conclusion', 'start_line': 0, 'end_line': 0}
    ]

    assert convert_paragraphs(input_data) == expected
