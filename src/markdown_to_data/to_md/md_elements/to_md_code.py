from typing import Dict, Any, Text, Optional

def code_data_to_md(data: Dict[str, Any]) -> Text:
    """Convert code block data to markdown format."""
    if not isinstance(data, dict) or 'content' not in data:
        return ''

    # Get the language specification (if any)
    language = data.get('language', '')
    content = str(data['content'])

    # Format the code block
    # If language is None, convert it to empty string
    language = '' if language is None else str(language)

    # Construct the code block
    return f"```{language}\n{content}\n```"
