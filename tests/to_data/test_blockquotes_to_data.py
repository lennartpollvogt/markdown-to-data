from re import M
import pytest
from markdown_to_data.to_data.joining_and_extraction.extraction import MarkdownExtractor
from markdown_to_data.markdown_to_data import Markdown

# pytest test_blockquotes.py


@pytest.fixture
def mapper():
    """Fixture to initialize the MarkdownMapper instance."""
    return MarkdownExtractor()

def test_extract_md_blockquote_1(mapper):
    blockquote_1 = '''
>>
> Note: this is a blockquote
>

>> With multiline
'''
    output_1 = {
        'blockquote': [
            'Note: this is a blockquote'
        ]
    }
    assert mapper._extract_md_blockquote(blockquote_1) == output_1

def test_extract_md_blockquote_2(mapper):
    blockquote_2 = '''
Text with > in it
> Note: this is a blockquote
>

>> With multiline
'''
    output_2 = {
        'blockquote': [
            'Note: this is a blockquote'
        ]
    }
    assert mapper._extract_md_blockquote(blockquote_2) == output_2

def test_extract_md_blockquote_3(mapper):
    blockquote_3 = '''
Text
> Note: this is a blockquote
>
>> With multiline
'''
    output_3 = {
        'blockquote': [
            {
                'Note: this is a blockquote': [
                    'With multiline'
                ]
            }
        ]
    }
    assert mapper._extract_md_blockquote(blockquote_3) == output_3

def test_extract_md_blockquote_4(mapper):
    blockquote_4 = '''
Text
> Note: this is a blockquote
>>
>>> With multiline
'''
    output_4 = {
        'blockquote': [
            {
                'Note: this is a blockquote': [
                    'With multiline'
                ]
            }
        ]
    }
    assert mapper._extract_md_blockquote(blockquote_4) == output_4

def test_multiple_consecutive_blockquotes(mapper):
    input_text = '''
> First blockquote
>
> Second blockquote
'''
    expected_output = {
        'blockquote': [
            'First blockquote',
            'Second blockquote'
        ]
    }
    assert mapper._extract_md_blockquote(input_text) == expected_output

def test_nested_blockquote_with_empty_lines(mapper):
    input_text = '''
> Top-level quote
>
>> Nested quote
>>
>>> Deeply nested quote
'''
    expected_output = {
        'blockquote': [
            {
                'Top-level quote': [
                    {
                        'Nested quote': [
                            'Deeply nested quote'
                        ]
                    }
                ]
            }
        ]
    }
    assert mapper._extract_md_blockquote(input_text) == expected_output

def test_nested_blockquote_with_empty_lines_(mapper):
    input_text = '''
> Top-level quote
>
>> Nested quote
>>> Deeply nested quote
'''
    expected_output = {
        'blockquote': [
            {
                'Top-level quote': [
                    {
                        'Nested quote': [
                            'Deeply nested quote'
                        ]
                    }
                ]
            }
        ]
    }
    assert mapper._extract_md_blockquote(input_text) == expected_output

def test_markdown_class_with_blockquote():
    input_text = '''
> a nested blockquote
> with multiline
>> the nested part
> last line of the blockquote
'''

    expected_output_list = [
        {
            'blockquote': [
                'a nested blockquote',
                {
                    'with multiline': [
                        'the nested part'
                    ]
                },
                'last line of the blockquote'
            ]
        }
    ]
    expected_output_dict = {
        'blockquote': [
            'a nested blockquote',
            {
                'with multiline': [
                    'the nested part'
                ]
            },
            'last line of the blockquote'
        ]
    }

    markdown = Markdown(input_text)
    assert markdown.md_list == expected_output_list
    assert markdown.md_dict == expected_output_dict


def test_markdown_class_with_multiple_blockquotes():
    input_text = '''
> a single blockquote

> a nested blockquote
> with multiline
>> the nested part
> last line of the blockquote
'''

    expected_output_list = [
        {
            'blockquote': ['a single blockquote']
        },
        {
            'blockquote': [
                'a nested blockquote',
                {
                    'with multiline': [
                        'the nested part'
                    ]
                },
                'last line of the blockquote'
            ]
        }
    ]
    expected_output_dict = {
        'blockquote': ['a single blockquote'],
        'blockquote2': [
            'a nested blockquote',
            {
                'with multiline': [
                    'the nested part'
                ]
            },
            'last line of the blockquote'
        ]
    }

    markdown = Markdown(input_text)
    assert markdown.md_list == expected_output_list
    assert markdown.md_dict == expected_output_dict
