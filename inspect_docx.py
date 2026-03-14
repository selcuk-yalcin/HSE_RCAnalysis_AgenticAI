from docx import Document

doc = Document('knowlodge_base/Türkçe_Taksonomi.docx')

print("İlk 30 paragraf:\n")
for i, para in enumerate(doc.paragraphs[:30]):
    if para.text.strip():
        print(f"{i:3d}: {para.text}")
        print()
