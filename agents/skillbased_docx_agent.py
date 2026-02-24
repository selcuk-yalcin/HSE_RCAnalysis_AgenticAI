"""
SkillBasedDocxAgent V2 - OpenRouter Claude API + python-docx ile Profesyonel HSE Raporu
========================================================================================

MİMARİ:
  RootCauseAgentV2 → JSON → OpenRouter Claude API (içerik üretir) → python-docx (DOCX oluşturur)

AVANTAJLAR:
  - OpenRouter üzerinden Claude kullanır
  - python-docx ile kesin, güvenilir DOCX oluşturma
  - 18-20 sayfalık profesyonel rapor
  - HSE renk şeması: koyu mavi, kırmızı, turuncu, yeşil kutular/tablolar

GEREKSİNİMLER:
  pip install requests python-docx

ORTAM DEĞİŞKENLERİ:
  OPENROUTER_API_KEY = "sk-or-v1-..."
"""

import requests
import json
import os
import sys
import re
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# python-docx imports
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ─────────────────────────────────────────────────────────────────────────────
# RENK PALETİ
# ─────────────────────────────────────────────────────────────────────────────
COLOR = {
    "dark_blue":  RGBColor(0x1B, 0x3A, 0x5C),
    "mid_blue":   RGBColor(0x2E, 0x6D, 0xA4),
    "light_blue": RGBColor(0xD6, 0xE4, 0xF0),
    "red":        RGBColor(0xC0, 0x39, 0x2B),
    "orange":     RGBColor(0xE6, 0x7E, 0x22),
    "green":      RGBColor(0x27, 0xAE, 0x60),
    "light_grey": RGBColor(0xF5, 0xF5, 0xF5),
    "white":      RGBColor(0xFF, 0xFF, 0xFF),
    "black":      RGBColor(0x00, 0x00, 0x00),
    "dark_grey":  RGBColor(0x44, 0x44, 0x44),
}

ROOT_CAUSE_COLORS = [
    COLOR["red"],
    COLOR["orange"],
    COLOR["green"],
    COLOR["mid_blue"],
]


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDE CONTENT PROMPT
# ─────────────────────────────────────────────────────────────────────────────
CONTENT_SYSTEM_PROMPT = """Sen bir HSE (İş Sağlığı ve Güvenliği) uzmanısın.
Sana bir kök neden analizi ham verisi gelecek.
Bu veriyi kullanarak raporun TÜM İÇERİĞİNİ üreteceksin.

Sadece JSON formatında çıktı ver. Başka hiçbir şey yazma.

Üretmen gereken JSON yapısı:
{
  "cover": {
    "title": "KÖK NEDEN ANALİZİ RAPORU",
    "subtitle": "-----------",
    "ref_no": "...",
    "date": "...",
    "location": "...",
    "incident_type": "...",
    "confidentiality": "GİZLİ - SADECE YETKİLİ PERSONELİN ERİŞİMİNE AÇIKTIR",
    "incident_summary_short": "2-3 cümle olay özeti"
  },
  "executive_summary": {
    "what_happened": "Ne oldu - 2 paragraf detaylı (Yönetici özeti için kısa ve öz olmalı, Olay Detayları'nda zaten uzun versiyon var)",
    "where_happened": "Nerede oldu - kısa ve öz (Olay Detayları'nda detaylı versiyon var)",
    "who_affected": "Kimler etkilendi - özet (Detay Olay Bilgileri'nde zaten var)",
    "immediate_response": "İlk müdahale nasıl yapıldı - 1-2 cümle özet (Detay zaman çizelgesinde var)",
    "key_findings": [
      "Temel Bulgu 1 - kısa madde halinde",
      "Temel Bulgu 2 - kısa madde halinde",
      "Temel Bulgu 3 - kısa madde halinde"
    ],
    "immediate_actions": [
      {"action": "Acil eylem 1", "responsible": "Sorumlu", "status": "Tamamlandı"},
      {"action": "Acil eylem 2", "responsible": "Sorumlu", "status": "Devam ediyor"}
    ]
  },
  "incident_details": {
    "info_table": {
      "Olay Referans No": "...",
      "Tarih": "...",
      "Saat": "...",
      "Lokasyon": "...",
      "Bölüm/Hat": "...",
      "Operatör/Çalışan": "...",
      "Vardiya": "...",
      "Ekipman": "...",
      "Malzeme/Madde": "...",
      "Hava Koşulları": "...",
      "Aydınlatma": "...",
      "Kişisel Koruyucu Ekipman": "..."
    },
    "event_table": {
      "Olay Tipi": "...",
      "Yaralanma/Hasar Durumu": "...",
      "Etkilenen Kişi Sayısı": "...",
      "Hasar Seviyesi": "...",
      "RIDDOR Kapsamında mı": "...",
      "İlk Tanık": "...",
      "Acil Servis Çağrıldı mı": "...",
      "Yatış/Taburculuk": "..."
    },
    "timeline": [
      {"time": "00:00", "event": "Olaydan önce durum açıklaması"},
      {"time": "00:05", "event": "Olayın başlangıcı"},
      {"time": "00:10", "event": "Olay anı"},
      {"time": "00:15", "event": "İlk müdahale"},
      {"time": "00:30", "event": "Acil servis/yönetim bildirim"},
      {"time": "01:00", "event": "Durum kontrolü ve raporlama"}
    ],
    "severity": {
      "actual_harm": "...",
      "potential_harm": "...",
      "investigation_level": "...",
      "riddor": "..."
    }
  },
  "analysis_method": {
    "methodology_description": "Kök neden analizi metodolojisi nedir ve bu olayda nasıl uygulandı - 3 paragraf",
    "five_why_explanation": "5-Why tekniği nasıl uygulandı - 2 paragraf",
    "code_system": [
      {"code": "A", "category": "İnsan Faktörü", "description": "Bilgi eksikliği, beceri yetersizliği, dikkatsizlik, yorgunluk gibi bireysel faktörler"},
      {"code": "B", "category": "Organizasyonel Faktör", "description": "Prosedür eksikliği, iletişim bozukluğu, yönetim kararları, politika yetersizlikleri"},
      {"code": "C", "category": "İş/Görev Faktörü", "description": "Ekipman arızası, tasarım hatası, fiziksel yük, ergonomi sorunları"},
      {"code": "D", "category": "Çevresel Faktör", "description": "Hava koşulları, aydınlatma, gürültü, sıcaklık, alan düzeni"}
    ],
    "team_members": [
      {"name": "HSE Uzmanı", "role": "Baş Araştırmacı", "date": "..."},
      {"name": "Üretim Müdürü", "role": "Departman Temsilcisi", "date": "..."},
      {"name": "Bakım Mühendisi", "role": "Teknik Uzman", "date": "..."},
      {"name": "İK Yöneticisi", "role": "İnsan Kaynakları Temsilcisi", "date": "..."},
      {"name": "Vardiya Amiri", "role": "Operasyonel Tanık", "date": "..."}
    ]
  },
  "branches": [
    {
      "branch_number": 1,
      "branch_title": "KRİTİK FAKTÖR 1 - Ana Başlık",
      "initial_condition": "Bu kritik faktörün başlangıç koşulu ve doğrudan neden açıklaması - 2 paragraf detaylı",
      "direct_cause": "Doğrudan nedenin teknik açıklaması",
      "why_chain": [
        {"number": 1, "question": "Neden oldu?", "answer": "Çünkü detaylı yanıt", "code": "C", "category": "İş/Görev"},
        {"number": 2, "question": "Neden?", "answer": "Çünkü detaylı yanıt", "code": "B", "category": "Organizasyonel"},
        {"number": 3, "question": "Neden?", "answer": "Çünkü detaylı yanıt", "code": "B", "category": "Organizasyonel"},
        {"number": 4, "question": "Neden?", "answer": "Çünkü detaylı yanıt", "code": "D", "category": "Organizasyonel"},
        {"number": 5, "question": "Neden?", "answer": "Çünkü kök neden", "code": "D", "category": "Organizasyonel"}
      ],
      "root_cause_title": "Kök Neden 1 başlığı",
      "root_cause_detail": "Kök nedenin çok detaylı açıklaması - 3-4 cümle",
      "root_cause_code": "D1.4",
      "root_cause_category": "Organizasyonel",
      "organizational_factors": [
        "Organizasyonel faktör 1 - detaylı",
        "Organizasyonel faktör 2 - detaylı",
        "Organizasyonel faktör 3 - detaylı",
        "Organizasyonel faktör 4 - detaylı"
      ]
    }
  ],
  "root_causes": [
    {
      "number": 1,
      "code": "D1.4",
      "title": "Kök Neden Başlığı",
      "category": "Organizasyonel",
      "detailed_description": "3-4 paragraf çok detaylı açıklama",
      "impacts": ["Etki 1", "Etki 2", "Etki 3", "Etki 4"],
      "contributing_organizations": "Hangi organizasyonel birimler bu nedenle ilişkili"
    }
  ],
  "contributing_factors": [
    {"factor_type": "İletişim Eksikliği", "description": "Detaylı açıklama", "impact_level": "Yüksek"},
    {"factor_type": "Eğitim Yetersizliği", "description": "Detaylı açıklama", "impact_level": "Yüksek"},
    {"factor_type": "Yorgunluk/Stres", "description": "Detaylı açıklama", "impact_level": "Orta"},
    {"factor_type": "Ekipman Bakım Eksikliği", "description": "Detaylı açıklama", "impact_level": "Yüksek"},
    {"factor_type": "Prosedür Uyumsuzluğu", "description": "Detaylı açıklama", "impact_level": "Orta"},
    {"factor_type": "Yönetim Denetim Eksikliği", "description": "Detaylı açıklama", "impact_level": "Yüksek"},
    {"factor_type": "Çevresel Koşullar", "description": "Detaylı açıklama", "impact_level": "Düşük"}
  ],
  "corrective_actions": [
    {"no": 1, "action": "Detaylı eylem açıklaması ve beklenen sonucu", "priority": "ACİL", "responsible": "HSE Yöneticisi", "deadline": "1 hafta", "kpi": "Ölçüm kriteri"},
    {"no": 2, "action": "Detaylı eylem", "priority": "ACİL", "responsible": "Üretim Müdürü", "deadline": "2 hafta", "kpi": "Ölçüm kriteri"},
    {"no": 3, "action": "Detaylı eylem", "priority": "YÜKSEK", "responsible": "Bakım Mühendisi", "deadline": "1 ay", "kpi": "Ölçüm kriteri"},
    {"no": 4, "action": "Detaylı eylem", "priority": "YÜKSEK", "responsible": "İK Müdürü", "deadline": "1 ay", "kpi": "Ölçüm kriteri"},
    {"no": 5, "action": "Detaylı eylem", "priority": "YÜKSEK", "responsible": "Vardiya Amiri", "deadline": "2 ay", "kpi": "Ölçüm kriteri"},
    {"no": 6, "action": "Detaylı eylem", "priority": "ORTA", "responsible": "Eğitim Koordinatörü", "deadline": "2 ay", "kpi": "Ölçüm kriteri"},
    {"no": 7, "action": "Detaylı eylem", "priority": "ORTA", "responsible": "Süreç Mühendisi", "deadline": "3 ay", "kpi": "Ölçüm kriteri"},
    {"no": 8, "action": "Detaylı eylem", "priority": "ORTA", "responsible": "Kalite Müdürü", "deadline": "3 ay", "kpi": "Ölçüm kriteri"},
    {"no": 9, "action": "Detaylı eylem", "priority": "ORTA", "responsible": "HSE Uzmanı", "deadline": "3 ay", "kpi": "Ölçüm kriteri"},
    {"no": 10, "action": "Detaylı eylem", "priority": "DÜŞÜK", "responsible": "Tesis Müdürü", "deadline": "6 ay", "kpi": "Ölçüm kriteri"},
    {"no": 11, "action": "Detaylı eylem", "priority": "DÜŞÜK", "responsible": "Teknik Direktör", "deadline": "6 ay", "kpi": "Ölçüm kriteri"},
    {"no": 12, "action": "Detaylı eylem", "priority": "DÜŞÜK", "responsible": "Genel Müdür", "deadline": "12 ay", "kpi": "Ölçüm kriteri"}
  ],
  "lessons_learned": {
    "what_to_do": [
      "Ders 1 - Ne yapılmalı: detaylı açıklama",
      "Ders 2 - Ne yapılmalı: detaylı açıklama",
      "Ders 3 - Ne yapılmalı: detaylı açıklama",
      "Ders 4 - Ne yapılmalı: detaylı açıklama"
    ],
    "long_term": [
      "Uzun vadeli çözüm 1: detaylı açıklama",
      "Uzun vadeli çözüm 2: detaylı açıklama",
      "Uzun vadeli çözüm 3: detaylı açıklama",
      "Uzun vadeli çözüm 4: detaylı açıklama"
    ],
    "communication": [
      "İletişim planı 1: detaylı açıklama",
      "İletişim planı 2: detaylı açıklama",
      "İletişim planı 3: detaylı açıklama"
    ],
    "training": [
      "Eğitim programı 1: detaylı açıklama",
      "Eğitim programı 2: detaylı açıklama",
      "Eğitim programı 3: detaylı açıklama",
      "Eğitim programı 4: detaylı açıklama"
    ]
  },
  "conclusion": {
    "overall_assessment": "Genel değerlendirme - 3-4 paragraf kapsamlı",
    "short_term_measures": [
      "Kısa vade önlem 1 (1-2 ay): detaylı",
      "Kısa vade önlem 2 (1-2 ay): detaylı",
      "Kısa vade önlem 3 (1-2 ay): detaylı",
      "Kısa vade önlem 4 (1-2 ay): detaylı"
    ],
    "long_term_improvements": [
      "Uzun vade iyileştirme 1 (3-12 ay): detaylı",
      "Uzun vade iyileştirme 2 (3-12 ay): detaylı",
      "Uzun vade iyileştirme 3 (3-12 ay): detaylı",
      "Uzun vade iyileştirme 4 (3-12 ay): detaylı"
    ],
    "comparison_table": [
      {"criterion": "Risk Seviyesi", "current": "Yüksek", "target": "Düşük"},
      {"criterion": "Prosedür Uyum Oranı", "current": "%60", "target": "%95"},
      {"criterion": "Eğitim Kapsamı", "current": "Temel", "target": "Kapsamlı"},
      {"criterion": "Bakım Periyodu", "current": "Reaktif", "target": "Proaktif"},
      {"criterion": "Denetim Sıklığı", "current": "Aylık", "target": "Haftalık"}
    ]
  }
}

KURALLAR:
- Tüm metin yüzde yüz TÜRKÇE
- Her alan ham veriden türetilmeli
- Kısa cevaplar değil, DETAYLI açıklamalar
- branches dizisi ham verideki tüm dalları içermeli
- root_causes dizisi ham verideki tüm kök nedenleri içermeli
- SADECE JSON döndür, başka hiçbir şey yazma
"""


# ─────────────────────────────────────────────────────────────────────────────
# DOCX YARDIMCI FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────────────────

def _set_cell_bg(cell, rgb: RGBColor):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def _set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def _add_section_header(doc, number, title):
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    _set_cell_bg(cell, COLOR["dark_blue"])
    _set_cell_margins(cell, 120, 120, 160, 160)
    p = cell.paragraphs[0]
    run = p.add_run(f"{number}. {title.upper()}")
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = COLOR["white"]
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)


def _add_subsection_header(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR["mid_blue"]


def _add_paragraph(doc, text, size=11, color=None, bold=False, italic=False,
                   space_before=4, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(str(text))
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color or COLOR["dark_grey"]


def _add_colored_box(doc, title, content, bg_color, title_color=None):
    table = doc.add_table(rows=2, cols=1)
    table.style = 'Table Grid'
    tc = table.cell(0, 0)
    _set_cell_bg(tc, bg_color)
    _set_cell_margins(tc, 80, 80, 140, 140)
    p = tc.paragraphs[0]
    run = p.add_run(str(title))
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = title_color or COLOR["white"]
    cc = table.cell(1, 0)
    _set_cell_bg(cc, COLOR["light_grey"])
    _set_cell_margins(cc, 100, 100, 140, 140)
    p = cc.paragraphs[0]
    run = p.add_run(str(content))
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR["dark_grey"]
    doc.add_paragraph()


def _add_info_table(doc, data: dict, header_color=None):
    if not data:
        return
    table = doc.add_table(rows=len(data), cols=2)
    table.style = 'Table Grid'
    hc = header_color or COLOR["light_blue"]
    for i, (key, val) in enumerate(data.items()):
        row = table.rows[i]
        lc = row.cells[0]
        _set_cell_bg(lc, hc)
        _set_cell_margins(lc)
        run = lc.paragraphs[0].add_run(str(key))
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR["dark_blue"]
        rc = row.cells[1]
        bg = COLOR["white"] if i % 2 == 0 else COLOR["light_grey"]
        _set_cell_bg(rc, bg)
        _set_cell_margins(rc)
        run = rc.paragraphs[0].add_run(str(val))
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR["dark_grey"]
    doc.add_paragraph()


def _add_bullet_list(doc, items: list, color=None):
    for item in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(str(item))
        run.font.size = Pt(10)
        run.font.color.rgb = color or COLOR["dark_grey"]


def _add_page_break(doc):
    doc.add_page_break()


def _add_page_numbers(doc):
    """Sayfa numaralarını ekle (footer'a)"""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    
    # Footer'ı temizle
    for paragraph in footer.paragraphs:
        paragraph.clear()
    
    # Yeni paragraph ekle ve sayfa numarasını ortala
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Sayfa numarası field ekle
    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR["dark_grey"]


def _build_table_of_contents(doc):
    """İçindekiler sayfası oluştur"""
    _add_section_header(doc, "", "İÇİNDEKİLER")
    doc.add_paragraph()
    
    # İçindekiler listesi
    toc_items = [
        ("1", "YÖNETİCİ ÖZETİ"),
        ("2", "OLAY BİLGİLERİ"),
        ("   2.1", "Genel Bilgiler"),
        ("   2.2", "Zaman Çizelgesi"),
        ("   2.3", "Önem Derecesi"),
        ("3", "ANALİZ YÖNTEMİ"),
        ("   3.4", "Analiz Ekibi"),
        ("4-N", "KRİTİK FAKTÖRLER (5-Why Zincirleri)"),
        ("6", "KATKIDA BULUNAN FAKTÖRLER"),
        ("7", "DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER"),
        ("8", "ÇIKARILAN DERSLER"),
        ("9", "SONUÇ VE ÖNERİLER"),
        ("10", "ONAY VE İMZA SAYFASI"),
    ]
    
    for num, title in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3) if num.startswith("   ") else Inches(0)
        p.paragraph_format.space_after = Pt(6)
        
        # Numara
        run = p.add_run(f"{num.strip()}.  ")
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR["dark_blue"]
        
        # Başlık
        run = p.add_run(title)
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR["dark_grey"]
    
    _add_page_break(doc)


# ─────────────────────────────────────────────────────────────────────────────
# RAPOR BÖLÜM FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────────────────

def _build_cover(doc, cover: dict):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(cover.get("title", "KÖK NEDEN ANALİZİ RAPORU"))
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = COLOR["dark_blue"]
    doc.add_paragraph()
    # Subtitle removed - HSG245 box no longer displayed
    doc.add_paragraph()
    # Gizlilik banner
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    _set_cell_bg(cell, COLOR["red"])
    _set_cell_margins(cell, 120, 120, 200, 200)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(cover.get("confidentiality", "GİZLİ - SADECE YETKİLİ PERSONELİN ERİŞİMİNE AÇIKTIR"))
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = COLOR["white"]
    doc.add_paragraph()
    _add_info_table(doc, {
        "Referans No": cover.get("ref_no", "N/A"),
        "Tarih": cover.get("date", "N/A"),
        "Lokasyon": cover.get("location", "N/A"),
        "Olay Tipi": cover.get("incident_type", "N/A"),
    }, COLOR["dark_blue"])
    _add_colored_box(doc, "OLAY ÖZETİ", cover.get("incident_summary_short", ""), COLOR["dark_blue"])
    _add_page_break(doc)


def _build_executive_summary(doc, es: dict, root_causes: list):
    _add_section_header(doc, "1", "YÖNETİCİ ÖZETİ")
    _add_subsection_header(doc, "1.1 Olay Özeti")
    for field in ["what_happened", "where_happened", "who_affected", "immediate_response"]:
        if es.get(field):
            _add_paragraph(doc, es[field], space_after=6)
    doc.add_paragraph()
    _add_subsection_header(doc, "1.2 Temel Bulgular")
    for finding in es.get("key_findings", []):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(f"  {finding}")
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR["dark_grey"]
    doc.add_paragraph()
    _add_subsection_header(doc, "1.3 Kritik Kök Nedenler")
    for i, rc in enumerate(root_causes[:3]):
        color = ROOT_CAUSE_COLORS[i % len(ROOT_CAUSE_COLORS)]
        desc = rc.get("detailed_description", "")
        short_desc = desc[:250] + "..." if len(desc) > 250 else desc
        _add_colored_box(
            doc,
            f"KOK NEDEN {i+1}: {rc.get('title', '')}",
            f"[{rc.get('code','')} / {rc.get('category','')}]\n{short_desc}",
            color
        )
    doc.add_paragraph()
    _add_subsection_header(doc, "1.4 Acil Eylemler")
    actions = es.get("immediate_actions", [])
    if actions:
        table = doc.add_table(rows=len(actions) + 1, cols=3)
        table.style = 'Table Grid'
        for j, h in enumerate(["Acil Eylem", "Sorumlu", "Durum"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["dark_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, act in enumerate(actions):
            row = table.rows[i + 1]
            vals = [act.get("action", ""), act.get("responsible", ""), act.get("status", "")]
            for j, val in enumerate(vals):
                c = row.cells[j]
                _set_cell_bg(c, COLOR["light_grey"] if i % 2 == 0 else COLOR["white"])
                _set_cell_margins(c)
                run = c.paragraphs[0].add_run(str(val))
                run.font.size = Pt(10)
    _add_page_break(doc)


def _build_incident_details(doc, details: dict):
    _add_section_header(doc, "2", "OLAY BİLGİLERİ")
    _add_subsection_header(doc, "2.1 Detaylı Bilgi Tablosu")
    _add_info_table(doc, details.get("info_table", {}))
    _add_subsection_header(doc, "2.2 Olay Detayları")
    _add_info_table(doc, details.get("event_table", {}))
    doc.add_paragraph()
    _add_subsection_header(doc, "2.3 Kronolojik Olay Akışı")
    timeline = details.get("timeline", [])
    if timeline:
        table = doc.add_table(rows=len(timeline) + 1, cols=2)
        table.style = 'Table Grid'
        for j, h in enumerate(["Zaman", "Olay"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["mid_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, step in enumerate(timeline):
            row = table.rows[i + 1]
            bg = COLOR["light_blue"] if i % 2 == 0 else COLOR["white"]
            tc = row.cells[0]
            _set_cell_bg(tc, bg)
            _set_cell_margins(tc)
            run = tc.paragraphs[0].add_run(step.get("time", ""))
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["dark_blue"]
            ec = row.cells[1]
            _set_cell_bg(ec, bg)
            _set_cell_margins(ec)
            run = ec.paragraphs[0].add_run(step.get("event", ""))
            run.font.size = Pt(10)
    doc.add_paragraph()
    sev = details.get("severity", {})
    if sev:
        _add_subsection_header(doc, "2.4 Aciliyet Seviyeleri")
        _add_info_table(doc, {
            "Gerçek Zarar": sev.get("actual_harm", ""),
            "Potansiyel Zarar": sev.get("potential_harm", ""),
            "Soruşturma Seviyesi": sev.get("investigation_level", ""),
            "RIDDOR Kapsamı": sev.get("riddor", ""),
        })
    _add_page_break(doc)


def _build_analysis_method(doc, method: dict):
    _add_section_header(doc, "3", "ANALİZ YÖNTEMİ")
    
    # 3.1, 3.2, 3.3 sections hidden from user view (working in background)
    # _add_subsection_header(doc, "3.1 Metodoloji")
    # _add_paragraph(doc, method.get("methodology_description", ""), space_after=8)
    # _add_subsection_header(doc, "3.2 5-Why Tekniği")
    # _add_paragraph(doc, method.get("five_why_explanation", ""), space_after=8)
    # _add_subsection_header(doc, "3.3 Kod Sistemi")
    # codes = method.get("code_system", [])
    # if codes:
    #     table = doc.add_table(rows=len(codes) + 1, cols=3)
    #     table.style = 'Table Grid'
    #     for j, h in enumerate(["Kod", "Kategori", "Açıklama"]):
    #         c = table.rows[0].cells[j]
    #         _set_cell_bg(c, COLOR["dark_blue"])
    #         _set_cell_margins(c)
    #         run = c.paragraphs[0].add_run(h)
    #         run.bold = True
    #         run.font.size = Pt(10)
    #         run.font.color.rgb = COLOR["white"]
    #     for i, code in enumerate(codes):
    #         row = table.rows[i + 1]
    #         bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
    #         vals = [code.get("code",""), code.get("category",""), code.get("description","")]
    #         for j, val in enumerate(vals):
    #             c = row.cells[j]
    #             _set_cell_bg(c, bg)
    #             _set_cell_margins(c)
    #             run = c.paragraphs[0].add_run(str(val))
    #             run.bold = (j == 0)
    #             run.font.size = Pt(10)
    #             run.font.color.rgb = COLOR["dark_blue"] if j == 0 else COLOR["dark_grey"]
    # doc.add_paragraph()
    
    _add_subsection_header(doc, "3.1 Analiz Ekibi")  # Changed from 3.4 to 3.1
    members = method.get("team_members", [])
    if members:
        table = doc.add_table(rows=len(members) + 1, cols=3)
        table.style = 'Table Grid'
        for j, h in enumerate(["İsim", "Rol", "Tarih"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["mid_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, m in enumerate(members):
            row = table.rows[i + 1]
            bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
            for j, val in enumerate([m.get("name",""), m.get("role",""), m.get("date","")]):
                c = row.cells[j]
                _set_cell_bg(c, bg)
                _set_cell_margins(c)
                run = c.paragraphs[0].add_run(str(val))
                run.font.size = Pt(10)
    _add_page_break(doc)


def _build_branches(doc, branches: list):
    branch_colors = [COLOR["red"], COLOR["orange"], COLOR["green"], COLOR["mid_blue"]]
    for branch in branches:
        bn = branch.get("branch_number", 1)
        color = branch_colors[(bn - 1) % len(branch_colors)]
        # Dal başlığı
        table = doc.add_table(rows=1, cols=1)
        table.style = 'Table Grid'
        cell = table.cell(0, 0)
        _set_cell_bg(cell, color)
        _set_cell_margins(cell, 120, 120, 160, 160)
        p = cell.paragraphs[0]
        run = p.add_run(branch.get("branch_title", f"KRİTİK FAKTÖR {bn}"))
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR["white"]
        doc.add_paragraph()
        _add_subsection_header(doc, f"{3+bn}.1 Başlangıç Durumu ve Doğrudan Neden")
        _add_paragraph(doc, branch.get("initial_condition", ""), space_after=6)
        _add_paragraph(doc, branch.get("direct_cause", ""), bold=True, space_after=8)
        _add_subsection_header(doc, f"{3+bn}.2 5-Why Analiz Tablosu")
        why_chain = branch.get("why_chain", [])
        if why_chain:
            table = doc.add_table(rows=len(why_chain) + 1, cols=4)
            table.style = 'Table Grid'
            for j, h in enumerate(["Neden #", "Soru ve Yanıt", "Kod", "Kategori"]):
                c = table.rows[0].cells[j]
                _set_cell_bg(c, COLOR["dark_blue"])
                _set_cell_margins(c)
                run = c.paragraphs[0].add_run(h)
                run.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = COLOR["white"]
            for i, why in enumerate(why_chain):
                row = table.rows[i + 1]
                bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
                qa = f"NEDEN: {why.get('question','')}\nYANIT: {why.get('answer','')}"
                vals = [f"NEDEN {why.get('number', i+1)}", qa, why.get("code",""), why.get("category","")]
                for j, val in enumerate(vals):
                    c = row.cells[j]
                    _set_cell_bg(c, bg)
                    _set_cell_margins(c)
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.size = Pt(9)
                    run.bold = (j == 0)
        doc.add_paragraph()
        _add_subsection_header(doc, f"{3+bn}.3 Kök Neden")
        rc_title = f"KOK NEDEN {bn}: {branch.get('root_cause_title','')}"
        rc_content = (f"[{branch.get('root_cause_code','')} / {branch.get('root_cause_category','')}]\n\n"
                      f"{branch.get('root_cause_detail','')}")
        _add_colored_box(doc, rc_title, rc_content, color)
        org_factors = branch.get("organizational_factors", [])
        if org_factors:
            _add_subsection_header(doc, f"{3+bn}.4 Organizasyonel Faktörler")
            _add_bullet_list(doc, org_factors)
        _add_page_break(doc)


# Section 6 removed - root causes already detailed in Critical Factor sections
# def _build_root_causes(doc, root_causes: list):
#     _add_section_header(doc, "6", "NİHAİ KÖK NEDENLER")
#     for i, rc in enumerate(root_causes):
#         color = ROOT_CAUSE_COLORS[i % len(ROOT_CAUSE_COLORS)]
#         table = doc.add_table(rows=1, cols=1)
#         table.style = 'Table Grid'
#         cell = table.cell(0, 0)
#         _set_cell_bg(cell, color)
#         _set_cell_margins(cell, 120, 120, 160, 160)
#         p = cell.paragraphs[0]
#         run = p.add_run(f"KOK NEDEN {i+1}: {rc.get('title','')}")
#         run.bold = True
#         run.font.size = Pt(12)
#         run.font.color.rgb = COLOR["white"]
#         doc.add_paragraph()
#         _add_info_table(doc, {
#             "Kod": rc.get("code",""),
#             "Kategori": rc.get("category",""),
#             "İlgili Birimler": rc.get("contributing_organizations",""),
#         })
#         _add_paragraph(doc, rc.get("detailed_description",""), space_after=8)
#         impacts = rc.get("impacts", [])
#         if impacts:
#             _add_subsection_header(doc, "Bu Nedenden Kaynaklanan Etkiler:")
#             _add_bullet_list(doc, impacts, color)
#         doc.add_paragraph()
#     _add_page_break(doc)


def _build_contributing_factors(doc, factors: list):
    _add_section_header(doc, "6", "KATKIDA BULUNAN FAKTÖRLER")
    doc.add_paragraph()
    priority_colors = {"Yüksek": COLOR["red"], "Orta": COLOR["orange"], "Düşük": COLOR["green"]}
    if factors:
        table = doc.add_table(rows=len(factors) + 1, cols=3)
        table.style = 'Table Grid'
        for j, h in enumerate(["Faktör Türü", "Açıklama", "Etki Seviyesi"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["dark_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, f in enumerate(factors):
            row = table.rows[i + 1]
            bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
            impact = f.get("impact_level","Orta")
            for j, val in enumerate([f.get("factor_type",""), f.get("description",""), impact]):
                c = row.cells[j]
                if j == 2:
                    _set_cell_bg(c, priority_colors.get(impact, COLOR["light_grey"]))
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["white"]
                else:
                    _set_cell_bg(c, bg)
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["dark_grey"]
                _set_cell_margins(c)
                run.bold = (j == 0)
                run.font.size = Pt(10)
    _add_page_break(doc)


def _build_corrective_actions(doc, actions: list):
    _add_section_header(doc, "7", "DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER")
    doc.add_paragraph()
    priority_colors = {
        "ACİL": COLOR["red"], "YÜKSEK": COLOR["orange"],
        "ORTA": COLOR["green"], "DÜŞÜK": COLOR["mid_blue"],
    }
    if actions:
        table = doc.add_table(rows=len(actions) + 1, cols=6)
        table.style = 'Table Grid'
        for j, h in enumerate(["No", "Faaliyet", "Öncelik", "Sorumlu", "Süre", "KPI"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["dark_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, act in enumerate(actions):
            row = table.rows[i + 1]
            bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
            priority = act.get("priority","ORTA")
            vals = [str(act.get("no",i+1)), act.get("action",""), priority,
                    act.get("responsible",""), act.get("deadline",""), act.get("kpi","")]
            for j, val in enumerate(vals):
                c = row.cells[j]
                if j == 2:
                    _set_cell_bg(c, priority_colors.get(priority, COLOR["light_grey"]))
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["white"]
                    run.bold = True
                else:
                    _set_cell_bg(c, bg)
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["dark_grey"]
                _set_cell_margins(c)
                run.font.size = Pt(9)
    _add_page_break(doc)


def _build_lessons_learned(doc, lessons: dict):
    _add_section_header(doc, "8", "CIKARILAN DERSLER")
    doc.add_paragraph()
    sections = [
        ("NE YAPILMALI", lessons.get("what_to_do", []), COLOR["green"]),
        ("UZUN VADELI COZUMLER", lessons.get("long_term", []), COLOR["mid_blue"]),
        ("ILETISIM VE PAYLASIM", lessons.get("communication", []), COLOR["orange"]),
        ("EGITIM VE FARKINDALIK", lessons.get("training", []), COLOR["red"]),
    ]
    for title, items, color in sections:
        if items:
            _add_colored_box(doc, title, "\n".join(f"- {item}" for item in items), color)
    _add_page_break(doc)


def _build_conclusion(doc, conclusion: dict):
    _add_section_header(doc, "9", "SONUC VE ONERILER")
    _add_subsection_header(doc, "9.1 Genel Değerlendirme")
    _add_paragraph(doc, conclusion.get("overall_assessment",""), space_after=8)
    _add_subsection_header(doc, "9.2 Kısa Vadeli Önlemler (1-2 Ay)")
    _add_bullet_list(doc, conclusion.get("short_term_measures",[]))
    doc.add_paragraph()
    _add_subsection_header(doc, "9.3 Uzun Vadeli İyileştirmeler (3-12 Ay)")
    _add_bullet_list(doc, conclusion.get("long_term_improvements",[]))
    doc.add_paragraph()
    _add_subsection_header(doc, "9.4 Mevcut vs Hedef Karşılaştırması")
    comparison = conclusion.get("comparison_table", [])
    if comparison:
        table = doc.add_table(rows=len(comparison) + 1, cols=3)
        table.style = 'Table Grid'
        for j, h in enumerate(["Kriter", "Mevcut Durum", "Hedeflenen"]):
            c = table.rows[0].cells[j]
            _set_cell_bg(c, COLOR["dark_blue"])
            _set_cell_margins(c)
            run = c.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["white"]
        for i, row_data in enumerate(comparison):
            row = table.rows[i + 1]
            vals = [row_data.get("criterion",""), row_data.get("current",""), row_data.get("target","")]
            for j, val in enumerate(vals):
                c = row.cells[j]
                if j == 2:
                    _set_cell_bg(c, COLOR["green"])
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["white"]
                elif j == 1:
                    _set_cell_bg(c, COLOR["light_grey"])
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["red"]
                else:
                    _set_cell_bg(c, COLOR["light_blue"])
                    run = c.paragraphs[0].add_run(str(val))
                    run.font.color.rgb = COLOR["dark_blue"]
                _set_cell_margins(c)
                run.bold = (j == 0)
                run.font.size = Pt(10)
    _add_page_break(doc)


def _build_signature_page(doc):
    _add_section_header(doc, "10", "ONAY VE IMZA SAYFASI")
    doc.add_paragraph()
    roles = [
        ("HAZIRLAYAN", "HSE Uzmanı", "HSE Kök Neden Analisti"),
        ("INCELEYEN", "HSE Yöneticisi", "HSE Departman Yöneticisi"),
        ("ONAYLAYAN", "Tesis Müdürü", "Genel Operasyon Müdürü"),
    ]
    table = doc.add_table(rows=len(roles) + 1, cols=4)
    table.style = 'Table Grid'
    for j, h in enumerate(["Rol", "İsim", "Ünvan", "İmza / Tarih"]):
        c = table.rows[0].cells[j]
        _set_cell_bg(c, COLOR["dark_blue"])
        _set_cell_margins(c)
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR["white"]
    for i, (role, name, title) in enumerate(roles):
        row = table.rows[i + 1]
        bg = COLOR["light_grey"] if i % 2 == 0 else COLOR["white"]
        for j, val in enumerate([role, name, title, "___________________\n_____ / _____ / _____"]):
            c = row.cells[j]
            _set_cell_bg(c, bg)
            _set_cell_margins(c, 160, 160, 120, 120)
            run = c.paragraphs[0].add_run(str(val))
            run.bold = (j == 0)
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR["dark_blue"] if j == 0 else COLOR["dark_grey"]


# ─────────────────────────────────────────────────────────────────────────────
# ANA AGENT SINIFI
# ─────────────────────────────────────────────────────────────────────────────

class SkillBasedDocxAgent:
    """
    V2: Claude API içerik üretir → python-docx DOCX oluşturur.

    Kullanım:
        agent = SkillBasedDocxAgent()
        path = agent.generate_report(
            investigation_data=data,
            output_path="outputs/rapor.docx"
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY bulunamadı! .env dosyasına ekleyin.")
        self.api_key = key
        self.model = "anthropic/claude-sonnet-4.5"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        print(f"✅ SkillBasedDocxAgent V2 hazır (OpenRouter {self.model})")

    def generate_report(
        self,
        investigation_data: Dict,
        output_path: str = "outputs/hse_report.docx",
        timeout_seconds: int = 600,
    ) -> str:
        """
        Investigation data'dan kapsamlı DOCX rapor üretir.

        Args:
            investigation_data: part1, part2, part3_rca içeren tam pipeline verisi
            output_path: Çıktı dosyası yolu
            timeout_seconds: API timeout (saniye)

        Returns:
            Oluşturulan DOCX dosyasının tam yolu
        """
        print("\n" + "=" * 70)
        print("📄 DOCX RAPOR ÜRETME V2 (Claude + python-docx)")
        print("=" * 70)

        raw_data = self._build_raw_payload(investigation_data)
        char_count = len(json.dumps(raw_data, ensure_ascii=False))
        print(f"✅ Ham veri hazır ({char_count} karakter)")

        print("\n🤖 Claude API'ye içerik isteği gönderiliyor...")
        start = time.time()
        content = self._generate_content_with_claude(raw_data)
        elapsed = time.time() - start
        out_chars = len(json.dumps(content, ensure_ascii=False))
        print(f"✅ İçerik alındı ({elapsed:.1f}s, {out_chars} karakter)")

        print("\n📝 DOCX oluşturuluyor (python-docx)...")
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self._build_docx(content, str(output_file.resolve()))

        if not output_file.exists():
            raise RuntimeError(f"DOCX oluşturulamadı: {output_file}")

        size_kb = output_file.stat().st_size / 1024
        print(f"\n✅ DOCX başarıyla oluşturuldu!")
        print(f"📄 Dosya : {output_file.resolve()}")
        print(f"📊 Boyut : {size_kb:.1f} KB")
        
        # HTML rapor da üret
        html_path = str(output_file).replace('.docx', '.html')
        print(f"\n📝 HTML raporu oluşturuluyor...")
        self._build_html(content, html_path)
        html_size_kb = Path(html_path).stat().st_size / 1024
        print(f"✅ HTML başarıyla oluşturuldu!")
        print(f"📄 Dosya : {html_path}")
        print(f"📊 Boyut : {html_size_kb:.1f} KB")
        
        print("=" * 70)
        return str(output_file.resolve())

    def _build_raw_payload(self, data: Dict) -> Dict:
        if "part3_rca" in data:
            return {
                "part1": data.get("part1", {}),
                "part2": data.get("part2", {}),
                "part3_rca": data["part3_rca"],
            }
        if "analysis_branches" in data:
            return {"part1": {}, "part2": {}, "part3_rca": data}
        return data

    def _generate_content_with_claude(self, raw_data: Dict) -> Dict:
        user_msg = (
            "Aşağıdaki kök neden analizi ham verisini kullanarak "
            "profesyonel HSE raporu içeriğini üret.\n\n"
            "Ham Veri:\n```json\n"
            + json.dumps(raw_data, ensure_ascii=False, indent=2)
            + "\n```\n\n"
            "SADECE JSON döndür. Başka hiçbir şey yazma."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hse-rca-system",
            "X-Title": "HSE RCA DOCX Generator",
            "anthropic-version": "2023-06-01"  # Prompt caching için gerekli
        }

        # Anthropic Prompt Caching - sistem promptu cache'le (maliyeti %90 düşürür)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": [
                        {
                            "type": "text",
                            "text": CONTENT_SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"}  # Bu promptu 5 dakika cache'le
                        }
                    ]
                },
                {"role": "user", "content": user_msg}
            ],
            "max_tokens": 32000,
            "temperature": 0.3,
            "stream": False  # Non-streaming daha hızlı ve güvenilir
        }

        print("-" * 50)
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=600
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                full_text = result['choices'][0].get('message', {}).get('content', '')
                
                # İçeriği ekrana yazdır (debug için)
                print(full_text[:500] + "..." if len(full_text) > 500 else full_text)
                print(f"\n📊 Toplam karakter: {len(full_text)}")
                print("-" * 50)
                
                return self._parse_json_response(full_text)
            else:
                print(f"\n❌ Geçersiz API yanıtı: {result}")
                print("-" * 50)
                return {"cover": {"title": "KÖK NEDEN ANALİZİ RAPORU"}}
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ OpenRouter API hatası: {e}")
            print("-" * 50)
            return {"cover": {"title": "KÖK NEDEN ANALİZİ RAPORU"}}

    def _parse_json_response(self, text: str) -> Dict:
        m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        print("⚠️  JSON parse başarısız, minimal içerik kullanılıyor...")
        return {"cover": {"title": "KOK NEDEN ANALİZİ RAPORU"}}

    def _build_docx(self, content: Dict, output_path: str) -> None:
        doc = Document()
        section = doc.sections[0]
        section.page_width = Cm(21.59)
        section.page_height = Cm(27.94)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)

        # Sayfa numaralarını ekle
        _add_page_numbers(doc)

        # 1. Kapak Sayfası
        _build_cover(doc, content.get("cover", {}))
        
        # 2. İçindekiler Sayfası
        _build_table_of_contents(doc)
        
        # 3. Rapor içeriği
        _build_executive_summary(doc, content.get("executive_summary", {}), content.get("root_causes", []))
        _build_incident_details(doc, content.get("incident_details", {}))
        _build_analysis_method(doc, content.get("analysis_method", {}))
        branches = content.get("branches", [])
        if branches:
            _build_branches(doc, branches)
        # Section 6 removed - root causes already in Critical Factor sections
        # root_causes = content.get("root_causes", [])
        # if root_causes:
        #     _build_root_causes(doc, root_causes)
        _build_contributing_factors(doc, content.get("contributing_factors", []))
        _build_corrective_actions(doc, content.get("corrective_actions", []))
        _build_lessons_learned(doc, content.get("lessons_learned", {}))
        _build_conclusion(doc, content.get("conclusion", {}))
        _build_signature_page(doc)

        doc.save(output_path)
        print(f"✅ Dosya kaydedildi: {output_path}")

    def _build_html(self, content: Dict, output_path: str) -> None:
        """Düzenlenebilir HTML rapor oluşturur."""
        html = self._generate_html_template(content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_html_template(self, content: Dict) -> str:
        """Modern, responsive ve düzenlenebilir HTML rapor şablonu."""
        cover = content.get("cover", {})
        executive_summary = content.get("executive_summary", {})
        incident_details = content.get("incident_details", {})
        analysis_method = content.get("analysis_method", {})
        branches = content.get("branches", [])
        root_causes = content.get("root_causes", [])
        contributing_factors = content.get("contributing_factors", [])
        corrective_actions = content.get("corrective_actions", [])
        lessons_learned = content.get("lessons_learned", {})
        conclusion = content.get("conclusion", {})

        # HTML oluştur
        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cover.get('title', 'KÖK NEDEN ANALİZİ RAPORU')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #444;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .cover {{
            background: linear-gradient(135deg, #1B3A5C 0%, #2E6DA4 100%);
            color: white;
            padding: 80px 40px;
            text-align: center;
        }}
        
        .cover h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-transform: uppercase;
        }}
        
        .cover .subtitle {{
            font-size: 1.2em;
            font-style: italic;
            margin-bottom: 30px;
        }}
        
        .confidential-banner {{
            background: #C0392B;
            color: white;
            padding: 15px;
            margin: 30px 0;
            font-weight: bold;
            text-align: center;
            border-radius: 5px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }}
        
        .info-item {{
            background: #D6E4F0;
            padding: 15px;
            border-left: 4px solid #1B3A5C;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #1B3A5C;
            font-size: 0.9em;
        }}
        
        .info-value {{
            margin-top: 5px;
            color: #444;
        }}
        
        .incident-summary {{
            background: #1B3A5C;
            color: white;
            padding: 20px;
            margin: 30px 0;
            border-radius: 5px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin: 40px 0;
            page-break-inside: avoid;
        }}
        
        .section-header {{
            background: #1B3A5C;
            color: white;
            padding: 15px 20px;
            margin: 30px 0 20px 0;
            font-size: 1.3em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .subsection-header {{
            color: #2E6DA4;
            font-size: 1.1em;
            font-weight: bold;
            margin: 25px 0 15px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #2E6DA4;
        }}
        
        .paragraph {{
            margin: 15px 0;
            text-align: justify;
            line-height: 1.8;
        }}
        
        .colored-box {{
            margin: 20px 0;
            border-radius: 5px;
            overflow: hidden;
        }}
        
        .box-header {{
            padding: 15px;
            font-weight: bold;
            color: white;
        }}
        
        .box-content {{
            background: #F5F5F5;
            padding: 20px;
            white-space: pre-wrap;
        }}
        
        .box-red .box-header {{ background: #C0392B; }}
        .box-orange .box-header {{ background: #E67E22; }}
        .box-green .box-header {{ background: #27AE60; }}
        .box-blue .box-header {{ background: #2E6DA4; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #1B3A5C;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background: #F5F5F5;
        }}
        
        tr:hover {{
            background: #E8F4F8;
        }}
        
        .timeline {{
            margin: 20px 0;
        }}
        
        .timeline-item {{
            display: flex;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #2E6DA4;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .timeline-time {{
            font-weight: bold;
            color: #2E6DA4;
            min-width: 80px;
            font-size: 1.1em;
        }}
        
        .timeline-event {{
            flex: 1;
            margin-left: 20px;
        }}
        
        .why-chain {{
            margin: 20px 0;
        }}
        
        .why-item {{
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid #E67E22;
            background: #FFF8F0;
        }}
        
        .why-number {{
            font-weight: bold;
            color: #E67E22;
            font-size: 1.1em;
        }}
        
        .why-question {{
            font-weight: bold;
            margin: 5px 0;
            color: #444;
        }}
        
        .why-answer {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        
        .why-code {{
            display: inline-block;
            background: #E67E22;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        
        .root-cause-box {{
            margin: 30px 0;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }}
        
        .root-cause-header {{
            padding: 20px;
            color: white;
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .root-cause-content {{
            background: white;
            padding: 25px;
        }}
        
        .root-cause-1 .root-cause-header {{ background: #C0392B; }}
        .root-cause-2 .root-cause-header {{ background: #E67E22; }}
        .root-cause-3 .root-cause-header {{ background: #27AE60; }}
        .root-cause-4 .root-cause-header {{ background: #2E6DA4; }}
        
        ul.bullet-list {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        ul.bullet-list li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        .priority-urgent {{
            background: #C0392B;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .priority-high {{
            background: #E67E22;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .priority-medium {{
            background: #27AE60;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .priority-low {{
            background: #2E6DA4;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .impact-high {{ color: #C0392B; font-weight: bold; }}
        .impact-medium {{ color: #E67E22; font-weight: bold; }}
        .impact-low {{ color: #27AE60; font-weight: bold; }}
        
        .signature-section {{
            margin: 40px 0;
        }}
        
        .signature-table td {{
            padding: 30px 15px;
        }}
        
        .signature-line {{
            border-top: 2px solid #444;
            margin-top: 60px;
            padding-top: 10px;
            text-align: center;
        }}
        
        .comparison-table td:first-child {{
            background: #D6E4F0 !important;
            color: #1B3A5C;
            font-weight: bold;
        }}
        
        .comparison-table .current {{
            background: #FFE6E6 !important;
            color: #C0392B;
        }}
        
        .comparison-table .target {{
            background: #E8F8F0 !important;
            color: #27AE60;
            font-weight: bold;
        }}
        
        /* Navigasyon Menüsü */
        .nav-menu {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 250px;
        }}
        
        .nav-menu h3 {{
            margin: 0 0 10px 0;
            font-size: 1em;
            color: #1B3A5C;
            border-bottom: 2px solid #1B3A5C;
            padding-bottom: 5px;
        }}
        
        .nav-menu ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .nav-menu li {{
            margin: 8px 0;
        }}
        
        .nav-menu a {{
            color: #2E6DA4;
            text-decoration: none;
            font-size: 0.9em;
            display: block;
            padding: 5px;
            border-radius: 3px;
            transition: all 0.2s;
        }}
        
        .nav-menu a:hover {{
            background: #D6E4F0;
            padding-left: 10px;
        }}
        
        .nav-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1B3A5C;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            z-index: 999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}
        
        .nav-toggle:hover {{
            background: #2E6DA4;
        }}
        
        /* Düzenleme Toolbar */
        .edit-toolbar {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            display: none;
        }}
        
        .edit-toolbar.active {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .toolbar-btn {{
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        
        .toolbar-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .btn-save {{
            background: #27AE60;
            color: white;
        }}
        
        .btn-print {{
            background: #2E6DA4;
            color: white;
        }}
        
        .btn-export {{
            background: #E67E22;
            color: white;
        }}
        
        .btn-reset {{
            background: #C0392B;
            color: white;
        }}
        
        .btn-edit-mode {{
            background: #9B59B6;
            color: white;
        }}
        
        /* Sayfa Numaraları (Yazdırma için) */
        @page {{
            margin: 2cm;
            @bottom-right {{
                content: "Sayfa " counter(page) " / " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
            @bottom-left {{
                content: "HSE Kök Neden Analizi - {cover.get('ref_no', 'N/A')}";
                font-size: 10pt;
                color: #666;
            }}
        }}
        
        /* Yazdırma Ayarları */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                max-width: none;
            }}
            
            .section {{
                page-break-inside: avoid;
            }}
            
            .section-header {{
                page-break-after: avoid;
            }}
            
            .root-cause-box {{
                page-break-inside: avoid;
            }}
            
            .nav-menu, .nav-toggle, .edit-toolbar {{
                display: none !important;
            }}
            
            /* Sayfa numaraları için footer */
            .page-footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 10pt;
                color: #666;
                padding: 10px;
                border-top: 1px solid #ddd;
            }}
            
            /* Bölüm başlarında sayfa ayırıcı */
            .section-header {{
                page-break-before: always;
            }}
            
            .cover {{
                page-break-after: always;
            }}
        }}
        
        /* Düzenlenebilir alanlar için */
        [contenteditable="true"] {{
            outline: none;
            transition: background 0.2s;
            position: relative;
        }}
        
        [contenteditable="true"]:hover {{
            background: #FFFACD;
        }}
        
        [contenteditable="true"]:focus {{
            background: #FFFFE0;
            border: 1px dashed #E67E22;
            padding: 5px;
        }}
        
        [contenteditable="true"]:hover::after {{
            content: "✏️ Düzenlemek için tıklayın";
            position: absolute;
            top: -25px;
            left: 0;
            background: #E67E22;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            white-space: nowrap;
            z-index: 100;
        }}
        
        .edit-hint {{
            color: #999;
            font-size: 0.85em;
            font-style: italic;
            margin-top: 5px;
        }}
        
        /* Scroll-to-top button */
        .scroll-top {{
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: #1B3A5C;
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5em;
            display: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 998;
        }}
        
        .scroll-top:hover {{
            background: #2E6DA4;
        }}
        
        .scroll-top.visible {{
            display: block;
        }}
        
        /* Highlight effect for navigation */
        .section.highlighted {{
            animation: highlight 1s ease-in-out;
        }}
        
        @keyframes highlight {{
            0% {{ background: transparent; }}
            50% {{ background: #FFFACD; }}
            100% {{ background: transparent; }}
        }}
    </style>
</head>
<body>
    <!-- Navigasyon Toggle Butonu -->
    <button class="nav-toggle" onclick="toggleNav()">📋 İçindekiler</button>
    
    <!-- Navigasyon Menüsü -->
    <div class="nav-menu" id="navMenu" style="display: none;">
        <h3>İÇİNDEKİLER</h3>
        <ul>
            <li><a href="#cover" onclick="scrollToSection('cover')">🏠 Kapak Sayfası</a></li>
            <li><a href="#executive-summary" onclick="scrollToSection('executive-summary')">📊 Yönetici Özeti</a></li>
            <li><a href="#incident-details" onclick="scrollToSection('incident-details')">📝 Olay Bilgileri</a></li>
            <li><a href="#analysis-method" onclick="scrollToSection('analysis-method')">🔬 Analiz Yöntemi</a></li>
            <li><a href="#branches" onclick="scrollToSection('branches')">🌳 Kritik Faktörler</a></li>
            <li><a href="#contributing-factors" onclick="scrollToSection('contributing-factors')">⚠️ Katkıda Bulunan Faktörler</a></li>
            <li><a href="#corrective-actions" onclick="scrollToSection('corrective-actions')">✅ Düzeltici Faaliyetler</a></li>
            <li><a href="#lessons-learned" onclick="scrollToSection('lessons-learned')">💡 Çıkarılan Dersler</a></li>
            <li><a href="#conclusion" onclick="scrollToSection('conclusion')">🏁 Sonuç</a></li>
            <li><a href="#signatures" onclick="scrollToSection('signatures')">✍️ İmzalar</a></li>
        </ul>
    </div>
    
    <!-- Düzenleme Toolbar -->
    <div class="edit-toolbar" id="editToolbar">
        <button class="toolbar-btn btn-edit-mode" onclick="toggleEditMode()">
            <span id="editModeText">🔒 Düzenleme Modu: KAPALI</span>
        </button>
        <button class="toolbar-btn btn-save" onclick="saveReport()" title="Değişiklikleri Kaydet">
            💾 Kaydet
        </button>
        <button class="toolbar-btn btn-print" onclick="printReport()" title="Yazdır / PDF Kaydet">
            🖨️ Yazdır
        </button>
        <button class="toolbar-btn btn-export" onclick="exportHTML()" title="HTML Olarak İndir">
            📥 HTML İndir
        </button>
        <button class="toolbar-btn btn-reset" onclick="resetReport()" title="Orijinal Haline Döndür">
            🔄 Sıfırla
        </button>
    </div>
    
    <!-- Scroll to Top Button -->
    <button class="scroll-top" id="scrollTopBtn" onclick="scrollToTop()">↑</button>
    
    <div class="container">
        <!-- KAPAK SAYFASI -->
        <div class="cover" id="cover">
            <h1 contenteditable="true">{cover.get('title', 'KÖK NEDEN ANALİZİ RAPORU')}</h1>
            
            <div class="confidential-banner" contenteditable="true">
                {cover.get('confidentiality', 'GİZLİ - SADECE YETKİLİ PERSONELİN ERİŞİMİNE AÇIKTIR')}
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Referans No</div>
                    <div class="info-value" contenteditable="true">{cover.get('ref_no', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Tarih</div>
                    <div class="info-value" contenteditable="true">{cover.get('date', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Lokasyon</div>
                    <div class="info-value" contenteditable="true">{cover.get('location', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Olay Tipi</div>
                    <div class="info-value" contenteditable="true">{cover.get('incident_type', 'N/A')}</div>
                </div>
            </div>
            
            <div class="incident-summary">
                <h3>OLAY ÖZETİ</h3>
                <p contenteditable="true">{cover.get('incident_summary_short', '')}</p>
            </div>
        </div>
        
        <!-- İÇERİK -->
        <div class="content">
"""

        # 1. YÖNETİCİ ÖZETİ
        html += self._html_executive_summary(executive_summary, root_causes)
        
        # 2. OLAY BİLGİLERİ
        html += self._html_incident_details(incident_details)
        
        # 3. ANALİZ YÖNTEMİ
        html += self._html_analysis_method(analysis_method)
        
        # 4-N. DALLAR
        html += self._html_branches(branches)
        
        # Section 6 removed - root causes already in Critical Factor sections
        # N+1. KÖK NEDENLER
        # html += self._html_root_causes(root_causes)
        
        # N+2. KATKIDA BULUNAN FAKTÖRLER
        html += self._html_contributing_factors(contributing_factors)
        
        # N+3. DÜZELTİCİ FAALİYETLER
        html += self._html_corrective_actions(corrective_actions)
        
        # N+4. ÇIKARILAN DERSLER
        html += self._html_lessons_learned(lessons_learned)
        
        # N+5. SONUÇ
        html += self._html_conclusion(conclusion)
        
        # N+6. İMZA SAYFASI
        html += self._html_signatures()

        html += """
        </div>
    </div>
    
    <script>
        // Navigasyon toggle
        function toggleNav() {
            const menu = document.getElementById('navMenu');
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
        
        // Bölüme kaydır ve highlight
        function scrollToSection(sectionId) {
            const element = document.getElementById(sectionId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                element.classList.add('highlighted');
                setTimeout(() => element.classList.remove('highlighted'), 1000);
            }
            // Mobilde menüyü kapat
            if (window.innerWidth < 768) {
                document.getElementById('navMenu').style.display = 'none';
            }
        }
        
        // Scroll to top
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        // Scroll position tracking
        window.addEventListener('scroll', function() {
            const scrollBtn = document.getElementById('scrollTopBtn');
            if (window.pageYOffset > 300) {
                scrollBtn.classList.add('visible');
            } else {
                scrollBtn.classList.remove('visible');
            }
        });
        
        // Düzenleme modu toggle
        let editMode = false;
        function toggleEditMode() {
            editMode = !editMode;
            const editableElements = document.querySelectorAll('[contenteditable]');
            const editModeText = document.getElementById('editModeText');
            const toolbar = document.getElementById('editToolbar');
            
            if (editMode) {
                editableElements.forEach(el => el.setAttribute('contenteditable', 'true'));
                editModeText.textContent = '🔓 Düzenleme Modu: AÇIK';
                toolbar.classList.add('active');
                showNotification('✏️ Düzenleme modu AÇIK - İstediğiniz alanı düzenleyebilirsiniz', 'success');
            } else {
                editableElements.forEach(el => el.setAttribute('contenteditable', 'false'));
                editModeText.textContent = '🔒 Düzenleme Modu: KAPALI';
                toolbar.classList.remove('active');
                showNotification('🔒 Düzenleme modu KAPALI', 'info');
            }
        }
        
        // Raporu kaydet (localStorage)
        function saveReport() {
            const html = document.documentElement.outerHTML;
            const timestamp = new Date().toISOString();
            localStorage.setItem('hse_report_saved', html);
            localStorage.setItem('hse_report_saved_time', timestamp);
            showNotification('💾 Rapor başarıyla kaydedildi!', 'success');
            console.log('Rapor kaydedildi:', timestamp);
        }
        
        // Yazdır / PDF kaydet
        function printReport() {
            // Düzenleme modunu kapat
            if (editMode) {
                toggleEditMode();
            }
            
            showNotification('🖨️ Yazdırma ekranı açılıyor...', 'info');
            setTimeout(() => {
                window.print();
            }, 500);
        }
        
        // HTML olarak indir
        function exportHTML() {
            const html = document.documentElement.outerHTML;
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'hse_report_' + new Date().getTime() + '.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showNotification('📥 HTML dosyası indiriliyor...', 'success');
        }
        
        // Orijinal haline döndür
        function resetReport() {
            if (confirm('⚠️ Tüm değişiklikler kaybolacak. Orijinal rapora dönmek istediğinizden emin misiniz?')) {
                location.reload();
                showNotification('🔄 Rapor sıfırlandı', 'info');
            }
        }
        
        // Bildirim göster
        function showNotification(message, type = 'info') {
            // Mevcut bildirimi kaldır
            const existing = document.querySelector('.notification');
            if (existing) {
                existing.remove();
            }
            
            // Yeni bildirim oluştur
            const notification = document.createElement('div');
            notification.className = 'notification notification-' + type;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: ${type === 'success' ? '#27AE60' : type === 'error' ? '#C0392B' : '#2E6DA4'};
                color: white;
                padding: 15px 20px;
                border-radius: 5px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                font-weight: bold;
            `;
            
            document.body.appendChild(notification);
            
            // 3 saniye sonra kaldır
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        // Animasyonlar
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Otomatik kaydetme
        let autoSaveTimeout;
        document.addEventListener('input', function(e) {
            if (e.target.hasAttribute('contenteditable')) {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    const html = document.documentElement.outerHTML;
                    localStorage.setItem('hse_report_autosave', html);
                    localStorage.setItem('hse_report_autosave_time', new Date().toISOString());
                    console.log('📝 Otomatik kaydedildi:', new Date().toLocaleTimeString());
                }, 2000); // 2 saniye sonra otomatik kaydet
            }
        });
        
        // Sayfa yüklendiğinde toolbar'ı göster
        window.addEventListener('load', function() {
            document.getElementById('editToolbar').classList.add('active');
            
            // Kaydedilmiş rapor var mı kontrol et
            const savedTime = localStorage.getItem('hse_report_saved_time');
            if (savedTime) {
                console.log('💾 Son kayıt:', new Date(savedTime).toLocaleString('tr-TR'));
            }
            
            showNotification('📄 Rapor yüklendi - Düzenlemek için 🔓 butonuna tıklayın', 'info');
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl+P: Print
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                printReport();
            }
            // Ctrl+S: Save
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                saveReport();
            }
            // Ctrl+E: Toggle edit mode
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                toggleEditMode();
            }
            // Escape: Close nav
            if (e.key === 'Escape') {
                document.getElementById('navMenu').style.display = 'none';
            }
        });
        
        // PDF hint
        console.log('💡 KULLANIM İPUÇLARI:');
        console.log('📋 Ctrl+E: Düzenleme modunu aç/kapat');
        console.log('💾 Ctrl+S: Kaydet');
        console.log('🖨️ Ctrl+P: Yazdır / PDF kaydet');
        console.log('📥 HTML İndir: Raporu HTML dosyası olarak indir');
        console.log('🔄 Sıfırla: Tüm değişiklikleri geri al');
    </script>
</body>
</html>
"""
        return html

    def _html_executive_summary(self, es: Dict, root_causes: List[Dict]) -> str:
        """Yönetici özeti HTML."""
        html = """
        <div class="section" id="executive-summary">
            <div class="section-header">1. YÖNETİCİ ÖZETİ</div>
            
            <div class="subsection-header">1.1 Olay Özeti</div>
"""
        
        for field in ["what_happened", "where_happened", "who_affected", "immediate_response"]:
            if es.get(field):
                html += f'<div class="paragraph" contenteditable="true">{es[field]}</div>\n'
        
        html += """
            <div class="subsection-header">1.2 Temel Bulgular</div>
            <ul class="bullet-list">
"""
        for finding in es.get("key_findings", []):
            html += f'<li contenteditable="true">{finding}</li>\n'
        
        html += """
            </ul>
            
            <div class="subsection-header">1.3 Kritik Kök Nedenler</div>
"""
        
        colors = ['red', 'orange', 'green', 'blue']
        for i, rc in enumerate(root_causes[:4]):
            color = colors[i % len(colors)]
            desc = rc.get("detailed_description", "")
            short_desc = desc[:300] + "..." if len(desc) > 300 else desc
            html += f"""
            <div class="colored-box box-{color}">
                <div class="box-header" contenteditable="true">KÖK NEDEN {i+1}: {rc.get('title', '')}</div>
                <div class="box-content" contenteditable="true">[{rc.get('code','')} / {rc.get('category','')}]
                
{short_desc}</div>
            </div>
"""
        
        html += """
            <div class="subsection-header">1.4 Acil Eylemler</div>
            <table>
                <thead>
                    <tr>
                        <th>Acil Eylem</th>
                        <th>Sorumlu</th>
                        <th>Durum</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for act in es.get("immediate_actions", []):
            html += f"""
                    <tr>
                        <td contenteditable="true">{act.get('action', '')}</td>
                        <td contenteditable="true">{act.get('responsible', '')}</td>
                        <td contenteditable="true">{act.get('status', '')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _html_incident_details(self, details: Dict) -> str:
        """Olay bilgileri HTML."""
        html = """
        <div class="section" id="incident-details">
            <div class="section-header">2. OLAY BİLGİLERİ</div>
            
            <div class="subsection-header">2.1 Detaylı Bilgi Tablosu</div>
            <table>
"""
        
        for key, val in details.get("info_table", {}).items():
            html += f"""
                <tr>
                    <td style="background: #D6E4F0; font-weight: bold; color: #1B3A5C;">{key}</td>
                    <td contenteditable="true">{val}</td>
                </tr>
"""
        
        html += """
            </table>
            
            <div class="subsection-header">2.2 Olay Detayları</div>
            <table>
"""
        
        for key, val in details.get("event_table", {}).items():
            html += f"""
                <tr>
                    <td style="background: #D6E4F0; font-weight: bold; color: #1B3A5C;">{key}</td>
                    <td contenteditable="true">{val}</td>
                </tr>
"""
        
        html += """
            </table>
            
            <div class="subsection-header">2.3 Kronolojik Olay Akışı</div>
            <div class="timeline">
"""
        
        for step in details.get("timeline", []):
            html += f"""
                <div class="timeline-item">
                    <div class="timeline-time" contenteditable="true">{step.get('time', '')}</div>
                    <div class="timeline-event" contenteditable="true">{step.get('event', '')}</div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
        return html

    def _html_analysis_method(self, method: Dict) -> str:
        """Analiz yöntemi HTML."""
        html = f"""
        <div class="section" id="analysis-method">
            <div class="section-header">3. ANALİZ YÖNTEMİ</div>
            
            <div class="subsection-header">3.1 Metodoloji</div>
            <div class="paragraph" contenteditable="true">{method.get('methodology_description', '')}</div>
            
            <div class="subsection-header">3.2 5-Why Tekniği</div>
            <div class="paragraph" contenteditable="true">{method.get('five_why_explanation', '')}</div>
            
            <div class="subsection-header">3.3 Kod Sistemi</div>
            <table>
                <thead>
                    <tr>
                        <th>Kod</th>
                        <th>Kategori</th>
                        <th>Açıklama</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for code in method.get("code_system", []):
            html += f"""
                    <tr>
                        <td style="font-weight: bold; color: #1B3A5C;">{code.get('code', '')}</td>
                        <td contenteditable="true">{code.get('category', '')}</td>
                        <td contenteditable="true">{code.get('description', '')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
            
            <div class="subsection-header">3.4 Analiz Ekibi</div>
            <table>
                <thead>
                    <tr>
                        <th>İsim</th>
                        <th>Rol</th>
                        <th>Tarih</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for member in method.get("team_members", []):
            html += f"""
                    <tr>
                        <td contenteditable="true">{member.get('name', '')}</td>
                        <td contenteditable="true">{member.get('role', '')}</td>
                        <td contenteditable="true">{member.get('date', '')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _html_branches(self, branches: List[Dict]) -> str:
        """Analiz dalları HTML."""
        html = """
        <div class="section" id="branches">
"""
        
        for branch in branches:
            bn = branch.get("branch_number", 1)
            html += f"""
            <div class="subsection">
            <div class="section-header">{3+bn}. {branch.get('branch_title', f'KRİTİK FAKTÖR {bn}')}</div>
            
            <div class="subsection-header">{3+bn}.1 Başlangıç Durumu ve Doğrudan Neden</div>
            <div class="paragraph" contenteditable="true">{branch.get('initial_condition', '')}</div>
            <div class="paragraph" contenteditable="true" style="font-weight: bold;">{branch.get('direct_cause', '')}</div>
            
            <div class="subsection-header">{3+bn}.2 5-Why Analiz Zinciri</div>
            <div class="why-chain">
"""
            
            for why in branch.get("why_chain", []):
                html += f"""
                <div class="why-item">
                    <div class="why-number">NEDEN {why.get('number', '')}</div>
                    <div class="why-question" contenteditable="true">{why.get('question', '')}</div>
                    <div class="why-answer" contenteditable="true">→ {why.get('answer', '')}</div>
                    <span class="why-code">{why.get('code', '')} - {why.get('category', '')}</span>
                </div>
"""
            
            colors = ['red', 'orange', 'green', 'blue']
            color = colors[(bn - 1) % len(colors)]
            
            html += f"""
            </div>
            
            <div class="subsection-header">{3+bn}.3 Kök Neden</div>
            <div class="colored-box box-{color}">
                <div class="box-header" contenteditable="true">KÖK NEDEN {bn}: {branch.get('root_cause_title', '')}</div>
                <div class="box-content" contenteditable="true">[{branch.get('root_cause_code', '')} / {branch.get('root_cause_category', '')}]

{branch.get('root_cause_detail', '')}</div>
            </div>
"""
            
            if branch.get("organizational_factors"):
                html += f"""
            <div class="subsection-header">{3+bn}.4 Organizasyonel Faktörler</div>
            <ul class="bullet-list">
"""
                for factor in branch.get("organizational_factors", []):
                    html += f'<li contenteditable="true">{factor}</li>\n'
                html += """
            </ul>
"""
            
            html += """
            </div>
"""
        
        html += """
        </div>
"""
        
        return html

    # Section 6 removed - root causes already detailed in Critical Factor sections
    # def _html_root_causes(self, root_causes: List[Dict]) -> str:
    #     """Nihai kök nedenler HTML."""
    #     html = """
    #     <div class="section" id="root-causes">
    #         <div class="section-header">6. NİHAİ KÖK NEDENLER</div>
    # """
    #     
    #     for i, rc in enumerate(root_causes):
    #         html += f"""
    #         <div class="root-cause-box root-cause-{i+1}">
    #             <div class="root-cause-header" contenteditable="true">KÖK NEDEN {i+1}: {rc.get('title', '')}</div>
    #             <div class="root-cause-content">
    #                 <table style="margin-bottom: 20px;">
    #                     <tr>
    #                         <td style="background: #D6E4F0; font-weight: bold; width: 30%;">Kod</td>
    #                         <td contenteditable="true">{rc.get('code', '')}</td>
    #                     </tr>
    #                     <tr>
    #                         <td style="background: #D6E4F0; font-weight: bold;">Kategori</td>
    #                         <td contenteditable="true">{rc.get('category', '')}</td>
    #                     </tr>
    #                     <tr>
    #                         <td style="background: #D6E4F0; font-weight: bold;">İlgili Birimler</td>
    #                         <td contenteditable="true">{rc.get('contributing_organizations', '')}</td>
    #                     </tr>
    #                 </table>
    #                 
    #                 <div class="paragraph" contenteditable="true">{rc.get('detailed_description', '')}</div>
    #                 
    #                 <h4 style="margin-top: 20px; color: #1B3A5C;">Bu Nedenden Kaynaklanan Etkiler:</h4>
    #                 <ul class="bullet-list">
    # """
    #         
    #         for impact in rc.get("impacts", []):
    #             html += f'<li contenteditable="true">{impact}</li>\n'
    #         
    #         html += """
    #                 </ul>
    #             </div>
    #         </div>
    # """
    #     
    #     html += """
    #     </div>
    # """
    #     return html

    def _html_contributing_factors(self, factors: List[Dict]) -> str:
        """Katkıda bulunan faktörler HTML."""
        html = """
        <div class="section" id="contributing-factors">
            <div class="section-header">6. KATKIDA BULUNAN FAKTÖRLER</div>
            
            <table>
                <thead>
                    <tr>
                        <th>Faktör Türü</th>
                        <th>Açıklama</th>
                        <th>Etki Seviyesi</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for factor in factors:
            impact = factor.get("impact_level", "Orta")
            impact_class = f"impact-{impact.lower()}" if impact.lower() in ['high', 'yüksek'] else (f"impact-medium" if impact.lower() in ['medium', 'orta'] else "impact-low")
            
            html += f"""
                    <tr>
                        <td style="font-weight: bold;" contenteditable="true">{factor.get('factor_type', '')}</td>
                        <td contenteditable="true">{factor.get('description', '')}</td>
                        <td class="{impact_class}" contenteditable="true">{impact}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _html_corrective_actions(self, actions: List[Dict]) -> str:
        """Düzeltici faaliyetler HTML."""
        html = """
        <div class="section" id="corrective-actions">
            <div class="section-header">7. DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER</div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">No</th>
                        <th style="width: 35%;">Faaliyet</th>
                        <th style="width: 10%;">Öncelik</th>
                        <th style="width: 15%;">Sorumlu</th>
                        <th style="width: 10%;">Süre</th>
                        <th style="width: 25%;">KPI</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for act in actions:
            priority = act.get("priority", "ORTA")
            priority_class = "priority-urgent" if priority == "ACİL" else ("priority-high" if priority == "YÜKSEK" else ("priority-medium" if priority == "ORTA" else "priority-low"))
            
            html += f"""
                    <tr>
                        <td>{act.get('no', '')}</td>
                        <td contenteditable="true">{act.get('action', '')}</td>
                        <td><span class="{priority_class}">{priority}</span></td>
                        <td contenteditable="true">{act.get('responsible', '')}</td>
                        <td contenteditable="true">{act.get('deadline', '')}</td>
                        <td contenteditable="true">{act.get('kpi', '')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _html_lessons_learned(self, lessons: Dict) -> str:
        """Çıkarılan dersler HTML."""
        sections = [
            ("NE YAPILMALI", lessons.get("what_to_do", []), "green"),
            ("UZUN VADELİ ÇÖZÜMLER", lessons.get("long_term", []), "blue"),
            ("İLETİŞİM VE PAYLAŞIM", lessons.get("communication", []), "orange"),
            ("EĞİTİM VE FARKINDALIK", lessons.get("training", []), "red"),
        ]
        
        html = """
        <div class="section" id="lessons-learned">
            <div class="section-header">8. ÇIKARILAN DERSLER</div>
"""
        
        for title, items, color in sections:
            if items:
                content = "\n".join(f"• {item}" for item in items)
                html += f"""
            <div class="colored-box box-{color}">
                <div class="box-header">{title}</div>
                <div class="box-content" contenteditable="true">{content}</div>
            </div>
"""
        
        html += """
        </div>
"""
        return html

    def _html_conclusion(self, conclusion: Dict) -> str:
        """Sonuç ve öneriler HTML."""
        html = f"""
        <div class="section" id="conclusion">
            <div class="section-header">9. SONUÇ VE ÖNERİLER</div>
            
            <div class="subsection-header">9.1 Genel Değerlendirme</div>
            <div class="paragraph" contenteditable="true">{conclusion.get('overall_assessment', '')}</div>
            
            <div class="subsection-header">9.2 Kısa Vadeli Önlemler (1-2 Ay)</div>
            <ul class="bullet-list">
"""
        
        for measure in conclusion.get("short_term_measures", []):
            html += f'<li contenteditable="true">{measure}</li>\n'
        
        html += """
            </ul>
            
            <div class="subsection-header">9.3 Uzun Vadeli İyileştirmeler (3-12 Ay)</div>
            <ul class="bullet-list">
"""
        
        for improvement in conclusion.get("long_term_improvements", []):
            html += f'<li contenteditable="true">{improvement}</li>\n'
        
        html += """
            </ul>
            
            <div class="subsection-header">9.4 Mevcut vs Hedef Karşılaştırması</div>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Kriter</th>
                        <th>Mevcut Durum</th>
                        <th>Hedeflenen</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for row in conclusion.get("comparison_table", []):
            html += f"""
                    <tr>
                        <td>{row.get('criterion', '')}</td>
                        <td class="current" contenteditable="true">{row.get('current', '')}</td>
                        <td class="target" contenteditable="true">{row.get('target', '')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
        return html

    def _html_signatures(self) -> str:
        """İmza sayfası HTML."""
        html = """
        <div class="section signature-section" id="signatures">
            <div class="section-header">10. ONAY VE İMZA SAYFASI</div>
            
            <table class="signature-table">
                <thead>
                    <tr>
                        <th>Rol</th>
                        <th>İsim</th>
                        <th>Ünvan</th>
                        <th>İmza / Tarih</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: bold; color: #1B3A5C;">HAZIRLAYAN</td>
                        <td contenteditable="true">HSE Uzmanı</td>
                        <td contenteditable="true">HSE Kök Neden Analisti</td>
                        <td contenteditable="true">
                            <div class="signature-line">
                                _____________________<br>
                                _____ / _____ / _____
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold; color: #1B3A5C;">İNCELEYEN</td>
                        <td contenteditable="true">HSE Yöneticisi</td>
                        <td contenteditable="true">HSE Departman Yöneticisi</td>
                        <td contenteditable="true">
                            <div class="signature-line">
                                _____________________<br>
                                _____ / _____ / _____
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold; color: #1B3A5C;">ONAYLAYAN</td>
                        <td contenteditable="true">Tesis Müdürü</td>
                        <td contenteditable="true">Genel Operasyon Müdürü</td>
                        <td contenteditable="true">
                            <div class="signature-line">
                                _____________________<br>
                                _____ / _____ / _____
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin-top: 40px; padding: 20px; background: #F5F5F5; border-left: 4px solid #2E6DA4;">
                <p style="margin: 0; color: #666;">
                    <strong>📝 Not:</strong> Bu HTML raporu tamamen düzenlenebilir. Herhangi bir alana tıklayarak içeriği değiştirebilirsiniz.
                    Değişiklikleriniz tarayıcınızın yerel belleğine otomatik olarak kaydedilir.
                </p>
                <p style="margin: 10px 0 0 0; color: #666;">
                    <strong>🖨️ Yazdırma:</strong> Bu raporu PDF olarak kaydetmek için <code>Ctrl+P</code> (veya Cmd+P) tuşlarına basın 
                    ve "PDF olarak kaydet" seçeneğini seçin.
                </p>
            </div>
        </div>
"""
        return html




if __name__ == "__main__":
    print("=" * 70)
    print("🧪 SkillBasedDocxAgent V2 — Standalone Test")
    print("=" * 70)

    outputs = sorted(Path("outputs").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if outputs:
        json_file = outputs[0]
        print(f"�� Kullanılan veri: {json_file}")
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("❌ outputs/*.json bulunamadı!")
        sys.exit(1)

    agent = SkillBasedDocxAgent()
    try:
        out = agent.generate_report(
            investigation_data=data,
            output_path="outputs/HSE_FULL_REPORT_V2.docx",
        )
        print(f"\n�� BAŞARILI! → {out}")
    except Exception as e:
        import traceback
        print(f"\n❌ HATA: {e}")
        traceback.print_exc()
        sys.exit(1)
