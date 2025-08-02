import docx

doc = docx.Document('ExamFormatExport-Finished.docx')
full_text = []
for para in doc.paragraphs:
    full_text.append(para.text)

text = '\n'.join(full_text)
print('=== FIRST 2000 CHARACTERS ===')
print(text[:2000])
print('\n=== LOOKING FOR MULTIPLE CHOICE SECTION ===')
if 'MULTIPLE' in text.upper():
    start = text.upper().find('MULTIPLE')
    print(text[start:start+1500])
else:
    print('MULTIPLE not found, looking for questions...')
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip() and any(char.isdigit() for char in line[:5]):
            print(f'Line {i}: {line}')
            if i < len(lines) - 5:
                for j in range(1, 6):
                    print(f'  +{j}: {lines[i+j]}')
            break
