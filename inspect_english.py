from docx import Document

doc = Document('knowlodge_base/İngilizce_Taksonomi.docx')

print("İngilizce Taksonomi - İlk 30 paragraf:\n")
for i, para in enumerate(doc.paragraphs[:30]):
    if para.text.strip():
        print(f"{i:3d}: {para.text}")
        print()
