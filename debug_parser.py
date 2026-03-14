from docx import Document
import re

doc = Document('knowlodge_base/Türkçe_Taksonomi.docx')

current_cause = None
waiting_for_definition = False

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    
    if not text:
        continue
    
    # Kod pattern'i
    code_match = re.match(r'^([A-Z]\d+\.\d+)\s+(.+)$', text)
    
    if code_match:
        code = code_match.group(1)
        if code == 'A1.1':
            print(f"=== {code} BAŞLADI (paragraf {i}) ===")
            current_cause = {'code': code, 'selection_criteria': None, 'typical_examples': []}
            waiting_for_definition = True
    
    elif current_cause and current_cause['code'] == 'A1.1':
        print(f"\nParagraf {i}:")
        print(f"  Text: [{text[:80]}...]" if len(text) > 80 else f"  Text: {text}")
        print(f"  waiting_for_definition: {waiting_for_definition}")
        print(f"  startswith('Seç eğer:'): {text.startswith('Seç eğer:')}")
        print(f"  'Seç eğer:' in text: {'Seç eğer:' in text}")
        
        # "Seç eğer:" kontrolü
        if text.startswith('Seç eğer:') or 'Seç eğer:' in text:
            print("  ✓ Seç eğer bulundu!")
            waiting_for_definition = False
            
            criteria_text = text.split('Seç eğer:')[1].strip()
            print(f"  criteria_text: [{criteria_text[:80]}...]" if len(criteria_text) > 80 else f"  criteria_text: {criteria_text}")
            
            if '→ Tipik:' in criteria_text:
                parts = criteria_text.split('→ Tipik:')
                current_cause['selection_criteria'] = parts[0].strip()
                if len(parts) > 1:
                    examples_text = parts[1].strip()
                    if examples_text:
                        current_cause['typical_examples'].append(examples_text)
                print(f"  ✓ selection_criteria: {current_cause['selection_criteria'][:50]}...")
                print(f"  ✓ typical_examples: {len(current_cause['typical_examples'])} örnek")
            else:
                current_cause['selection_criteria'] = criteria_text
                print(f"  ✓ selection_criteria (tipik yok): {current_cause['selection_criteria'][:50]}...")
        
        # Definition kontrolü
        elif waiting_for_definition and not text.startswith('→'):
            print("  ✓ Definition bulundu!")
            waiting_for_definition = False
        
        # A1.2 başladıysa dur
        if 'A1.2' in text:
            print("\n=== A1.2 BAŞLADI, A1.1 BİTTİ ===")
            print(f"\nFinal A1.1:")
            print(f"  selection_criteria: {current_cause['selection_criteria']}")
            print(f"  typical_examples: {current_cause['typical_examples']}")
            break
