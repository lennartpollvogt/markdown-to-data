import pytest
from markdown_to_data.utils.joining_and_extraction.extraction import MarkdownExtractor

# pytest test_blockquotes.py


@pytest.fixture
def mapper():
    """Fixture to initialize the MarkdownMapper instance."""
    return MarkdownExtractor()

def test_extract_md_blockquote_1(mapper):
    def_list_1 = '''
>>
> Note: this is a blockquote
>

>> With multiline
'''
    output_1 = [
        ["Note: this is a blockquote"],
    ]
    assert mapper._extract_md_blockquote(def_list_1) == output_1

def test_extract_md_blockquote_2(mapper):
    def_list_2 = '''
Text with > in it
> Note: this is a blockquote
>

>> With multiline
'''
    output_2 = [
        ["Note: this is a blockquote"]
    ]
    assert mapper._extract_md_blockquote(def_list_2) == output_2

def test_extract_md_blockquote_3(mapper):
    def_list_3 = '''
Text
> Note: this is a blockquote
>
>> With multiline
'''
    output_3 = [
        ["Note: this is a blockquote"],
        [["With multiline"]]
    ]
    assert mapper._extract_md_blockquote(def_list_3) == output_3

def test_extract_md_blockquote_4(mapper):
    def_list_4 = '''
Text
> Note: this is a blockquote
>>
>>> With multiline
'''
    output_4 = [
        ["Note: this is a blockquote"], 
        [[["With multiline"]]]
    ]
    assert mapper._extract_md_blockquote(def_list_4) == output_4

def test_empty_input(mapper):
    assert mapper._extract_md_blockquote("") == []

def test_no_blockquote(mapper):
    assert mapper._extract_md_blockquote("No blockquote here") == []

def test_multiple_consecutive_blockquotes(mapper):
    input_text = '''
> First blockquote
>
> Second blockquote
'''
    expected_output = [
        ["First blockquote"],
        ["Second blockquote"]
    ]
    assert mapper._extract_md_blockquote(input_text) == expected_output

def test_nested_blockquote_with_empty_lines(mapper):
    input_text = '''
> Top-level quote
>
>> Nested quote
>>
>>> Deeply nested quote
'''
    expected_output = [
        ["Top-level quote"],
        [["Nested quote"]],
        [[["Deeply nested quote"]]]
    ]
    assert mapper._extract_md_blockquote(input_text) == expected_output

def test_nested_blockquote_with_empty_lines_(mapper):
    input_text = '''
> Top-level quote
>
>> Nested quote
>>> Deeply nested quote
'''
    expected_output = [
        ["Top-level quote"],
        [["Nested quote"]],
        [[["Deeply nested quote"]]]
    ]
    assert mapper._extract_md_blockquote(input_text) == expected_output