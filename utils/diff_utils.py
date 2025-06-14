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

def get_changed_lines(diff_text : str) -> dict:
    """
    Analyzes diff text and returns dictionary with information about actually changed lines (+/-) for each file.

    Args:
    diff_text (str): Diff text in git diff format

    Returns:
    dict: Dictionary where keys are file names, values are dictionaries with keys:
    - 'added': list of added lines
    - 'removed': list of removed lines
    """
    file_changes = {}
    current_file = None
    current_hunk = None
    
    # Regular expressions
    file_header_re = re.compile(r'^diff --git a/(.*?) b/(.*?)$', re.MULTILINE)
    hunk_header_re = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', re.MULTILINE)
    changed_line_re = re.compile(r'^([+-])(?!\+\+ |--- )(.+)', re.MULTILINE)
    
    for line in diff_text.split('\n'):
        # Check for start of new file
        file_match = file_header_re.match(line)
        if file_match:
            current_file = file_match.group(2)
            file_changes[current_file] = {'added': [], 'removed': []}
            continue
        
        # Check for start of new hunk
        hunk_match = hunk_header_re.match(line)
        if hunk_match and current_file:
            old_start = int(hunk_match.group(1))
            new_start = int(hunk_match.group(3))
            current_hunk = {
                'old_line': old_start,
                'new_line': new_start,
                'current_old': old_start,
                'current_new': new_start
            }
            continue
        
        # Analyze changed lines
        if current_file and current_hunk:
            line_type_match = changed_line_re.match(line)
            if line_type_match:
                line_type = line_type_match.group(1)
                content = line_type_match.group(2)
                
                if line_type == '+':
                    file_changes[current_file]['added'].append(current_hunk['new_line'])
                    current_hunk['new_line'] += 1
                elif line_type == '-':
                    file_changes[current_file]['removed'].append(current_hunk['old_line'])
                    current_hunk['old_line'] += 1
            else:
                # Normal line (no + or -) - increment both counters
                if not line.startswith('---') and not line.startswith('+++'):
                    current_hunk['old_line'] += 1
                    current_hunk['new_line'] += 1
    
    return file_changes

def annotate_diff_with_line_numbers(diff_text):
    """
    Adds correct line numbers to the diff text.

    Args:
        diff_text(str): The original diff text

    Returns:
        str: The diff text with line numbers added
    """
    result = []
    old_line = 0
    new_line = 0
    in_hunk = False
    
    for line in diff_text.split('\n'):
        # Processing the beginning of a new file
        if line.startswith('diff --git'):
            result.append(line)
            old_line = 0
            new_line = 0
            in_hunk = False
            continue
        
        # Processing file headers (--- / +++)
        if line.startswith('--- ') or line.startswith('+++ '):
            result.append(line)
            continue
        
        # Processing the beginning of the hunk
        if line.startswith('@@ '):
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                old_line = int(match.group(1))
                new_line = int(match.group(3))
            in_hunk = True
            result.append(line)
            continue
        
        if not in_hunk:
            result.append(line)
            continue
        
        # Context line (unchanged)
        if line.startswith(' '):
            # Context line (unchanged)
            annotated = f"{old_line:3} | {line}"
            old_line += 1
            new_line += 1
        elif line.startswith('-'):
            # Deleted line (only in old file)
            annotated = f"{old_line:3} | {line}"
            old_line += 1
        elif line.startswith('+'):
            # Added line (only in new file)
            annotated = f"{new_line:3} | {line}"
            new_line += 1
        elif line.startswith('\\'):
            # Special line (No newline at end of file)
            annotated = f"    | {line}"
        else:
            annotated = line
        
        result.append(annotated)
    
    return '\n'.join(result)