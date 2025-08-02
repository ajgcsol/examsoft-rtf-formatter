#!/usr/bin/env python3

import sys
sys.path.append('.')
import re

from examsoft_formatter_updated import extract_text_from_rtf, parse_exam_content

# Debug question parsing
with open('Final SU2025 rtf.rtf', 'rb') as f:
    text = extract_text_from_rtf(f)

instructions_text, questions_text = parse_exam_content(text)

# Split into individual questions - look for numbered patterns
question_blocks = re.split(r'\n\s*(\d+)\.\s+', questions_text)

print(f"Total question blocks: {len(question_blocks)}")
print(f"Question blocks (every other one starting from 1): {question_blocks[1::2][:10]}")

# Look at the last few questions
for i in range(len(question_blocks) - 10, len(question_blocks), 2):
    if i >= 1 and i + 1 < len(question_blocks):
        q_num = question_blocks[i]
        q_content = question_blocks[i + 1]
        print(f"\n=== Question {q_num} ===")
        print(f"Content length: {len(q_content)}")
        print(f"First 200 chars: {q_content[:200]}")
        print(f"Contains 'Type: E'?: {'Type: E' in q_content}")
        print(f"Contains 'Type: E {q_num}'?: {bool(re.search(rf'Type:\s*E\s*{q_num}', q_content))}")
        print(f"Is >= 41?: {int(q_num) >= 41}")

# Look for the essay content specifically
essay_matches = re.findall(r'Type:\s*E\s*\d+', questions_text, re.IGNORECASE)
print(f"\nFound essay markers: {essay_matches}")

# Find all question numbers
all_numbers = re.findall(r'\n\s*(\d+)\.\s+', questions_text)
print(f"All question numbers found: {all_numbers}")
