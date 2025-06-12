from typing import Optional
import re

def split_diff(diff: str, max_length: int, ignore_files: Optional[list[str]] = None) -> list[str]:
    """
    Split a git diff into chunks that are smaller than the specified maximum length.
    
    The function preserves the structure of the diff by keeping related changes together.
    If a single block of changes exceeds the maximum length, it will be kept as a single chunk.
    
    Args:
        diff (str): The git diff content to split
        max_length (int): Maximum length for each chunk in characters
        ignore_files (Optional[list[str]]): List of file names to exclude from the diff chunks
        
    Returns:
        list[str]: List of diff chunks, each smaller than max_length
    """
    if ignore_files is None:
        ignore_files = []
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
        # Skip blocks for ignored files
        files_in_block = get_files_from_diff(block)
        if any( any(ignore_file in filename for filename in files_in_block) for ignore_file in ignore_files ):
            continue
            
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
    Extract file names from a git diff text.
    
    Args:
        diff_text (str): The git diff content to analyze
        
    Returns:
        list[str]: List of unique file names found in the diff
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
