from docx import Document
import re

doc = Document('knowlodge_base/Türkçe_Taksonomi.docx')

in_exclusion = False
count = 0

for para in doc.paragraphs:
    text = para.text.strip()
    text_normalized = text.replace('\xa0', ' ').replace('\n', ' ')
    
    if 'Bu değil eğer:' in text:
        in_exclusion = True
        print("=== EXCLUSION BÖLÜMÜ BAŞLADI ===\n")
        continue
    
    if in_exclusion:
        if text and not text.startswith('A'):  # Yeni cause başlamadıysa
            print(f"Satır {count}:")
            print(f"  Original: {repr(text[:80])}")
            print(f"  Normalized: {repr(text_normalized[:80])}")
            print(f"  '→' var mı: {'→' in text}")
            print(f"  '→' var mı (normalized): {'→' in text_normalized}")
            
            if '→' in text_normalized:
                parts = text_normalized.split('→')
                condition = parts[0].strip()
                redirect_info = parts[1].strip() if len(parts) > 1 else ''
                redirect_match = re.search(r'([A-Z]\d+\.\d+)', redirect_info)
                redirect_code = redirect_match.group(1) if redirect_match else ''
                
                print(f"  ✓ Condition: {condition[:50]}")
                print(f"  ✓ Redirect code: {redirect_code}")
                print(f"  ✓ Redirect info: {redirect_info[:50]}")
            print()
            
            count += 1
            if count > 8:
                break
        elif 'A1.2' in text:
            print("=== YENİ CAUSE BAŞLADI ===")
            break
