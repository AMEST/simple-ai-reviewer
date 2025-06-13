import re
import json

def extract_json_blocks(text: str) -> list[str]:
    """
    Extracts all JSON blocks from text.
    Finds lines starting with { or [ and matching closing characters.
    
    Args:
        text: Text containing JSON blocks
    
    Returns:
        List of found JSON strings (may be empty)
    """
    json_blocks = []
    stack = []
    start_index = -1
    in_string = False
    escape_char = False # Flag to track escaped characters
    for i, char in enumerate(text):
        if char == '"' and not escape_char:
            in_string = not in_string
        elif char == '\\' and in_string:
            escape_char = not escape_char 
            continue
        if not in_string:
            if char in '{[':
                if not stack:  # Start of a new JSON block
                    start_index = i
                stack.append(char)
            elif char in '}]' and stack:
                opening = stack.pop()
                if (opening == '{' and char == '}') or (opening == '[' and char == ']'):
                    if not stack:  # Closing the JSON block
                        json_blocks.append(text[start_index:i+1])
        escape_char = False
    # Validation of extracted blocks
    valid_blocks = []
    for block in json_blocks:
        try:
            # Let's try to remove possible Markdown framing
            clean_block = re.sub(r'^```(json)?\s*|\s*```$', '', block, flags=re.IGNORECASE).strip()
            fix_json = re.sub(r'("(?:\\?.)*?")|,\s*([]}])', r'\1\2', clean_block.replace("\n",""))
            # Let's check that this is valid JSON
            json.loads(fix_json)
            valid_blocks.append(fix_json)
        except (json.JSONDecodeError, ValueError):
            continue
    return valid_blocks
