from typing import Dict, Any, Text

def code_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert code block data to markdown format."""
    if not isinstance(data, dict) or 'code' not in data:
        return ''

    code_data = data['code']

    # Validate code structure
    # TODO: could be pydantic model
    if not isinstance(code_data, dict) or \
       'language' not in code_data or \
       'content' not in code_data:
        return ''

    # Get the language specification (if any)
    language = code_data['language']
    content = str(code_data['content'])

    # Format the code block
    # If language is None, convert it to empty string
    language = '' if language is None else str(language)

    # Construct the code block
    return f"```{language}\n{content}\n```"
