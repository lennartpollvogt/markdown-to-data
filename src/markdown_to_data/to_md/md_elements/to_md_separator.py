from typing import Dict, Any, Text

def separator_data_to_md(data: Dict[str, Any]) -> Text:
    if not isinstance(data, dict) or not data:
        return ''

    return str(data.items())
