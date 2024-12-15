# pytest tests/to_data/classification/test_classify_md_definition_list.py

import pytest
from src.markdown_to_data.to_python.classification.md_classification.classify_md_definition_list import (
    is_definition_list_item,
    process_definition_list
)

class TestDefinitionListClassification:
    def test_basic_definition_list_item(self):
        """Test basic definition list item detection"""
        # Test definition description with previous term
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, result = is_definition_list_item(': Description', previous_dict)
        assert is_def is True
        assert 'convert_previous' in result
        assert result['convert_previous']['dt'] == 'Term'
        assert result['current']['dd'] == 'Description'

    def test_multiple_descriptions(self):
        """Test multiple descriptions for same term"""
        # First description
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, result1 = is_definition_list_item(': First description', previous_dict)
        assert is_def is True

        # Second description
        previous_dict = result1['current']
        is_def, result2 = is_definition_list_item(': Second description', previous_dict)
        assert is_def is True
        assert result2['dd'] == 'Second description'

    def test_indentation_preservation(self):
        """Test if indentation is properly preserved"""
        previous_dict = {'p': 'Term', 'indent': 2}
        is_def, result = is_definition_list_item('    : Description', previous_dict)
        assert result['current']['indent'] == 4

    def test_invalid_definition_items(self):
        """Test cases that should not be recognized as definition items"""
        # No previous dictionary
        is_def, result = is_definition_list_item(': Description', None)
        assert is_def is False

        # Line doesn't start with ':'
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, result = is_definition_list_item('Not a description', previous_dict)
        assert is_def is False

        # Previous line is empty
        previous_dict = {'p': '', 'indent': 0}
        is_def, result = is_definition_list_item(': Description', previous_dict)
        assert is_def is False

    def test_process_definition_list(self):
        """Test processing complete definition lists"""
        lines = [
            'Term 1',
            ': Description 1.1',
            ': Description 1.2',
            'Term 2',
            ': Description 2'
        ]

        result, last_idx = process_definition_list(lines, 0)
        assert len(result) == 5
        assert result[0]['dt'] == 'Term 1'
        assert result[1]['dd'] == 'Description 1.1'
        assert result[2]['dd'] == 'Description 1.2'
        assert result[3]['dt'] == 'Term 2'
        assert result[4]['dd'] == 'Description 2'

    def test_indented_definition_list(self):
        """Test indented definition lists"""
        lines = [
            '  Term',
            '  : Description'
        ]

        result, last_idx = process_definition_list(lines, 0)
        assert result[0]['indent'] == 2
        assert result[1]['indent'] == 2

    def test_complex_definition_list(self):
        """Test more complex definition list scenarios"""
        markdown = [
            'Term of definition list',
            ': item of definition list',
            ': second item of definition list',
            'A second term of a second definition list',
            ': Item of second def list',
            ': Item of second def list'
        ]

        result, last_idx = process_definition_list(markdown, 0)
        assert len(result) == 6
        assert result[0]['dt'] == 'Term of definition list'
        assert len([item for item in result if 'dd' in item]) == 4  # Should have 4 descriptions

    def test_edge_cases(self):
        """Test various edge cases"""
        # Empty lines between definitions
        lines = [
            'Term',
            '',
            ': Description'
        ]
        result, last_idx = process_definition_list(lines, 0)
        assert len(result) == 1

        # Description with multiple colons
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, result = is_definition_list_item(': Description: with: colons', previous_dict)
        assert is_def is True
        assert result['current']['dd'] == 'Description: with: colons'

        # Term with colon
        previous_dict = {'p': 'Term: with colon', 'indent': 0}
        is_def, result = is_definition_list_item(': Description', previous_dict)
        assert is_def is True
        assert result['convert_previous']['dt'] == 'Term: with colon'

    def test_malformed_input(self):
        """Test handling of malformed input"""
        # Description without term
        lines = [': Description without term']
        result, last_idx = process_definition_list(lines, 0)
        assert len(result) == 1

        # Empty description
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, result = is_definition_list_item(':', previous_dict)
        assert is_def is False
        assert result == {}

    @pytest.mark.parametrize("input_line,expected_is_def", [
        (': Normal description', True),
        ('Not a description', False),
        (':No space after colon', False),
        ('  : Indented description', True),
        (': ', False),
        (':', False),
        ('', False)
    ])
    def test_various_input_formats(self, input_line, expected_is_def):
        """Test various input formats with parametrize"""
        previous_dict = {'p': 'Term', 'indent': 0}
        is_def, _ = is_definition_list_item(input_line, previous_dict)
        assert is_def == expected_is_def
