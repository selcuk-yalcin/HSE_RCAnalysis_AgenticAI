from docx import Document

doc = Document('knowlodge_base/Türkçe_Taksonomi.docx')

found = False
for para in doc.paragraphs:
    text = para.text.strip()
    if text.startswith('Seç eğer:') and not found:
        found = True
        print('Tam metin:')
        print(repr(text))
        print()
        print('→ Tipik: var mı?', '→ Tipik:' in text)
        print()
        criteria_text = text.split('Seç eğer:')[1].strip()
        print('criteria_text:')
        print(repr(criteria_text))
        print()
        print('→ Tipik: var mı (criteria_text)?', '→ Tipik:' in criteria_text)
        break
