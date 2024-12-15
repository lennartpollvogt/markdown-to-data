from src.markdown_to_data.to_python.convert_single_line_objects.convert_paragraphs import convert_paragraphs

def test_single_paragraph():
    input_data = [
        {'p': 'This is a simple paragraph', 'indent': 0}
    ]

    expected = [
        {'paragraph': 'This is a simple paragraph'}
    ]

    assert convert_paragraphs(input_data) == expected

def test_multiple_paragraphs():
    input_data = [
        {'p': 'First paragraph', 'indent': 0},
        {'p': 'Second paragraph', 'indent': 0},
        {'p': 'Third paragraph', 'indent': 0}
    ]

    expected = [
        {'paragraph': 'First paragraph'},
        {'paragraph': 'Second paragraph'},
        {'paragraph': 'Third paragraph'}
    ]

    assert convert_paragraphs(input_data) == expected

def test_empty_paragraphs():
    input_data = [
        {'p': '', 'indent': 0},
        {'p': 'Some content', 'indent': 0},
        {'p': '', 'indent': 0}
    ]

    expected = [
        {'paragraph': ''},
        {'paragraph': 'Some content'},
        {'paragraph': ''}
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
        {'paragraph': 'A paragraph'},
        {'hr': '---', 'indent': 0},
        {'paragraph': 'Another paragraph'}
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
        {'paragraph': 'Paragraph with *asterisks* and _underscores_'},
        {'paragraph': 'Paragraph with [links](http://example.com)'},
        {'paragraph': 'Paragraph with `code`'}
    ]

    assert convert_paragraphs(input_data) == expected

def test_paragraphs_with_different_indents():
    input_data = [
        {'p': 'No indent', 'indent': 0},
        {'p': 'Single indent', 'indent': 1},
        {'p': 'Double indent', 'indent': 2}
    ]

    expected = [
        {'paragraph': 'No indent'},
        {'paragraph': 'Single indent'},
        {'paragraph': 'Double indent'}
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
        {'paragraph': ''},
        {'paragraph': 'Introduction paragraph'},
        {'paragraph': ''},
        {'h2': 'Section', 'indent': 0},
        {'paragraph': 'Section content'},
        {'hr': '---', 'indent': 0},
        {'paragraph': 'Conclusion'}
    ]

    assert convert_paragraphs(input_data) == expected
