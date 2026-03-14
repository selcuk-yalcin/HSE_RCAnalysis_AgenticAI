#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSE Root Cause Analysis PDF Report Generator
SKILL.md tabanlı profesyonel rapor üretici
Kimyasal Yanma (Asit Sıçraması) Olayı - INC-2026-03-5771
"""

import json
import os
import sys
from functools import partial

# ─────────────────────────────────────────────
# BAĞIMLILIK KONTROLÜ
# ─────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
except ImportError:
    print("ReportLab bulunamadı. Yükleniyor...")
    os.system("pip install reportlab --break-system-packages -q")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.pdfgen import canvas as pdfcanvas

# ─────────────────────────────────────────────
# SAYFA SABİTLERİ
# ─────────────────────────────────────────────
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40

# ─────────────────────────────────────────────
# HSE KURUMSAL RENK PALETİ
# ─────────────────────────────────────────────
class HSEColors:
    primary_dark   = colors.HexColor("#1A2744")
    primary_mid    = colors.HexColor("#2C4A8A")
    primary_light  = colors.HexColor("#4A90D9")
    accent_orange  = colors.HexColor("#E8631A")
    accent_amber   = colors.HexColor("#F5A623")
    success_green  = colors.HexColor("#2ECC71")
    warning_yellow = colors.HexColor("#F39C12")
    danger_red     = colors.HexColor("#E74C3C")
    medium_orange  = colors.HexColor("#E67E22")
    bg_light       = colors.HexColor("#F8F9FA")
    bg_gray        = colors.HexColor("#ECF0F1")
    text_dark      = colors.HexColor("#2C3E50")
    text_medium    = colors.HexColor("#5D6D7E")
    border_light   = colors.HexColor("#BDC3C7")
    white          = colors.white
    black          = colors.black

C = HSEColors()

SEVERITY_COLORS = {
    "CRITICAL":    C.danger_red,
    "HIGH":        C.accent_orange,
    "MEDIUM":      C.medium_orange,
    "LOW":         C.success_green,
    "IN_PROGRESS": C.warning_yellow,
    "COMPLETED":   C.success_green,
    "PLANNED":     C.primary_light,
}

CONFIDENCE_COLORS = {
    "HIGH":   C.success_green,
    "MEDIUM": C.warning_yellow,
    "LOW":    C.danger_red,
}

# ─────────────────────────────────────────────
# VERİ TEMİZLEME YARDIMCILARI
# ─────────────────────────────────────────────
def clean_text(text, max_len=None):
    """Metni temizle, satır sonlarını ve fazla boşlukları kaldır."""
    if not text:
        return ""
    # Satır başı/sonu boşlukları temizle
    cleaned = " ".join(str(text).split())
    if max_len and len(cleaned) > max_len:
        cleaned = cleaned[:max_len - 3] + "..."
    return cleaned

def truncate(text, max_len=90):
    """Metni belirtilen uzunlukta kes."""
    text = clean_text(text)
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text

def safe_get(d, key, default=""):
    """Sözlükten güvenli değer al."""
    val = d.get(key, default)
    if val is None:
        return default
    return val

# ─────────────────────────────────────────────
# JSON DOĞRULAMA
# ─────────────────────────────────────────────
def validate_rca_json(data):
    """Gelen JSON'u doğrula ve eksik alanları kontrol et."""
    required_fields = ["incident_title", "five_whys", "root_cause"]
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        print(f"UYARI: Eksik alanlar tespit edildi: {missing}")
        # Eksik alanları varsayılan değerlerle doldur
        for field in missing:
            if field == "five_whys":
                data[field] = []
            elif field == "corrective_actions":
                data[field] = []
            else:
                data[field] = "Bilgi mevcut değil"
    
    why_count = len(data.get("five_whys", []))
    if why_count < 3:
        print(f"UYARI: {why_count} Why zinciri - ideal 5 olmalı. Mevcut verilerle devam ediliyor.")
    elif why_count > 7:
        print(f"UYARI: {why_count} Why zinciri - 7'den fazla. İlk 7 alınacak.")
        data["five_whys"] = data["five_whys"][:7]
    
    # Olay başlığını temizle (çok uzun veya özel karakter içerebilir)
    data["incident_title"] = clean_text(
        data.get("incident_title", "Olay Başlığı Belirtilmemiş"), 
        max_len=80
    )
    
    # Açıklamayı temizle
    desc = data.get("description", "")
    if len(desc) > 2000:
        data["description_full"] = desc
        data["description"] = desc[:2000] + "..."
    
    return data

# ─────────────────────────────────────────────
# HEADER / FOOTER
# ─────────────────────────────────────────────
def add_page_header(canvas_obj, doc, data):
    """Her sayfaya kurumsal header ve footer ekle."""
    canvas_obj.saveState()
    
    # ── Üst Header Bar (lacivert) ──
    canvas_obj.setFillColor(C.primary_dark)
    canvas_obj.rect(0, PAGE_HEIGHT - 58, PAGE_WIDTH, 58, fill=1, stroke=0)
    
    # Sol: HSE logosu / başlık
    canvas_obj.setFillColor(C.white)
    canvas_obj.setFont("Helvetica-Bold", 15)
    canvas_obj.drawString(MARGIN, PAGE_HEIGHT - 24, "HSE")
    
    canvas_obj.setFillColor(C.primary_light)
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.drawString(MARGIN + 36, PAGE_HEIGHT - 20, "ROOT CAUSE ANALYSIS")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(MARGIN + 36, PAGE_HEIGHT - 32, "Kok Neden Analizi Raporu")
    
    # Dikey ayraç
    canvas_obj.setStrokeColor(C.accent_orange)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(MARGIN + 32, PAGE_HEIGHT - 10, MARGIN + 32, PAGE_HEIGHT - 48)
    
    # Sağ: Olay ID ve tarih
    canvas_obj.setFillColor(C.white)
    canvas_obj.setFont("Helvetica-Bold", 10)
    inc_id = safe_get(data, "incident_id", "N/A")
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 20, f"#{inc_id}")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(C.bg_gray)
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 34, 
                               safe_get(data, "incident_date", ""))
    canvas_obj.setFillColor(C.text_medium)
    dept = safe_get(data, "department", "")
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 46, dept[:40])
    
    # Turuncu alt şerit
    canvas_obj.setFillColor(C.accent_orange)
    canvas_obj.rect(0, PAGE_HEIGHT - 61, PAGE_WIDTH, 3, fill=1, stroke=0)
    
    # ── Alt Footer ──
    canvas_obj.setFillColor(C.bg_gray)
    canvas_obj.rect(0, 0, PAGE_WIDTH, 28, fill=1, stroke=0)
    
    # Footer sol
    canvas_obj.setFillColor(C.text_medium)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawString(MARGIN, 10, "GİZLİ — Yalnizca İc Kullanim İcin | HSE Root Cause Analysis")
    
    # Footer sağ: sayfa numarası
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, 10, 
                               f"Sayfa {doc.page}")
    
    # Footer orta: ince çizgi
    canvas_obj.setStrokeColor(C.border_light)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(MARGIN, 28, PAGE_WIDTH - MARGIN, 28)
    
    canvas_obj.restoreState()

# ─────────────────────────────────────────────
# KAPAK SAYFASI
# ─────────────────────────────────────────────
def build_cover_page(data):
    """Profesyonel kapak sayfası elemanları üret."""
    elements = []
    
    # ── Ana Başlık Kutusu ──
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=C.white,
        alignment=TA_CENTER,
        leading=30,
        spaceAfter=6
    )
    cover_sub_style = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica",
        fontSize=12,
        textColor=C.primary_light,
        alignment=TA_CENTER,
        leading=16
    )
    cover_type_style = ParagraphStyle(
        "CoverType",
        fontName="Helvetica",
        fontSize=10,
        textColor=C.accent_amber,
        alignment=TA_CENTER,
        leading=14
    )
    
    inc_type = safe_get(data, "incident_type", "Kaza Analizi")
    
    cover_data = [
        [Paragraph("ROOT CAUSE ANALYSIS", cover_title_style)],
        [Paragraph("HSE Kok Neden Analizi Raporu", cover_sub_style)],
        [Spacer(1, 8)],
        [Paragraph(f"[ {inc_type} ]", cover_type_style)],
    ]
    
    cover_table = Table(cover_data, colWidths=[PAGE_WIDTH - 2 * MARGIN])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C.primary_dark),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 30),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
    ]))
    
    elements.append(Spacer(1, 15))
    elements.append(cover_table)
    elements.append(Spacer(1, 12))
    
    # ── Severity Badge ──
    sev = safe_get(data, "severity", "HIGH")
    sev_color = SEVERITY_COLORS.get(sev, C.accent_orange)
    
    badge_style = ParagraphStyle(
        "Badge",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=C.white,
        alignment=TA_CENTER
    )
    
    badge_table = Table(
        [[Paragraph(f"OLAY SIDDETI: {sev}", badge_style)]],
        colWidths=[220]
    )
    badge_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), sev_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))
    
    # Badge'i ortala
    badge_wrapper = Table([[badge_table]], colWidths=[PAGE_WIDTH - 2 * MARGIN])
    badge_wrapper.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(badge_wrapper)
    elements.append(Spacer(1, 18))
    
    # ── Olay Bilgileri Tablosu ──
    info_label_style = ParagraphStyle(
        "InfoLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=C.text_medium
    )
    info_value_style = ParagraphStyle(
        "InfoValue",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=C.text_dark
    )
    info_value_small = ParagraphStyle(
        "InfoValueSmall",
        fontName="Helvetica",
        fontSize=9,
        textColor=C.text_dark
    )
    
    # Başlık satırı (tam genişlik)
    title_style = ParagraphStyle(
        "TitleRow",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=C.primary_dark,
        leading=16
    )
    
    inc_title = safe_get(data, "incident_title", "Olay Basliği Belirtilmemis")
    
    title_row = Table(
        [[Paragraph(inc_title, title_style)]],
        colWidths=[PAGE_WIDTH - 2 * MARGIN]
    )
    title_row.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 15),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 15),
        ("LINEBEFORE",    (0, 0), (0, -1), 5, C.accent_orange),
    ]))
    elements.append(title_row)
    elements.append(Spacer(1, 8))
    
    # 4 kolonlu bilgi tablosu
    col_w = (PAGE_WIDTH - 2 * MARGIN) / 4
    
    info_rows = [
        [
            Paragraph("OLAY TARİHİ", info_label_style),
            Paragraph(safe_get(data, "incident_date", "-"), info_value_style),
            Paragraph("LOKASYON", info_label_style),
            Paragraph(safe_get(data, "location", "-"), info_value_small),
        ],
        [
            Paragraph("DEPARTMAN", info_label_style),
            Paragraph(safe_get(data, "department", "-"), info_value_small),
            Paragraph("OLAY TÜRÜ", info_label_style),
            Paragraph(safe_get(data, "incident_type", "-"), info_value_small),
        ],
        [
            Paragraph("RAPORLAYAN", info_label_style),
            Paragraph(safe_get(data, "reported_by", "-"), info_value_small),
            Paragraph("İNCELEYEN", info_label_style),
            Paragraph(safe_get(data, "investigated_by", "-"), info_value_small),
        ],
        [
            Paragraph("İNCELEME TARİHİ", info_label_style),
            Paragraph(safe_get(data, "investigation_date", "-"), info_value_style),
            Paragraph("ANALİZ YÖNTEMİ", info_label_style),
            Paragraph(safe_get(data, "analysis_method", "5-Why Analizi"), info_value_small),
        ],
    ]
    
    info_table = Table(info_rows, colWidths=[col_w * 0.85, col_w * 1.15, col_w * 0.85, col_w * 1.15])
    info_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), C.bg_gray),
        ("BACKGROUND",    (2, 0), (2, -1), C.bg_gray),
        ("BACKGROUND",    (1, 0), (1, -1), C.white),
        ("BACKGROUND",    (3, 0), (3, -1), C.white),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    return elements

# ─────────────────────────────────────────────
# OLAY AÇIKLAMASI BÖLÜMÜ
# ─────────────────────────────────────────────
def build_incident_description(data):
    """Olay açıklaması ve anlık etkiler bölümü."""
    elements = []
    
    h2 = ParagraphStyle(
        "H2", fontName="Helvetica-Bold", fontSize=13,
        textColor=C.primary_mid, spaceAfter=6, spaceBefore=10
    )
    body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=9,
        textColor=C.text_dark, spaceAfter=5, leading=14
    )
    body_bold = ParagraphStyle(
        "BodyBold", fontName="Helvetica-Bold", fontSize=9,
        textColor=C.text_dark, spaceAfter=5, leading=14
    )
    
    elements.append(Paragraph("OLAY AÇIKLAMASI", h2))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=C.accent_orange, spaceAfter=8
    ))
    
    # Açıklama metnini temizle ve bölümlere ayır
    desc_raw = safe_get(data, "description", "Açıklama mevcut değil.")
    
    # Uzun açıklamayı satırlara böl ve temizle
    desc_lines = [line.strip() for line in desc_raw.split('\n') if line.strip()]
    
    # İlk 40 satırı al (çok uzun olabilir)
    desc_lines = desc_lines[:50]
    
    desc_elements = []
    for line in desc_lines:
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')):
            # Bölüm başlıkları
            desc_elements.append(Paragraph(f"<b>{line}</b>", body_bold))
        elif line.startswith(('-', '•', '✅', '⚠️', '❌', '⚠')):
            # Liste öğeleri
            clean_line = line.replace('✅', '[OK]').replace('❌', '[X]').replace('⚠️', '[!]').replace('⚠', '[!]')
            desc_elements.append(Paragraph(f"  {clean_line}", body))
        elif line.startswith('='):
            # Ayraç satırları - atla
            continue
        else:
            desc_elements.append(Paragraph(line, body))
    
    # Açıklama kutusuna koy
    if desc_elements:
        desc_table = Table(
            [[elem] for elem in desc_elements[:30]],  # Max 30 satır
            colWidths=[PAGE_WIDTH - 2 * MARGIN - 20]
        )
        desc_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBEFORE",    (0, 0), (0, -1), 3, C.primary_mid),
        ]))
        elements.append(desc_table)
    
    elements.append(Spacer(1, 12))
    
    # ── Anlık Etkiler ──
    consequences = data.get("immediate_consequences", [])
    if consequences:
        elements.append(Paragraph("ANLIK ETKİLER", 
            ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10,
                           textColor=C.text_dark, spaceAfter=6, spaceBefore=8)))
        
        cons_rows = []
        for c in consequences:
            c_clean = clean_text(str(c))
            if c_clean:
                cons_rows.append([Paragraph(f"• {c_clean}", body)])
        
        if cons_rows:
            cons_table = Table(cons_rows, colWidths=[PAGE_WIDTH - 2 * MARGIN])
            cons_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
                ("LEFTPADDING",   (0, 0), (-1, -1), 15),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEAFTER",     (0, 0), (0, -1), 4, C.accent_orange),
            ]))
            elements.append(cons_table)
    
    return elements

# ─────────────────────────────────────────────
# KPI ÖZET KUTULARI (Canvas tabanlı)
# ─────────────────────────────────────────────
def draw_kpi_boxes(canvas_obj, data, x, y):
    """4 adet KPI özet kutusu çiz."""
    risk = data.get("risk_assessment", {})
    actions = data.get("corrective_actions", [])
    
    completed = sum(1 for a in actions if a.get("status") == "COMPLETED")
    
    kpis = [
        {
            "label": "5-WHY ADIMI",
            "value": str(len(data.get("five_whys", []))),
            "sub": "Analiz Zinciri",
            "color": C.primary_mid,
        },
        {
            "label": "RİSK (ÖNCE)",
            "value": str(risk.get("risk_score_before", "N/A")),
            "sub": risk.get("risk_level_before", ""),
            "color": C.danger_red,
        },
        {
            "label": "RİSK (SONRA)",
            "value": str(risk.get("risk_score_after", "N/A")),
            "sub": risk.get("risk_level_after", ""),
            "color": C.success_green,
        },
        {
            "label": "DÜZELTİCİ",
            "value": str(len(actions)) if actions else "0",
            "sub": f"{completed} Tamamlandi",
            "color": C.accent_orange,
        },
    ]
    
    BOX_W = 118
    BOX_H = 72
    GAP   = 8
    
    for i, kpi in enumerate(kpis):
        bx = x + i * (BOX_W + GAP)
        
        # Renkli üst şerit
        canvas_obj.setFillColor(kpi["color"])
        canvas_obj.roundRect(bx, y, BOX_W, BOX_H, 5, fill=1, stroke=0)
        
        # Beyaz alt alan
        canvas_obj.setFillColor(C.white)
        canvas_obj.rect(bx, y, BOX_W, BOX_H - 14, fill=1, stroke=0)
        
        # Etiket (renkli şeritte)
        canvas_obj.setFillColor(C.white)
        canvas_obj.setFont("Helvetica-Bold", 7)
        canvas_obj.drawCentredString(bx + BOX_W / 2, y + BOX_H - 9, kpi["label"])
        
        # Büyük değer
        canvas_obj.setFillColor(kpi["color"])
        canvas_obj.setFont("Helvetica-Bold", 24)
        canvas_obj.drawCentredString(bx + BOX_W / 2, y + BOX_H - 40, kpi["value"])
        
        # Alt açıklama
        canvas_obj.setFillColor(C.text_medium)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(bx + BOX_W / 2, y + 8, kpi["sub"])
        
        # İnce kenarlık
        canvas_obj.setStrokeColor(C.border_light)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.roundRect(bx, y, BOX_W, BOX_H, 5, fill=0, stroke=1)

# ─────────────────────────────────────────────
# 5-WHY ZİNCİRİ (Flowable tablo formatı)
# ─────────────────────────────────────────────
def build_five_why_section(data):
    """5-Why zincirini görsel tablo formatında oluştur."""
    elements = []
    
    h1 = ParagraphStyle(
        "H1", fontName="Helvetica-Bold", fontSize=16,
        textColor=C.primary_dark, spaceAfter=8, spaceBefore=10
    )
    
    elements.append(Paragraph("5-WHY ANALİZ ZİNCİRİ", h1))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=C.primary_mid, spaceAfter=10
    ))
    
    five_whys = data.get("five_whys", [])
    
    if not five_whys:
        no_data = ParagraphStyle(
            "NoData", fontName="Helvetica-Oblique", fontSize=10,
            textColor=C.text_medium, alignment=TA_CENTER
        )
        elements.append(Paragraph("5-Why analiz verisi henüz mevcut değil.", no_data))
        return elements
    
    for idx, why in enumerate(five_whys):
        why_num  = why.get("why", idx + 1)
        question = clean_text(why.get("question", ""), max_len=120)
        answer   = clean_text(why.get("answer", ""), max_len=120)
        evidence = clean_text(why.get("evidence", ""), max_len=100)
        conf     = why.get("confidence", "MEDIUM")
        conf_hex = {
            "HIGH":   "#2ECC71",
            "MEDIUM": "#F39C12",
            "LOW":    "#E74C3C"
        }.get(conf, "#F39C12")
        
        # ── Soru satırı (lacivert) ──
        q_style = ParagraphStyle(
            f"Q{why_num}",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C.white,
            leading=13
        )
        conf_style = ParagraphStyle(
            f"Conf{why_num}",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=C.white,
            alignment=TA_CENTER
        )
        
        # Neden numarası + soru
        q_text = f"NEDEN {why_num}:  {question}"
        
        q_row = Table(
            [[
                Paragraph(q_text, q_style),
                Paragraph(conf, conf_style)
            ]],
            colWidths=[PAGE_WIDTH - 2 * MARGIN - 75, 70]
        )
        q_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), C.primary_dark),
            ("BACKGROUND",    (1, 0), (1, 0), colors.HexColor(conf_hex)),
            ("TOPPADDING",    (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING",   (0, 0), (0, 0), 12),
            ("RIGHTPADDING",  (0, 0), (0, 0), 8),
            ("LEFTPADDING",   (1, 0), (1, 0), 4),
            ("RIGHTPADDING",  (1, 0), (1, 0), 4),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        
        # ── Cevap satırı ──
        a_style = ParagraphStyle(
            f"A{why_num}",
            fontName="Helvetica",
            fontSize=9,
            textColor=C.text_dark,
            leading=13
        )
        a_bold = ParagraphStyle(
            f"ABold{why_num}",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C.primary_mid
        )
        ev_style = ParagraphStyle(
            f"Ev{why_num}",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=C.text_medium,
            leading=11
        )
        
        a_content = [
            [
                Paragraph("<b>CEVAP:</b>", a_bold),
                Paragraph(answer if answer else "İnceleme devam ediyor...", a_style),
            ],
        ]
        if evidence:
            a_content.append([
                Paragraph("KANIT:", ev_style),
                Paragraph(evidence, ev_style),
            ])
        
        a_row = Table(
            a_content,
            colWidths=[60, PAGE_WIDTH - 2 * MARGIN - 75 - 60]
        )
        a_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        
        # Sağ taraf (conf alanı altı - boş gri)
        right_fill = Table(
            [[""]],
            colWidths=[70]
        )
        right_fill.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C.bg_gray),
        ]))
        
        # Ana why kutusu (soru + cevap yan yana)
        main_row = Table(
            [[q_row], [a_row]],
            colWidths=[PAGE_WIDTH - 2 * MARGIN]
        )
        main_row.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
        ]))
        
        elements.append(KeepTogether([main_row]))
        
        # ── Ok (son eleman hariç) ──
        if idx < len(five_whys) - 1:
            arrow_style = ParagraphStyle(
                "Arrow",
                fontName="Helvetica-Bold",
                fontSize=18,
                textColor=C.accent_orange,
                alignment=TA_CENTER
            )
            arrow_tbl = Table(
                [[Paragraph("v", arrow_style)]],
                colWidths=[PAGE_WIDTH - 2 * MARGIN]
            )
            arrow_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C.white),
                ("TOPPADDING",    (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            elements.append(arrow_tbl)
        else:
            elements.append(Spacer(1, 8))
    
    # ── Kök Neden Kutusu ──
    root_cause = clean_text(safe_get(data, "root_cause", "Kök neden belirleniyor..."), max_len=200)
    
    root_style = ParagraphStyle(
        "Root",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=C.white,
        alignment=TA_CENTER,
        leading=16
    )
    root_label = ParagraphStyle(
        "RootLabel",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.HexColor("#FFCCCC"),
        alignment=TA_CENTER
    )
    
    root_table = Table(
        [
            [Paragraph("KOK NEDEN", root_label)],
            [Paragraph(root_cause, root_style)],
        ],
        colWidths=[PAGE_WIDTH - 2 * MARGIN]
    )
    root_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C.danger_red),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    elements.append(root_table)
    
    return elements

# ─────────────────────────────────────────────
# RİSK MATRİSİ (Canvas tabanlı)
# ─────────────────────────────────────────────
def draw_risk_matrix(canvas_obj, data, x_offset, y_offset):
    """5x5 Risk Matrisi çiz. Öncesi ve sonrası risk noktaları işaretlenir."""
    CELL = 38
    N    = 5
    
    # Matris renk şeması (satır: şiddet 5→1, sütun: olasılık 1→5)
    MATRIX_COLORS = [
        # Şiddet 5 (en üst satır)
        ["#E74C3C", "#E74C3C", "#E74C3C", "#E74C3C", "#E74C3C"],
        # Şiddet 4
        ["#E67E22", "#E74C3C", "#E74C3C", "#E74C3C", "#E74C3C"],
        # Şiddet 3
        ["#F39C12", "#E67E22", "#E67E22", "#E74C3C", "#E74C3C"],
        # Şiddet 2
        ["#2ECC71", "#F39C12", "#F39C12", "#E67E22", "#E67E22"],
        # Şiddet 1 (en alt satır)
        ["#2ECC71", "#2ECC71", "#F39C12", "#F39C12", "#E67E22"],
    ]
    
    risk = data.get("risk_assessment", {})
    
    # ── Başlık ──
    canvas_obj.setFillColor(C.primary_dark)
    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.drawString(x_offset, y_offset + N * CELL + 30, "RİSK MATRİSİ (5x5)")
    
    # ── Eksen etiketleri ──
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.setFillColor(C.text_dark)
    
    # X ekseni (Olasılık)
    canvas_obj.drawCentredString(
        x_offset + N * CELL / 2,
        y_offset - 18,
        "OLASILIK"
    )
    for i in range(N):
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(C.text_medium)
        canvas_obj.drawCentredString(
            x_offset + i * CELL + CELL / 2,
            y_offset - 8,
            str(i + 1)
        )
    
    # Y ekseni (Şiddet) - döndürülmüş metin
    canvas_obj.saveState()
    canvas_obj.rotate(90)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.setFillColor(C.text_dark)
    canvas_obj.drawCentredString(
        y_offset + N * CELL / 2,
        -(x_offset - 22),
        "SİDDET"
    )
    canvas_obj.restoreState()
    
    for i in range(N):
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(C.text_medium)
        canvas_obj.drawRightString(
            x_offset - 5,
            y_offset + i * CELL + CELL / 2 - 3,
            str(i + 1)
        )
    
    # ── Matris hücreleri ──
    for row in range(N):
        for col in range(N):
            cx = x_offset + col * CELL
            cy = y_offset + row * CELL
            
            # Renk: row=0 → şiddet=1 (alt), row=4 → şiddet=5 (üst)
            color_hex = MATRIX_COLORS[N - 1 - row][col]
            canvas_obj.setFillColor(colors.HexColor(color_hex))
            canvas_obj.setStrokeColor(C.white)
            canvas_obj.setLineWidth(1)
            canvas_obj.rect(cx, cy, CELL, CELL, fill=1, stroke=1)
            
            # Skor
            score = (col + 1) * (row + 1)
            canvas_obj.setFillColor(C.white)
            canvas_obj.setFont("Helvetica-Bold", 8)
            canvas_obj.drawCentredString(cx + CELL / 2, cy + CELL / 2 - 3, str(score))
    
    # ── Risk noktaları ──
    L_before = risk.get("likelihood_before", 4) - 1
    S_before = risk.get("severity_before", 5)  - 1
    L_after  = risk.get("likelihood_after",  2) - 1
    S_after  = risk.get("severity_after",    4) - 1
    
    # Öncesi: lacivert daire
    bx = x_offset + L_before * CELL + CELL / 2
    by = y_offset + S_before * CELL + CELL / 2
    canvas_obj.setFillColor(C.primary_dark)
    canvas_obj.setStrokeColor(C.white)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.circle(bx, by, 10, fill=1, stroke=1)
    canvas_obj.setFillColor(C.white)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawCentredString(bx, by - 3, "O")
    
    # Sonrası: yeşil daire
    ax = x_offset + L_after * CELL + CELL / 2
    ay = y_offset + S_after * CELL + CELL / 2
    canvas_obj.setFillColor(C.success_green)
    canvas_obj.setStrokeColor(C.white)
    canvas_obj.circle(ax, ay, 10, fill=1, stroke=1)
    canvas_obj.setFillColor(C.white)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawCentredString(ax, ay - 3, "S")
    
    # ── Lejant ──
    legend_x = x_offset + N * CELL + 20
    legend_y = y_offset + N * CELL - 10
    
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(C.text_dark)
    canvas_obj.drawString(legend_x, legend_y, "LEJANT")
    
    legend_items = [
        (C.primary_dark, "O = Oncesi Risk"),
        (C.success_green, "S = Sonrasi Risk"),
        (colors.HexColor("#E74C3C"), "Kritik Bolge"),
        (colors.HexColor("#E67E22"), "Yuksek Bolge"),
        (colors.HexColor("#F39C12"), "Orta Bolge"),
        (colors.HexColor("#2ECC71"), "Dusuk Bolge"),
    ]
    
    for i, (lcolor, ltext) in enumerate(legend_items):
        ly = legend_y - 20 - i * 18
        canvas_obj.setFillColor(lcolor)
        canvas_obj.roundRect(legend_x, ly, 12, 12, 2, fill=1, stroke=0)
        canvas_obj.setFillColor(C.text_dark)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(legend_x + 18, ly + 2, ltext)
    
    # ── Risk Skoru Özeti ──
    summary_y = y_offset - 50
    canvas_obj.setFillColor(C.bg_gray)
    canvas_obj.roundRect(x_offset, summary_y, N * CELL + 120, 38, 4, fill=1, stroke=0)
    
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(C.text_dark)
    canvas_obj.drawString(x_offset + 10, summary_y + 22, "Risk Skoru Degisimi:")
    
    score_before = risk.get("risk_score_before", 0)
    score_after  = risk.get("risk_score_after",  0)
    improvement  = score_before - score_after
    
    canvas_obj.setFillColor(C.danger_red)
    canvas_obj.setFont("Helvetica-Bold", 11)
    canvas_obj.drawString(x_offset + 10, summary_y + 8, f"Oncesi: {score_before}")
    
    canvas_obj.setFillColor(C.success_green)
    canvas_obj.drawString(x_offset + 100, summary_y + 8, f"Sonrasi: {score_after}")
    
    canvas_obj.setFillColor(C.primary_mid)
    canvas_obj.drawString(x_offset + 195, summary_y + 8, f"Iyilesme: -{improvement} puan")

# ─────────────────────────────────────────────
# RİSK DEĞERLENDİRME TABLOSU (Flowable)
# ─────────────────────────────────────────────
def build_risk_table(data):
    """Risk değerlendirme tablosu oluştur."""
    elements = []
    
    h1 = ParagraphStyle(
        "H1Risk", fontName="Helvetica-Bold", fontSize=14,
        textColor=C.primary_dark, spaceAfter=6, spaceBefore=10
    )
    label_s = ParagraphStyle(
        "LabelS", fontName="Helvetica-Bold", fontSize=9,
        textColor=C.white
    )
    body_s = ParagraphStyle(
        "BodyS", fontName="Helvetica", fontSize=9,
        textColor=C.text_dark
    )
    body_bold_s = ParagraphStyle(
        "BodyBoldS", fontName="Helvetica-Bold", fontSize=10,
        textColor=C.text_dark
    )
    
    elements.append(Paragraph("RİSK DEĞERLENDİRMESİ", h1))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=C.accent_orange, spaceAfter=10
    ))
    
    risk = data.get("risk_assessment", {})
    
    L_b = risk.get("likelihood_before", "-")
    S_b = risk.get("severity_before",   "-")
    R_b = risk.get("risk_score_before", "-")
    RL_b = risk.get("risk_level_before", "-")
    
    L_a = risk.get("likelihood_after",  "-")
    S_a = risk.get("severity_after",    "-")
    R_a = risk.get("risk_score_after",  "-")
    RL_a = risk.get("risk_level_after", "-")
    
    try:
        imp_l = int(L_b) - int(L_a)
        imp_r = int(R_b) - int(R_a)
    except (ValueError, TypeError):
        imp_l = "-"
        imp_r = "-"
    
    risk_rows = [
        [
            Paragraph("PARAMETRE", label_s),
            Paragraph("ÖNCE", label_s),
            Paragraph("SONRA", label_s),
            Paragraph("İYİLEŞME", label_s),
        ],
        [
            Paragraph("Olasilik", body_s),
            Paragraph(str(L_b), body_bold_s),
            Paragraph(str(L_a), body_bold_s),
            Paragraph(f"↓ {imp_l} puan" if imp_l != "-" else "-", body_s),
        ],
        [
            Paragraph("Siddet", body_s),
            Paragraph(str(S_b), body_bold_s),
            Paragraph(str(S_a), body_bold_s),
            Paragraph("Degerlendiriliyor", body_s),
        ],
        [
            Paragraph("Risk Skoru", body_bold_s),
            Paragraph(str(R_b), body_bold_s),
            Paragraph(str(R_a), body_bold_s),
            Paragraph(f"↓ {imp_r} puan" if imp_r != "-" else "-", body_bold_s),
        ],
        [
            Paragraph("Risk Seviyesi", body_s),
            Paragraph(str(RL_b), body_s),
            Paragraph(str(RL_a), body_s),
            Paragraph("", body_s),
        ],
    ]
    
    risk_tbl = Table(risk_rows, colWidths=[150, 100, 100, 170])
    
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), C.primary_dark),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C.white),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C.white, C.bg_light]),
        ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    
    # Risk seviyesi renklendirme
    before_color = SEVERITY_COLORS.get(str(RL_b), C.danger_red)
    after_color  = SEVERITY_COLORS.get(str(RL_a), C.success_green)
    
    style_cmds.append(("BACKGROUND", (1, 4), (1, 4), before_color))
    style_cmds.append(("TEXTCOLOR",  (1, 4), (1, 4), C.white))
    style_cmds.append(("BACKGROUND", (2, 4), (2, 4), after_color))
    style_cmds.append(("TEXTCOLOR",  (2, 4), (2, 4), C.white))
    
    risk_tbl.setStyle(TableStyle(style_cmds))
    elements.append(risk_tbl)
    
    return elements

# ─────────────────────────────────────────────
# DÜZELTİCİ FAALİYETLER TABLOSU
# ─────────────────────────────────────────────
def build_corrective_actions_table(data):
    """Düzeltici faaliyetler tablosu oluştur."""
    elements = []
    
    h1 = ParagraphStyle(
        "H1CA", fontName="Helvetica-Bold", fontSize=14,
        textColor=C.primary_dark, spaceAfter=6, spaceBefore=15
    )
    label_s = ParagraphStyle(
        "LabelCA", fontName="Helvetica-Bold", fontSize=8,
        textColor=C.white
    )
    cell_s = ParagraphStyle(
        "CellCA", fontName="Helvetica", fontSize=8,
        textColor=C.text_dark, leading=11
    )
    cell_bold = ParagraphStyle(
        "CellBoldCA", fontName="Helvetica-Bold", fontSize=8,
        textColor=C.text_dark
    )
    center_s = ParagraphStyle(
        "CenterCA", fontName="Helvetica-Bold", fontSize=8,
        textColor=C.white, alignment=TA_CENTER
    )
    
    elements.append(Paragraph("DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER", h1))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=C.success_green, spaceAfter=10
    ))
    
    actions = data.get("corrective_actions", [])
    
    if not actions:
        # Boş durum mesajı
        no_action_style = ParagraphStyle(
            "NoAction",
            fontName="Helvetica-Oblique",
            fontSize=10,
            textColor=C.text_medium,
            alignment=TA_CENTER
        )
        placeholder_table = Table(
            [[Paragraph(
                "Düzeltici faaliyet planı hazirlanma asamasindadir.\n"
                "Kök neden analizi tamamlandiktan sonra güncellenecektir.",
                no_action_style
            )]],
            colWidths=[PAGE_WIDTH - 2 * MARGIN]
        )
        placeholder_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
            ("TOPPADDING",    (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
            ("LINEBEFORE",    (0, 0), (0, -1), 4, C.warning_yellow),
        ]))
        elements.append(placeholder_table)
        return elements
    
    # Başlık satırı
    headers = [
        Paragraph("ID",        label_s),
        Paragraph("FAALİYET",  label_s),
        Paragraph("SORUMLU",   label_s),
        Paragraph("TARİH",     label_s),
        Paragraph("ÖNCELİK",   label_s),
        Paragraph("DURUM",     label_s),
    ]
    
    rows = [headers]
    
    for action in actions:
        priority = action.get("priority", "MEDIUM")
        status   = action.get("status",   "PLANNED")
        
        row = [
            Paragraph(f'<b>{action.get("id", "")}</b>', cell_bold),
            Paragraph(clean_text(action.get("description", ""), max_len=80), cell_s),
            Paragraph(clean_text(action.get("responsible", ""), max_len=30), cell_s),
            Paragraph(action.get("due_date", ""), cell_s),
            Paragraph(priority, center_s),
            Paragraph(status,   center_s),
        ]
        rows.append(row)
    
    col_widths = [42, 195, 90, 68, 58, 75]
    ca_table = Table(rows, colWidths=col_widths, repeatRows=1)
    
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), C.primary_dark),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C.white, C.bg_light]),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    
    # Öncelik ve durum renkleri
    for i, action in enumerate(actions, 1):
        prio   = action.get("priority", "MEDIUM")
        status = action.get("status",   "PLANNED")
        p_color = SEVERITY_COLORS.get(prio,   C.warning_yellow)
        s_color = SEVERITY_COLORS.get(status, C.primary_light)
        style_cmds.append(("BACKGROUND", (4, i), (4, i), p_color))
        style_cmds.append(("BACKGROUND", (5, i), (5, i), s_color))
    
    ca_table.setStyle(TableStyle(style_cmds))
    elements.append(ca_table)
    
    return elements

# ─────────────────────────────────────────────
# KATKI SAĞLAYAN FAKTÖRLER
# ─────────────────────────────────────────────
def build_contributing_factors(data):
    """Katkıda bulunan faktörler bölümü."""
    elements = []
    
    factors = data.get("contributing_factors", [])
    if not factors:
        return elements
    
    h2 = ParagraphStyle(
        "H2CF", fontName="Helvetica-Bold", fontSize=12,
        textColor=C.primary_mid, spaceAfter=6, spaceBefore=12
    )
    body = ParagraphStyle(
        "BodyCF", fontName="Helvetica", fontSize=9,
        textColor=C.text_dark, leading=13
    )
    
    elements.append(Paragraph("KATKI SAĞLAYAN FAKTÖRLER", h2))
    elements.append(HRFlowable(
        width="100%", thickness=1,
        color=C.border_light, spaceAfter=8
    ))
    
    factor_rows = []
    for i, factor in enumerate(factors):
        f_clean = clean_text(str(factor), max_len=120)
        if f_clean:
            num_style = ParagraphStyle(
                f"Num{i}", fontName="Helvetica-Bold", fontSize=9,
                textColor=C.white, alignment=TA_CENTER
            )
            factor_rows.append([
                Paragraph(str(i + 1), num_style),
                Paragraph(f_clean, body),
            ])
    
    if factor_rows:
        f_table = Table(factor_rows, colWidths=[28, PAGE_WIDTH - 2 * MARGIN - 28])
        
        style_cmds = [
            ("BACKGROUND",    (0, 0), (0, -1), C.accent_orange),
            ("BACKGROUND",    (1, 0), (1, -1), C.bg_light),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (0, -1), 4),
            ("LEFTPADDING",   (1, 0), (1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
            ("ROWBACKGROUNDS",(1, 0), (1, -1), [C.bg_light, C.white]),
        ]
        f_table.setStyle(TableStyle(style_cmds))
        elements.append(f_table)
    
    return elements

# ─────────────────────────────────────────────
# ÇIKARILAN DERSLER & İMZA
# ─────────────────────────────────────────────
def build_lessons_and_signature(data):
    """Çıkarılan dersler ve imza alanları."""
    elements = []
    
    h1 = ParagraphStyle(
        "H1LL", fontName="Helvetica-Bold", fontSize=14,
        textColor=C.primary_dark, spaceAfter=6, spaceBefore=10
    )
    h2 = ParagraphStyle(
        "H2LL", fontName="Helvetica-Bold", fontSize=12,
        textColor=C.primary_mid, spaceAfter=6, spaceBefore=15
    )
    lessons_style = ParagraphStyle(
        "Lessons",
        fontName="Helvetica-Oblique",
        fontSize=10,
        textColor=C.primary_dark,
        leading=16,
        leftIndent=10,
        rightIndent=10
    )
    sig_style = ParagraphStyle(
        "Sig", fontName="Helvetica", fontSize=9,
        textColor=C.text_medium, alignment=TA_CENTER
    )
    sig_label = ParagraphStyle(
        "SigL", fontName="Helvetica-Bold", fontSize=9,
        textColor=C.text_dark, alignment=TA_CENTER
    )
    
    # ── Çıkarılan Dersler ──
    elements.append(Paragraph("ÇIKARILAN DERSLER", h1))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=C.primary_light, spaceAfter=10
    ))
    
    lessons = clean_text(
        safe_get(data, "lessons_learned", "Dersler belirleniyor..."),
        max_len=500
    )
    
    lessons_box = Table(
        [[Paragraph(lessons, lessons_style)]],
        colWidths=[PAGE_WIDTH - 2 * MARGIN]
    )
    lessons_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C.bg_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 15),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 15),
        ("LINEBEFORE",    (0, 0), (0, -1), 5, C.primary_mid),
    ]))
    elements.append(lessons_box)
    elements.append(Spacer(1, 20))
    
    # ── Benzer Olaylar & Maliyet ──
    similar = data.get("similar_incidents", 0)
    cost    = data.get("estimated_cost", 0)
    
    if similar or cost:
        info_style = ParagraphStyle(
            "InfoS", fontName="Helvetica", fontSize=9,
            textColor=C.text_dark
        )
        info_bold = ParagraphStyle(
            "InfoB", fontName="Helvetica-Bold", fontSize=10,
            textColor=C.primary_dark
        )
        
        stats_rows = []
        if similar:
            stats_rows.append([
                Paragraph("Benzer Olay Sayisi:", info_style),
                Paragraph(str(similar), info_bold),
            ])
        if cost:
            stats_rows.append([
                Paragraph("Tahmini Maliyet:", info_style),
                Paragraph(f"{cost:,} TL", info_bold),
            ])
        
        if stats_rows:
            stats_tbl = Table(stats_rows, colWidths=[200, 150])
            stats_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C.bg_gray),
                ("TOPPADDING",    (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("GRID",          (0, 0), (-1, -1), 0.5, C.border_light),
            ]))
            elements.append(stats_tbl)
            elements.append(Spacer(1, 20))
    
    # ── İmza Alanları ──
    elements.append(Paragraph("ONAY VE İMZALAR", h2))
    elements.append(HRFlowable(
        width="100%", thickness=1,
        color=C.border_light, spaceAfter=20
    ))
    
    sig_data = [
        [
            Paragraph("_________________________", sig_style),
            Paragraph("_________________________", sig_style),
            Paragraph("_________________________", sig_style),
        ],
        [
            Paragraph("HSE Yöneticisi", sig_label),
            Paragraph("Departman Müdürü", sig_label),
            Paragraph("İnceleme Sorumlusu", sig_label),
        ],
        [
            Paragraph("Tarih: ___/___/______", sig_style),
            Paragraph("Tarih: ___/___/______", sig_style),
            Paragraph("Tarih: ___/___/______", sig_style),
        ],
    ]
    
    col_w = (PAGE_WIDTH - 2 * MARGIN) / 3
    sig_table = Table(sig_data, colWidths=[col_w, col_w, col_w])
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 30))
    
    # ── Rapor Bilgileri ──
    footer_style = ParagraphStyle(
        "FooterInfo",
        fontName="Helvetica",
        fontSize=8,
        textColor=C.text_medium,
        alignment=TA_CENTER
    )
    
    inc_id   = safe_get(data, "incident_id",       "N/A")
    inv_by   = safe_get(data, "investigated_by",   "HSE Ekibi")
    inv_date = safe_get(data, "investigation_date", "")
    
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=C.border_light, spaceAfter=8
    ))
    elements.append(Paragraph(
        f"Rapor No: {inc_id}  |  Hazirlayan: {inv_by}  |  Tarih: {inv_date}  |  "
        "Bu rapor HSE Root Cause Analysis sistemi tarafindan otomatik olusturulmustur.",
        footer_style
    ))
    
    return elements

# ─────────────────────────────────────────────
# ÖZEL FLOWABLE: KPI + Risk Matrisi Canvas Sayfası
# ─────────────────────────────────────────────
from reportlab.platypus.flowables import Flowable

class KPIBoxesFlowable(Flowable):
    """KPI kutularını canvas üzerinde çizen özel Flowable."""
    
    def __init__(self, data, width, height=80):
        super().__init__()
        self.data   = data
        self.width  = width
        self.height = height
    
    def draw(self):
        draw_kpi_boxes(self.canv, self.data, 0, 0)
    
    def wrap(self, availWidth, availHeight):
        return self.width, self.height


class RiskMatrixFlowable(Flowable):
    """Risk matrisini canvas üzerinde çizen özel Flowable."""
    
    def __init__(self, data, width, height=320):
        super().__init__()
        self.data   = data
        self.width  = width
        self.height = height
    
    def draw(self):
        draw_risk_matrix(self.canv, self.data, 30, 80)
    
    def wrap(self, availWidth, availHeight):
        return self.width, self.height

# ─────────────────────────────────────────────
# ANA RAPOR ÜRETİM FONKSİYONU
# ─────────────────────────────────────────────
def generate_hse_rca_report(json_input, output_path):
    """
    Ana fonksiyon: JSON girdi → Profesyonel HSE PDF raporu
    
    Args:
        json_input: JSON string veya dict
        output_path: Çıktı PDF dosya yolu
    
    Returns:
        output_path: Oluşturulan PDF dosyasının yolu
    """
    print(f"[HSE RCA] Rapor üretimi başlatılıyor...")
    print(f"[HSE RCA] Çıktı: {output_path}")
    
    # ── JSON Parse ──
    if isinstance(json_input, str):
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse hatası: {e}")
    else:
        data = dict(json_input)
    
    # ── Doğrulama ──
    data = validate_rca_json(data)
    
    # ── Çıktı dizini oluştur ──
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        print(f"[HSE RCA] Dizin oluşturuldu: {out_dir}")
    
    # ── Header/Footer callback ──
    def on_page(canvas_obj, doc):
        add_page_header(canvas_obj, doc, data)
    
    # ── PDF Dökümanı ──
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=75,
        bottomMargin=45,
        title=f"HSE RCA Raporu - {data.get('incident_id', '')}",
        author=data.get("investigated_by", "HSE Ekibi"),
        subject="Root Cause Analysis Report",
        creator="HSE RCA Report Generator v2.0",
    )
    
    story = []
    
    # ════════════════════════════════════════════
    # SAYFA 1: KAPAK + OLAY AÇIKLAMASI
    # ════════════════════════════════════════════
    print("[HSE RCA] Sayfa 1: Kapak sayfası hazırlanıyor...")
    
    story.extend(build_cover_page(data))
    story.extend(build_incident_description(data))
    story.append(PageBreak())
    
    # ════════════════════════════════════════════
    # SAYFA 2: KPI KUTULARI + 5-WHY ZİNCİRİ
    # ════════════════════════════════════════════
    print("[HSE RCA] Sayfa 2: 5-Why zinciri hazırlanıyor...")
    
    # KPI Kutuları
    kpi_title = ParagraphStyle(
        "KPITitle", fontName="Helvetica-Bold", fontSize=13,
        textColor=C.primary_mid, spaceAfter=8
    )
    story.append(Paragraph("ÖZET GÖSTERGELERİ (KPI)", kpi_title))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=C.primary_mid, spaceAfter=8
    ))
    story.append(KPIBoxesFlowable(data, PAGE_WIDTH - 2 * MARGIN, height=85))
    story.append(Spacer(1, 15))
    
    # 5-Why Zinciri
    story.extend(build_five_why_section(data))
    story.append(PageBreak())
    
    # ════════════════════════════════════════════
    # SAYFA 3: RİSK MATRİSİ + DÜZELTİCİ FAALİYETLER
    # ════════════════════════════════════════════
    print("[HSE RCA] Sayfa 3: Risk matrisi ve düzeltici faaliyetler...")
    
    # Risk Tablosu (Flowable)
    story.extend(build_risk_table(data))
    story.append(Spacer(1, 15))
    
    # Risk Matrisi (Canvas)
    risk_title = ParagraphStyle(
        "RiskMatTitle", fontName="Helvetica-Bold", fontSize=12,
        textColor=C.primary_mid, spaceAfter=6, spaceBefore=10
    )
    story.append(Paragraph("RİSK MATRİSİ GÖRSELİ", risk_title))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=C.border_light, spaceAfter=8
    ))
    story.append(RiskMatrixFlowable(data, PAGE_WIDTH - 2 * MARGIN, height=310))
    story.append(Spacer(1, 15))
    
    # Düzeltici Faaliyetler
    story.extend(build_corrective_actions_table(data))
    
    # Katkıda Bulunan Faktörler
    story.extend(build_contributing_factors(data))
    story.append(PageBreak())
    
    # ════════════════════════════════════════════
    # SAYFA 4: ÇIKARILAN DERSLER + İMZA
    # ════════════════════════════════════════════
    print("[HSE RCA] Sayfa 4: Çıkarılan dersler ve imza alanları...")
    
    story.extend(build_lessons_and_signature(data))
    
    # ── PDF Oluştur ──
    print("[HSE RCA] PDF oluşturuluyor...")
    
    try:
        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
        file_size = os.path.getsize(output_path)
        print(f"[HSE RCA] ✅ Rapor başarıyla oluşturuldu!")
        print(f"[HSE RCA] 📄 Dosya: {output_path}")
        print(f"[HSE RCA] 📦 Boyut: {file_size / 1024:.1f} KB")
        return output_path
    except Exception as e:
        print(f"[HSE RCA] ❌ PDF oluşturma hatası: {e}")
        raise

# ─────────────────────────────────────────────
# RCA VERİSİ
# ─────────────────────────────────────────────
RCA_DATA = {
    "incident_id": "INC-2026-03-5771",
    "incident_title": "KAZA RAPORU - KİMYASAL YANMA (ASIT SIÇRAMASI)",
    "incident_date": "2026-03-12",
    "location": "ABC Kimya Fabrikasi, Asit Depolama Sahasi, Tank 7",
    "department": "HSE & Operations",
    "severity": "HIGH",
    "incident_type": "Kimyasal Yanma - Asit Sicramasi",
    "reported_by": "Sistem Operatoru",
    "investigated_by": "Agentic AI RCA Sistemi",
    "investigation_date": "2026-03-12",
    "analysis_method": "HSG245 5-Why Hierarchical Analysis",
    "description": (
        "OLAY OZETI\n"
        "Mehmet Yilmaz (34 yas, Kimya Teknisyeni, 8 yil kidem), "
        "%98 konsantrasyonlu sulfurik asit transferi sirasinda hortum baglantisinin "
        "gevshemesi sonucu yuzune ve gogusune asit sicramasi olmustur.\n"
        "ZAMAN CİZELGESİ\n"
        "08:00 - Vardiya baslangici, toolbox meeting (Konu: Elektrik guvenligi)\n"
        "09:00 - Tank 7'ye asit transferi icin hazirlik basladi\n"
        "09:30 - Pompa devreye alindi, ilk kontrol yapildi\n"
        "14:25 - Hortum titresimi fark edildi, operator kontrol icin yaklasti\n"
        "14:30 - Hortum baglantisi gevshedi, asit sicramasi oldu\n"
        "14:31 - Acil durum dusuna kostu, yikama basladi\n"
        "14:32 - Dus basinci yetersiz, operator bagrdi\n"
        "14:33 - Is arkadaslari yardima geldi, normal musluktan yikama yapildi\n"
        "14:35 - 112 arandi, ilk yardim malzemeleri getirildi\n"
        "14:50 - Ambulans geldi, hastaneye sevk\n"
        "BULGULAR\n"
        "Personel: Temel ISG egitimi alindi (2025 Ocak). "
        "Pratik acil durum tatbikati 2 yil once yapildi. "
        "Asit transfer proseduru pratik egitimi YOK.\n"
        "KKD: Kimyasal koruyucu gozluk, eldiven, onluk saglanmis. "
        "Gozluk CE belgeli ama asit sicramasina YETERSIZ (yan koruma yok). "
        "Yuz siperi YOK (risk degerlendirmesinde gerekli gorumus ama tedarik edilmemis).\n"
        "Ekipman: Acil durum dusu basinci test edilmemis (son test: 14 ay once). "
        "Hortum baglantisi orijinal parca degil, lokal imalat kullanilmis. "
        "Titresim sensoru ARIZALI (2 haftadir bakim bekliyor).\n"
        "Yonetim: Risk degerlendirmesi 18 ay once yapilmis. "
        "Is izin belgesi rutin olarak imzalaniyor (detayli kontrol YOK). "
        "Acil Durum Plani var ama PERSONEL BİLMİYOR.\n"
        "YARALANIM: 2. derece kimyasal yanik (yuz, boyun, gogus). "
        "Her iki gozde irritasyon. Tedavi suresi: 45 gun (tahmini). "
        "Kalici hasar riski: Var (cilt lekesi, goz problemleri)."
    ),
    "immediate_consequences": [
        "2. derece kimyasal yanik - yuz, boyun, gogus bolgesi",
        "Her iki gozde kimyasal irritasyon",
        "45 gun tahmini is gorsemezlik",
        "Kalici hasar riski (cilt lekesi, goz problemleri)",
        "Uretim durmasi - Tank 7 hatti devre disi",
        "Acil hastane sevki - 112 ambulans",
    ],
    "five_whys": [
        {
            "why": 1,
            "question": "Neden calisan yuzune ve gogusune asit sicramasi oldu?",
            "answer": "%98 konsantrasyonlu sulfurik asit transfer hortumunun baglantisi gevshedi ve asit sicramasi meydana geldi.",
            "evidence": "Olay yeri incelemesi, tanik ifadeleri (Ali Kaya: 'Hortum titriyordu'), fotografik belgeler",
            "confidence": "HIGH"
        },
        {
            "why": 2,
            "question": "Neden hortum baglantisi gevshedi?",
            "answer": "Hortum baglantisinda orijinal parca yerine lokal imalat parca kullanilmisti ve titresim sensoru arizali oldugu icin uyari verilmemisti.",
            "evidence": "Ekipman incelemesi: lokal imalat parca tespiti. SCADA kayitlari: sensor alarmi yok. Bakim kayitlari: sensor 2 haftadir arizali",
            "confidence": "HIGH"
        },
        {
            "why": 3,
            "question": "Neden lokal imalat parca kullanildi ve sensor arizi giderilmedi?",
            "answer": "Satin alma sureci maliyet odakli yonetilmekte, guvenlik kriterleri ikinci planda kalmaktadir. Bakim is emirleri onceliklendirilmemekte ve takip edilmemektedir.",
            "evidence": "Satin alma kayitlari: en dusuk fiyat kriteri. Bakim is emri #MNT-2026-089: 14 gunluk gecikme. Vardiya sefi ifadesi: 'zaman yok'",
            "confidence": "HIGH"
        },
        {
            "why": 4,
            "question": "Neden satin alma guvenlik kriterlerini gozardi ediyor ve bakim takibi yetersiz?",
            "answer": "Yonetim sistemi guvenlik performansini finansal performansla esit tutmamaktadir. Kritik ekipman tanimlama ve onceliklendirme proseduru eksiktir.",
            "evidence": "Risk degerlendirmesi: 18 ay guncellenmemis. Is izin sistemi: rutin imza uygulamasi. Acil durum plani: personel bilmiyor",
            "confidence": "MEDIUM"
        },
        {
            "why": 5,
            "question": "Neden yonetim sistemi guvenlik onceliklerini etkin sekilde yonetemiyor?",
            "answer": "Ust yonetim taahhudunde guvenlik kulturu tam oturmamis; prosedurler kagit uzerinde var ancak sahada uygulanmiyor. Hesap verebilirlik mekanizmalari yetersiz.",
            "evidence": "Acil durum dusu son test: 14 ay once (standart: 3 ayda bir). Yuz siperi talep tarihi: 3 ay once, hala temin edilmemis. Tatbikat: 2 yil once",
            "confidence": "MEDIUM"
        },
    ],
    "root_cause": (
        "Ust yonetim taahhudundeki guvenlik kulturu eksikligi nedeniyle; "
        "prosedurler kagit uzerinde kalmakta, kritik ekipman bakimi ihmal edilmekte, "
        "KKD temini geciktirilmekte ve acil durum sistemleri test edilmemektedir. "
        "Bu sistemsel baskari, sahada birden fazla guvenlik bariyerinin ayni anda "
        "devre disi kalmasina yol acmistir."
    ),
    "contributing_factors": [
        "Acil durum dusu 14 aydir test edilmemis (standart: 3 ayda bir)",
        "Yuz siperi talep 3 ay once yapilmis, hala temin edilmemis (butce bekleniyor)",
        "Titresim sensoru 2 haftadir arizali, bakim is emri beklemede",
        "Hortum baglantisinda lokal imalat parca kullanilmis (maliyet tasarrufu)",
        "Pratik acil durum tatbikati 2 yildir yapilmamis",
        "Risk degerlendirmesi 18 aydir guncellenmemis",
        "Is izin sistemi rutin imza uygulamasina donusmus (detayli kontrol yok)",
        "Toolbox meeting konusu asit transferiyle ilgisiz (elektrik guvenligi)",
        "Asit transfer proseduru pratik egitimi hic verilmemis",
    ],
    "corrective_actions": [
        {
            "id": "CA-01",
            "description": "Tum acil durum duslarinin ve goz yikama istasyonlarinin derhal test edilmesi ve bakim yapilmasi",
            "responsible": "Tesis Bakım Müdürü",
            "due_date": "2026-03-15",
            "priority": "CRITICAL",
            "status": "IN_PROGRESS"
        },
        {
            "id": "CA-02",
            "description": "Yuz siperi ve uygun KKD'nin acil temin edilmesi (butce onayı beklenmeksizin)",
            "responsible": "HSE Müdürü",
            "due_date": "2026-03-17",
            "priority": "CRITICAL",
            "status": "IN_PROGRESS"
        },
        {
            "id": "CA-03",
            "description": "Titresim sensoru tamiri ve tum kritik sensörlerin kontrolü",
            "responsible": "Elektrik/Enstrüman Bakım",
            "due_date": "2026-03-16",
            "priority": "CRITICAL",
            "status": "PLANNED"
        },
        {
            "id": "CA-04",
            "description": "Asit transfer hattinda tum lokal imalat parcalarin orijinal ile degistirilmesi",
            "responsible": "Mekanik Bakım Ekibi",
            "due_date": "2026-03-20",
            "priority": "HIGH",
            "status": "PLANNED"
        },
        {
            "id": "CA-05",
            "description": "Tum kimyasal transfer personeline pratik acil durum tatbikati ve KKD kullanim egitimi",
            "responsible": "HSE & İK",
            "due_date": "2026-03-25",
            "priority": "HIGH",
            "status": "PLANNED"
        },
        {
            "id": "CA-06",
            "description": "Risk degerlendirmesinin guncellenmesi ve is izin sisteminin revize edilmesi",
            "responsible": "HSE Uzmanı",
            "due_date": "2026-04-01",
            "priority": "HIGH",
            "status": "PLANNED"
        },
        {
            "id": "CA-07",
            "description": "Satin alma prosedurune guvenlik kriterleri eklenmesi (kritik ekipman icin zorunlu onay)",
            "responsible": "Satin Alma & HSE",
            "due_date": "2026-04-15",
            "priority": "MEDIUM",
            "status": "PLANNED"
        },
        {
            "id": "CA-08",
            "description": "Ust yonetim guvenlik kulturu egitimi ve hesap verebilirlik mekanizmalarinin kurulmasi",
            "responsible": "Genel Müdür & HSE",
            "due_date": "2026-04-30",
            "priority": "MEDIUM",
            "status": "PLANNED"
        },
    ],
    "risk_assessment": {
        "likelihood_before": 4,
        "severity_before": 5,
        "risk_score_before": 20,
        "risk_level_before": "CRITICAL",
        "likelihood_after": 2,
        "severity_after": 4,
        "risk_score_after": 8,
        "risk_level_after": "MEDIUM"
    },
    "lessons_learned": (
        "1. Guvenlik kulturu ust yonetimden baslar: Prosedurler kagit uzerinde kalmamali, "
        "sahada uygulanmali ve denetlenmelidir.\n"
        "2. Kritik guvenlik ekipmanlari (acil dus, goz yikama, sensorler) periyodik test "
        "programina alinmali ve takip edilmelidir.\n"
        "3. KKD temini guvenlik onceligi olarak ele alinmali, butce gerekceleriyle "
        "ertelenmemelidir.\n"
        "4. Is izin sistemleri rutin imzaya donusmemeli, her is icin gercek risk "
        "degerlendirmesi yapilmalidir.\n"
        "5. Pratik tatbikatlar teorik egitimden daha etkilidir; acil durum prosedurlerinin "
        "sahada uygulanmasi saglanmalidir."
    ),
    "similar_incidents": 2,
    "estimated_cost": 185000,
    "total_branches": 5,
    "total_root_causes": 3,
}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Çıktı yolu
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "outputs/reports/chemical_burn_report_20260312_014635.pdf"
    
    # JSON dosyasından okuma desteği
    if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
        with open(sys.argv[2], encoding="utf-8") as f:
            rca_data = json.load(f)
    else:
        rca_data = RCA_DATA
    
    try:
        result = generate_hse_rca_report(rca_data, output_file)
        print(f"\n{'='*60}")
        print(f"  HSE RCA RAPORU BASARIYLA OLUSTURULDU")
        print(f"{'='*60}")
        print(f"  Dosya : {result}")
        print(f"  Boyut : {os.path.getsize(result) / 1024:.1f} KB")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n[HATA] Rapor olusturulamadi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
