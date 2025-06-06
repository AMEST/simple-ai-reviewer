import re

def split_diff(diff: str, max_length: int) -> list[str]:
    if not diff:
        return []
    blocks = []
    current_block = []
    lines = diff.splitlines(keepends=True)
    for line in lines:
        if line.startswith('diff --git'):
            if current_block:
                blocks.append(''.join(current_block))
                current_block = []
        current_block.append(line)
    if current_block:
        blocks.append(''.join(current_block))
    chunks = []
    current_chunk = []
    current_size = 0

    for block in blocks:
        block_len = len(block)
        if block_len > max_length:
            if current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            chunks.append(block)
        else:
            if current_size + block_len <= max_length:
                current_chunk.append(block)
                current_size += block_len
            else:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [block]
                current_size = block_len
    if current_chunk:
        chunks.append(''.join(current_chunk))
    return chunks

def get_files_from_diff(diff_text):
    """
    Extracts file names from a diff text.

    Args:
    diff_text: The diff text as a string.

    Returns:
    A list of file names.
    """
    files = []
    for line in diff_text.splitlines():
        match = re.match(r"^diff --git a/(.*) b/(.*)$", line)
        if match:
            files.extend([match.group(1), match.group(2)])
        match = re.match(r"^rename from (.*)$", line)
        if match:
            files.append(match.group(1))
        match = re.match(r"^rename to (.*)$", line)
        if match:
            files.append(match.group(1))
    return list(set(files))  # Remove duplicates
