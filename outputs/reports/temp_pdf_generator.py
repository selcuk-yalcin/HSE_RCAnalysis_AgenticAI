#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSE Root Cause Analysis PDF Report Generator
SKILL.md tabanlı profesyonel rapor üretim sistemi
"""

import json
import os
import sys
from datetime import datetime
from functools import partial

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF

# ═══════════════════════════════════════════════════════════════════
# SAYFA BOYUTLARI VE MARGIN
# ═══════════════════════════════════════════════════════════════════
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40

# ═══════════════════════════════════════════════════════════════════
# HSE KURUMSAL RENK PALETİ
# ═══════════════════════════════════════════════════════════════════
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

HSE = HSEColors()

# Severity / Status renk eşleşmesi
SEVERITY_COLORS = {
    "CRITICAL":    HSE.danger_red,
    "HIGH":        HSE.accent_orange,
    "MEDIUM":      HSE.medium_orange,
    "LOW":         HSE.success_green,
    "IN_PROGRESS": HSE.warning_yellow,
    "COMPLETED":   HSE.success_green,
    "PLANNED":     HSE.primary_light,
}

CONFIDENCE_COLORS = {
    "HIGH":   HSE.success_green,
    "MEDIUM": HSE.warning_yellow,
    "LOW":    HSE.danger_red,
}

# Risk matrisi renkleri (5x5)
MATRIX_COLORS = [
    [colors.HexColor("#E74C3C"), colors.HexColor("#E74C3C"), colors.HexColor("#E67E22"),
     colors.HexColor("#E67E22"), colors.HexColor("#E67E22")],
    [colors.HexColor("#E74C3C"), colors.HexColor("#E74C3C"), colors.HexColor("#E67E22"),
     colors.HexColor("#F39C12"), colors.HexColor("#F39C12")],
    [colors.HexColor("#E67E22"), colors.HexColor("#E67E22"), colors.HexColor("#F39C12"),
     colors.HexColor("#F39C12"), colors.HexColor("#2ECC71")],
    [colors.HexColor("#E67E22"), colors.HexColor("#F39C12"), colors.HexColor("#F39C12"),
     colors.HexColor("#2ECC71"), colors.HexColor("#2ECC71")],
    [colors.HexColor("#F39C12"), colors.HexColor("#F39C12"), colors.HexColor("#2ECC71"),
     colors.HexColor("#2ECC71"), colors.HexColor("#2ECC71")],
]


# ═══════════════════════════════════════════════════════════════════
# ADIM 1 — JSON DOĞRULAMA
# ═══════════════════════════════════════════════════════════════════
def validate_rca_json(data: dict) -> bool:
    """Gelen JSON'u doğrula ve eksik alanları kontrol et."""
    required_fields = ["incident_title", "five_whys", "root_cause", "corrective_actions"]
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
                data[field] = "Bilgi Mevcut Değil"

    why_count = len(data.get("five_whys", []))
    if why_count < 3:
        print(f"UYARI: {why_count} Why zinciri — ideal minimum 3 olmalı")
    elif why_count > 7:
        print(f"UYARI: {why_count} Why zinciri — ideal maksimum 7 olmalı")
    else:
        print(f"✓ {why_count} Why zinciri doğrulandı")

    # Risk skoru tutarlılık kontrolü
    risk = data.get("risk_assessment", {})
    if risk:
        calc_before = risk.get("likelihood_before", 0) * risk.get("severity_before", 0)
        calc_after  = risk.get("likelihood_after", 0)  * risk.get("severity_after", 0)
        if calc_before != risk.get("risk_score_before", calc_before):
            print(f"UYARI: Risk skoru (önce) tutarsız. Hesaplanan: {calc_before}")
            data["risk_assessment"]["risk_score_before"] = calc_before
        if calc_after != risk.get("risk_score_after", calc_after):
            print(f"UYARI: Risk skoru (sonra) tutarsız. Hesaplanan: {calc_after}")
            data["risk_assessment"]["risk_score_after"] = calc_after

    return True


# ═══════════════════════════════════════════════════════════════════
# ADIM 3 — HEADER / FOOTER
# ═══════════════════════════════════════════════════════════════════
def add_page_header(canvas_obj, doc, data: dict):
    """Her sayfaya kurumsal header ve footer ekle."""
    canvas_obj.saveState()

    # ── Üst header bar (lacivert) ──────────────────────────────────
    canvas_obj.setFillColor(HSE.primary_dark)
    canvas_obj.rect(0, PAGE_HEIGHT - 58, PAGE_WIDTH, 58, fill=1, stroke=0)

    # Turuncu alt şerit
    canvas_obj.setFillColor(HSE.accent_orange)
    canvas_obj.rect(0, PAGE_HEIGHT - 61, PAGE_WIDTH, 3, fill=1, stroke=0)

    # Sol: HSE logosu ve başlık
    canvas_obj.setFillColor(HSE.accent_orange)
    canvas_obj.roundRect(MARGIN, PAGE_HEIGHT - 48, 36, 28, 4, fill=1, stroke=0)
    canvas_obj.setFillColor(HSE.white)
    canvas_obj.setFont("Helvetica-Bold", 13)
    canvas_obj.drawCentredString(MARGIN + 18, PAGE_HEIGHT - 37, "HSE")

    canvas_obj.setFillColor(HSE.white)
    canvas_obj.setFont("Helvetica-Bold", 12)
    canvas_obj.drawString(MARGIN + 44, PAGE_HEIGHT - 30, "Root Cause Analysis Report")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(HSE.primary_light)
    canvas_obj.drawString(MARGIN + 44, PAGE_HEIGHT - 44, "HSG245 5-Why Hierarchical Analysis")

    # Sağ: Olay ID ve tarih
    canvas_obj.setFillColor(HSE.white)
    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 28,
                               f"#{data.get('incident_id', 'N/A')}")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(HSE.primary_light)
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 42,
                               data.get("incident_date", ""))

    # ── Alt footer ─────────────────────────────────────────────────
    canvas_obj.setFillColor(HSE.bg_gray)
    canvas_obj.rect(0, 0, PAGE_WIDTH, 28, fill=1, stroke=0)
    canvas_obj.setFillColor(HSE.accent_orange)
    canvas_obj.rect(0, 27, PAGE_WIDTH, 1.5, fill=1, stroke=0)

    canvas_obj.setFillColor(HSE.text_medium)
    canvas_obj.setFont("Helvetica-Oblique", 7)
    canvas_obj.drawString(MARGIN, 10, "GIZLI — Yalnizca Ic Kullanim Icin | HSE Root Cause Analysis")
    canvas_obj.setFont("Helvetica-Bold", 7)
    canvas_obj.drawRightString(PAGE_WIDTH - MARGIN, 10,
                               f"Sayfa {doc.page} | {data.get('department', 'HSE')}")

    canvas_obj.restoreState()


# ═══════════════════════════════════════════════════════════════════
# ADIM 4 — KAPAK SAYFASI
# ═══════════════════════════════════════════════════════════════════
def build_cover_page(data: dict) -> list:
    """Profesyonel kapak sayfası elemanları."""
    elements = []

    # ── Ana başlık kutusu ──────────────────────────────────────────
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=HSE.white,
        alignment=TA_CENTER,
        leading=32,
        spaceAfter=6
    )
    cover_sub_style = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica",
        fontSize=13,
        textColor=HSE.primary_light,
        alignment=TA_CENTER,
        leading=18
    )
    cover_method_style = ParagraphStyle(
        "CoverMethod",
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=HSE.accent_amber,
        alignment=TA_CENTER,
        leading=14
    )

    cover_data = [
        [Paragraph("ROOT CAUSE ANALYSIS", cover_title_style)],
        [Paragraph("HSE Inceleme Raporu", cover_sub_style)],
        [Spacer(1, 6)],
        [Paragraph(
            f"Metot: {data.get('analysis_method', 'HSG245 5-Why Hierarchical Analysis')}",
            cover_method_style
        )],
    ]
    cover_table = Table(cover_data, colWidths=[PAGE_WIDTH - 2 * MARGIN])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HSE.primary_dark),
        ("TOPPADDING",    (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 30),
        ("LEFTPADDING",   (0, 0), (-1, -1), 30),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
        ("LINEBELOW", (0, 0), (-1, 0), 2, HSE.accent_orange),
    ]))
    elements.append(Spacer(1, 15))
    elements.append(cover_table)
    elements.append(Spacer(1, 15))

    # ── Severity badge ─────────────────────────────────────────────
    sev = data.get("severity", "MEDIUM")
    sev_color = SEVERITY_COLORS.get(sev, HSE.accent_orange)
    badge_style = ParagraphStyle(
        "Badge",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=HSE.white,
        alignment=TA_CENTER
    )
    badge_table = Table(
        [[Paragraph(f"SEVERITY: {sev}", badge_style)]],
        colWidths=[180]
    )
    badge_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), sev_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))

    # Badge'i ortala
    badge_wrapper = Table([[badge_table]], colWidths=[PAGE_WIDTH - 2 * MARGIN])
    badge_wrapper.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(badge_wrapper)
    elements.append(Spacer(1, 20))

    # ── Olay bilgileri tablosu ─────────────────────────────────────
    info_label_style = ParagraphStyle(
        "InfoLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=HSE.text_medium
    )
    info_value_style = ParagraphStyle(
        "InfoValue",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=HSE.text_dark
    )

    def lbl(text):
        return Paragraph(text.upper(), info_label_style)

    def val(text):
        return Paragraph(str(text) if text else "—", info_value_style)

    info_rows = [
        [lbl("Olay Basligi"),  val(data.get("incident_title", "")),
         lbl("Olay Tarihi"),   val(data.get("incident_date", ""))],
        [lbl("Lokasyon"),      val(data.get("location", "")),
         lbl("Departman"),     val(data.get("department", ""))],
        [lbl("Olay Tipi"),     val(data.get("incident_type", "")),
         lbl("Olay ID"),       val(data.get("incident_id", ""))],
        [lbl("Raporlayan"),    val(data.get("reported_by", "")),
         lbl("Inceleyen"),     val(data.get("investigated_by", ""))],
        [lbl("Inceleme Tar."), val(data.get("investigation_date", "")),
         lbl("Benzer Olay"),   val(str(data.get("similar_incidents", 0)))],
    ]

    col_w = [110, 155, 110, 155]
    info_table = Table(info_rows, colWidths=col_w)
    info_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), HSE.bg_gray),
        ("BACKGROUND",    (2, 0), (2, -1), HSE.bg_gray),
        ("BACKGROUND",    (1, 0), (1, -1), HSE.bg_light),
        ("BACKGROUND",    (3, 0), (3, -1), HSE.bg_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.5, HSE.border_light),
        ("LINEABOVE",     (0, 0), (-1, 0), 2, HSE.primary_mid),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 18))

    # ── Olay açıklaması ────────────────────────────────────────────
    desc_title_style = ParagraphStyle(
        "DescTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=HSE.primary_dark,
        spaceAfter=4
    )
    desc_body_style = ParagraphStyle(
        "DescBody",
        fontName="Helvetica",
        fontSize=10,
        textColor=HSE.text_dark,
        leading=15
    )
    elements.append(Paragraph("OLAY ACIKLAMASI", desc_title_style))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.accent_orange, spaceAfter=8
    ))
    elements.append(Paragraph(data.get("description", "Aciklama mevcut degil."), desc_body_style))
    elements.append(Spacer(1, 12))

    # ── Anlık etkiler ──────────────────────────────────────────────
    consequences = data.get("immediate_consequences", [])
    if consequences:
        elements.append(Paragraph("ANLIK ETKİLER", desc_title_style))
        cons_rows = []
        for c in consequences:
            cons_rows.append([Paragraph(f"• {c}", desc_body_style)])

        cons_table = Table(cons_rows, colWidths=[PAGE_WIDTH - 2 * MARGIN])
        cons_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), HSE.bg_light),
            ("LEFTPADDING",   (0, 0), (-1, -1), 16),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBEFORE",    (0, 0), (0, -1), 4, HSE.accent_orange),
            ("LINEBELOW",     (0, -1), (-1, -1), 0.5, HSE.border_light),
        ]))
        elements.append(cons_table)

    return elements


# ═══════════════════════════════════════════════════════════════════
# ADIM 5 — 5 WHY ZİNCİRİ (Tablo Formatında)
# ═══════════════════════════════════════════════════════════════════
def build_five_why_section(data: dict) -> list:
    """5 Why zincirini görsel tablo formatında oluştur."""
    elements = []

    h1_style = ParagraphStyle(
        "H1", fontName="Helvetica-Bold", fontSize=16,
        textColor=HSE.primary_dark, spaceAfter=8, spaceBefore=10
    )
    elements.append(Paragraph("5 WHY ANALİZ ZİNCİRİ", h1_style))
    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.primary_mid, spaceAfter=12
    ))

    five_whys = data.get("five_whys", [])
    total = len(five_whys)

    for idx, why in enumerate(five_whys):
        why_num  = why.get("why", idx + 1)
        question = why.get("question", "Soru belirtilmedi")
        answer   = why.get("answer",   "Cevap belirtilmedi")
        evidence = why.get("evidence", "")
        conf     = why.get("confidence", "MEDIUM")
        conf_color = CONFIDENCE_COLORS.get(conf, HSE.warning_yellow)

        # Soru satırı
        q_num_style = ParagraphStyle(
            "QNum", fontName="Helvetica-Bold", fontSize=10,
            textColor=HSE.white
        )
        q_text_style = ParagraphStyle(
            "QText", fontName="Helvetica-Bold", fontSize=10,
            textColor=HSE.white, leading=14
        )
        conf_style = ParagraphStyle(
            "Conf", fontName="Helvetica-Bold", fontSize=8,
            textColor=HSE.white, alignment=TA_CENTER
        )

        # Cevap satırı
        a_label_style = ParagraphStyle(
            "ALabel", fontName="Helvetica-Bold", fontSize=9,
            textColor=HSE.primary_mid
        )
        a_text_style = ParagraphStyle(
            "AText", fontName="Helvetica", fontSize=10,
            textColor=HSE.text_dark, leading=14
        )
        ev_style = ParagraphStyle(
            "Ev", fontName="Helvetica-Oblique", fontSize=8,
            textColor=HSE.text_medium, leading=12
        )

        # Why numarası dairesi (tablo hücresi olarak)
        num_cell = Paragraph(f"<b>{why_num}</b>", ParagraphStyle(
            "Num", fontName="Helvetica-Bold", fontSize=14,
            textColor=HSE.white, alignment=TA_CENTER
        ))

        q_cell   = Paragraph(question, q_text_style)
        conf_cell = Paragraph(conf, conf_style)

        # Soru satırı tablosu
        q_row_data = [[num_cell, q_cell, conf_cell]]
        q_row_table = Table(q_row_data, colWidths=[32, PAGE_WIDTH - 2*MARGIN - 32 - 65, 60])
        q_row_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), HSE.primary_mid),
            ("BACKGROUND",    (1, 0), (1, 0), HSE.primary_dark),
            ("BACKGROUND",    (2, 0), (2, 0), conf_color),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (0, 0), (0, 0), "CENTER"),
            ("ALIGN",         (2, 0), (2, 0), "CENTER"),
        ]))

        # Cevap satırı
        a_content = [
            Paragraph("<b>CEVAP:</b>", a_label_style),
            Paragraph(answer, a_text_style),
        ]
        if evidence:
            a_content.append(Paragraph(f"Kanit: {evidence}", ev_style))

        a_cell_inner = Table(
            [[p] for p in a_content],
            colWidths=[PAGE_WIDTH - 2*MARGIN - 32]
        )
        a_cell_inner.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))

        a_row_data = [["", a_cell_inner]]
        a_row_table = Table(a_row_data, colWidths=[32, PAGE_WIDTH - 2*MARGIN - 32])
        a_row_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), HSE.primary_mid),
            ("BACKGROUND",    (1, 0), (1, 0), HSE.bg_light),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.5, HSE.border_light),
        ]))

        elements.append(KeepTogether([q_row_table, a_row_table]))

        # Ok (son eleman hariç)
        if idx < total - 1:
            arrow_style = ParagraphStyle(
                "Arrow", fontName="Helvetica-Bold", fontSize=18,
                textColor=HSE.accent_orange, alignment=TA_CENTER
            )
            arrow_table = Table(
                [[Paragraph("v", arrow_style)]],
                colWidths=[PAGE_WIDTH - 2*MARGIN]
            )
            arrow_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), HSE.white),
                ("TOPPADDING",    (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            elements.append(arrow_table)
        else:
            elements.append(Spacer(1, 10))

    # ── Kök Neden Kutusu ───────────────────────────────────────────
    root_style = ParagraphStyle(
        "Root", fontName="Helvetica-Bold", fontSize=12,
        textColor=HSE.white, alignment=TA_CENTER, leading=16
    )
    root_label_style = ParagraphStyle(
        "RootLabel", fontName="Helvetica-Bold", fontSize=9,
        textColor=HSE.accent_amber, alignment=TA_CENTER
    )

    root_content = [
        [Paragraph("KOK NEDEN", root_label_style)],
        [Paragraph(data.get("root_cause", "Belirleniyor..."), root_style)],
    ]
    root_table = Table(root_content, colWidths=[PAGE_WIDTH - 2*MARGIN])
    root_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HSE.danger_red),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("LINEABOVE",     (0, 0), (-1, 0), 3, HSE.accent_amber),
    ]))
    elements.append(root_table)

    return elements


# ═══════════════════════════════════════════════════════════════════
# ADIM 6 — RİSK MATRİSİ (5x5 Görsel — Canvas Flowable)
# ═══════════════════════════════════════════════════════════════════
from reportlab.platypus import Flowable

class RiskMatrixFlowable(Flowable):
    """5x5 Risk Matrisi — öncesi ve sonrası risk noktaları ile."""

    def __init__(self, risk_data: dict, width=None, height=None):
        super().__init__()
        self.risk_data = risk_data
        self.CELL_SIZE = 38
        self.MATRIX_SIZE = 5
        total_matrix = self.CELL_SIZE * self.MATRIX_SIZE
        self.width  = width  or (total_matrix + 80)
        self.height = height or (total_matrix + 80)

    def draw(self):
        c = self.canv
        risk = self.risk_data
        CS = self.CELL_SIZE
        MS = self.MATRIX_SIZE

        x_offset = 50
        y_offset = 40

        # Eksen başlıkları
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HSE.text_dark)
        c.drawCentredString(x_offset + MS * CS / 2, y_offset - 25,
                            "OLASILIK (Likelihood) ->")

        # Y ekseni (dikey metin)
        c.saveState()
        c.translate(x_offset - 35, y_offset + MS * CS / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, "<- SIDDET (Severity)")
        c.restoreState()

        # Eksen numaraları
        c.setFont("Helvetica", 7)
        c.setFillColor(HSE.text_medium)
        for i in range(MS):
            # X ekseni (olasılık)
            c.drawCentredString(x_offset + i * CS + CS / 2, y_offset - 12, str(i + 1))
            # Y ekseni (şiddet)
            c.drawRightString(x_offset - 5, y_offset + i * CS + CS / 2 - 3, str(i + 1))

        # Matris hücreleri
        for row in range(MS):
            for col in range(MS):
                x = x_offset + col * CS
                y = y_offset + row * CS
                cell_color = MATRIX_COLORS[4 - row][col]
                c.setFillColor(cell_color)
                c.setStrokeColor(HSE.white)
                c.setLineWidth(1.5)
                c.rect(x, y, CS, CS, fill=1, stroke=1)

                # Skor
                score = (col + 1) * (row + 1)
                c.setFillColor(HSE.white)
                c.setFont("Helvetica-Bold", 9)
                c.drawCentredString(x + CS / 2, y + CS / 2 - 3, str(score))

        # ── Öncesi risk noktası (koyu daire - "O") ─────────────────
        L_before = min(max(risk.get("likelihood_before", 4) - 1, 0), 4)
        S_before = min(max(risk.get("severity_before",   5) - 1, 0), 4)
        bx = x_offset + L_before * CS + CS / 2
        by = y_offset + S_before * CS + CS / 2

        c.setFillColor(HSE.primary_dark)
        c.setStrokeColor(HSE.white)
        c.setLineWidth(1.5)
        c.circle(bx, by, 11, fill=1, stroke=1)
        c.setFillColor(HSE.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(bx, by - 3, "ONCE")

        # ── Sonrası risk noktası (yeşil daire - "S") ───────────────
        L_after = min(max(risk.get("likelihood_after", 2) - 1, 0), 4)
        S_after = min(max(risk.get("severity_after",   4) - 1, 0), 4)
        ax = x_offset + L_after * CS + CS / 2
        ay = y_offset + S_after * CS + CS / 2

        c.setFillColor(HSE.success_green)
        c.setStrokeColor(HSE.white)
        c.setLineWidth(1.5)
        c.circle(ax, ay, 11, fill=1, stroke=1)
        c.setFillColor(HSE.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(ax, ay - 3, "SONRA")

        # ── Lejant ─────────────────────────────────────────────────
        legend_x = x_offset + MS * CS + 15
        legend_y = y_offset + MS * CS - 20

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HSE.text_dark)
        c.drawString(legend_x, legend_y, "LEJANT:")

        legend_items = [
            (HSE.danger_red,     "Kritik Risk"),
            (HSE.medium_orange,  "Yuksek Risk"),
            (HSE.warning_yellow, "Orta Risk"),
            (HSE.success_green,  "Dusuk Risk"),
        ]
        for i, (col_item, label) in enumerate(legend_items):
            ly = legend_y - 20 - i * 18
            c.setFillColor(col_item)
            c.rect(legend_x, ly, 12, 12, fill=1, stroke=0)
            c.setFillColor(HSE.text_dark)
            c.setFont("Helvetica", 7)
            c.drawString(legend_x + 16, ly + 2, label)


# ═══════════════════════════════════════════════════════════════════
# ADIM 8 — KPI ÖZET KUTULARI (Canvas Flowable)
# ═══════════════════════════════════════════════════════════════════
class KPISummaryFlowable(Flowable):
    """4 adet KPI özet kutusu."""

    def __init__(self, data: dict, width=None):
        super().__init__()
        self.data = data
        self.width  = width or (PAGE_WIDTH - 2 * MARGIN)
        self.height = 90

    def draw(self):
        c = self.canv
        data = self.data
        risk    = data.get("risk_assessment", {})
        actions = data.get("corrective_actions", [])
        completed = sum(1 for a in actions if a.get("status") == "COMPLETED")

        kpis = [
            {
                "label": "5 WHY SAYISI",
                "value": str(len(data.get("five_whys", []))),
                "sub":   "Analiz Adimi",
                "color": HSE.primary_mid,
            },
            {
                "label": "RISK (ONCE)",
                "value": str(risk.get("risk_score_before", "N/A")),
                "sub":   risk.get("risk_level_before", ""),
                "color": HSE.danger_red,
            },
            {
                "label": "RISK (SONRA)",
                "value": str(risk.get("risk_score_after", "N/A")),
                "sub":   risk.get("risk_level_after", ""),
                "color": HSE.success_green,
            },
            {
                "label": "DUZELTICI FAALIYET",
                "value": str(len(actions)),
                "sub":   f"{completed} Tamamlandi",
                "color": HSE.accent_orange,
            },
        ]

        BOX_W = (self.width - 30) / 4
        BOX_H = 80
        GAP   = 10

        for i, kpi in enumerate(kpis):
            bx = i * (BOX_W + GAP)
            by = 0

            # Arka plan (beyaz)
            c.setFillColor(HSE.white)
            c.setStrokeColor(HSE.border_light)
            c.setLineWidth(0.5)
            c.roundRect(bx, by, BOX_W, BOX_H, 6, fill=1, stroke=1)

            # Üst renkli şerit
            c.setFillColor(kpi["color"])
            c.roundRect(bx, by + BOX_H - 22, BOX_W, 22, 6, fill=1, stroke=0)
            c.rect(bx, by + BOX_H - 22, BOX_W, 11, fill=1, stroke=0)

            # Etiket
            c.setFillColor(HSE.white)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(bx + BOX_W / 2, by + BOX_H - 13, kpi["label"])

            # Değer (büyük)
            c.setFillColor(kpi["color"])
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(bx + BOX_W / 2, by + 30, kpi["value"])

            # Alt metin
            c.setFillColor(HSE.text_medium)
            c.setFont("Helvetica", 8)
            c.drawCentredString(bx + BOX_W / 2, by + 10, kpi["sub"])


# ═══════════════════════════════════════════════════════════════════
# ADIM 7 — DÜZELTİCİ FAALİYETLER TABLOSU
# ═══════════════════════════════════════════════════════════════════
def build_corrective_actions_table(data: dict):
    """Düzeltici faaliyetler için renkli, öncelikli tablo."""

    label_style = ParagraphStyle(
        "CALabel", fontName="Helvetica-Bold", fontSize=9,
        textColor=HSE.white
    )
    cell_style = ParagraphStyle(
        "CACell", fontName="Helvetica", fontSize=9,
        textColor=HSE.text_dark, leading=13
    )
    badge_style = ParagraphStyle(
        "CABadge", fontName="Helvetica-Bold", fontSize=8,
        textColor=HSE.white, alignment=TA_CENTER
    )

    headers = [
        Paragraph("ID",        label_style),
        Paragraph("FAALİYET",  label_style),
        Paragraph("SORUMLU",   label_style),
        Paragraph("TARİH",     label_style),
        Paragraph("ÖNCELİK",   label_style),
        Paragraph("DURUM",     label_style),
    ]

    rows = [headers]
    actions = data.get("corrective_actions", [])

    if not actions:
        # Boş durum satırı
        empty_style = ParagraphStyle(
            "Empty", fontName="Helvetica-Oblique", fontSize=9,
            textColor=HSE.text_medium, alignment=TA_CENTER
        )
        rows.append([
            Paragraph("—", cell_style),
            Paragraph("Henuz tanimlanmamis faaliyet", empty_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
            Paragraph("—", cell_style),
        ])
    else:
        for action in actions:
            priority = action.get("priority", "MEDIUM")
            status   = action.get("status",   "PLANNED")

            rows.append([
                Paragraph(f"<b>{action.get('id', '')}</b>", cell_style),
                Paragraph(action.get("description", ""), cell_style),
                Paragraph(action.get("responsible", ""), cell_style),
                Paragraph(action.get("due_date", ""), cell_style),
                Paragraph(f"<b>{priority}</b>", badge_style),
                Paragraph(f"<b>{status}</b>",   badge_style),
            ])

    col_widths = [42, 190, 90, 68, 58, 82]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), HSE.primary_dark),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, HSE.border_light),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HSE.white, HSE.bg_light]),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (4, 0), (5, -1), "CENTER"),
    ]

    for i, action in enumerate(actions, 1):
        prio   = action.get("priority", "MEDIUM")
        status = action.get("status",   "PLANNED")
        prio_color   = SEVERITY_COLORS.get(prio,   HSE.warning_yellow)
        status_color = SEVERITY_COLORS.get(status, HSE.primary_light)
        style_cmds.append(("BACKGROUND", (4, i), (4, i), prio_color))
        style_cmds.append(("BACKGROUND", (5, i), (5, i), status_color))
        style_cmds.append(("TEXTCOLOR",  (4, i), (5, i), HSE.white))

    table.setStyle(TableStyle(style_cmds))
    return table


# ═══════════════════════════════════════════════════════════════════
# ADIM 9 — TAM RAPOR ÜRETİM FONKSİYONU
# ═══════════════════════════════════════════════════════════════════
def generate_hse_rca_report(json_input, output_path: str) -> str:
    """
    Ana fonksiyon: JSON girdi → Profesyonel HSE PDF raporu.
    """
    # JSON parse
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = dict(json_input)

    # Doğrulama
    print("JSON doğrulanıyor...")
    validate_rca_json(data)

    # Çıktı dizini oluştur
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Dizin oluşturuldu: {output_dir}")

    # ── Stil tanımları ─────────────────────────────────────────────
    h1 = ParagraphStyle(
        "H1", fontName="Helvetica-Bold", fontSize=16,
        textColor=HSE.primary_dark, spaceAfter=8, spaceBefore=14
    )
    h2 = ParagraphStyle(
        "H2", fontName="Helvetica-Bold", fontSize=13,
        textColor=HSE.primary_mid, spaceAfter=6, spaceBefore=12
    )
    h3 = ParagraphStyle(
        "H3", fontName="Helvetica-Bold", fontSize=10,
        textColor=HSE.text_dark, spaceAfter=5, spaceBefore=8
    )
    body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=10,
        textColor=HSE.text_dark, spaceAfter=5, leading=14
    )
    label_s = ParagraphStyle(
        "LabelS", fontName="Helvetica-Bold", fontSize=8,
        textColor=HSE.text_medium
    )

    # ── PDF Dökümanı ───────────────────────────────────────────────
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
        creator="HSE RCA PDF Generator v2.0",
    )

    on_page = partial(add_page_header, data=data)

    story = []

    # ══════════════════════════════════════════════════════════════
    # SAYFA 1: KAPAK + OLAY BİLGİLERİ
    # ══════════════════════════════════════════════════════════════
    story.extend(build_cover_page(data))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SAYFA 2: KPI ÖZET + 5 WHY ZİNCİRİ
    # ══════════════════════════════════════════════════════════════

    # KPI Kutuları
    story.append(Paragraph("ÖZET GÖSTERGELERİ (KPI)", h2))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.primary_mid, spaceAfter=10
    ))
    story.append(KPISummaryFlowable(data, width=PAGE_WIDTH - 2 * MARGIN))
    story.append(Spacer(1, 20))

    # 5 Why Zinciri
    story.extend(build_five_why_section(data))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SAYFA 3: RİSK MATRİSİ + DEĞERLENDİRME
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("RİSK DEĞERLENDİRMESİ", h1))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.accent_orange, spaceAfter=12
    ))

    risk = data.get("risk_assessment", {})

    # Risk özet tablosu
    risk_label = ParagraphStyle(
        "RLabel", fontName="Helvetica-Bold", fontSize=9,
        textColor=HSE.white
    )
    risk_cell = ParagraphStyle(
        "RCell", fontName="Helvetica", fontSize=10,
        textColor=HSE.text_dark, alignment=TA_CENTER
    )
    risk_cell_bold = ParagraphStyle(
        "RCellB", fontName="Helvetica-Bold", fontSize=10,
        textColor=HSE.text_dark, alignment=TA_CENTER
    )

    improvement_before = risk.get("likelihood_before", 0) - risk.get("likelihood_after", 0)
    improvement_score  = risk.get("risk_score_before", 0) - risk.get("risk_score_after", 0)

    risk_table_data = [
        [Paragraph("PARAMETRE",    risk_label),
         Paragraph("ÖNCE",         risk_label),
         Paragraph("SONRA",        risk_label),
         Paragraph("İYİLEŞME",     risk_label)],
        [Paragraph("Olasilik",     risk_cell),
         Paragraph(str(risk.get("likelihood_before", "—")), risk_cell),
         Paragraph(str(risk.get("likelihood_after",  "—")), risk_cell),
         Paragraph(f"↓ {improvement_before} puan", risk_cell)],
        [Paragraph("Siddet",       risk_cell),
         Paragraph(str(risk.get("severity_before", "—")), risk_cell),
         Paragraph(str(risk.get("severity_after",  "—")), risk_cell),
         Paragraph("Sabit", risk_cell)],
        [Paragraph("Risk Skoru",   risk_cell_bold),
         Paragraph(f"<b>{risk.get('risk_score_before', '—')}</b>", risk_cell_bold),
         Paragraph(f"<b>{risk.get('risk_score_after',  '—')}</b>", risk_cell_bold),
         Paragraph(f"<b>↓ {improvement_score} puan</b>", risk_cell_bold)],
        [Paragraph("Risk Seviyesi", risk_cell),
         Paragraph(risk.get("risk_level_before", "—"), risk_cell),
         Paragraph(risk.get("risk_level_after",  "—"), risk_cell),
         Paragraph("", risk_cell)],
    ]

    risk_tbl = Table(risk_table_data, colWidths=[140, 100, 100, 180])
    risk_style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), HSE.primary_dark),
        ("TEXTCOLOR",     (0, 0), (-1, 0), HSE.white),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HSE.white, HSE.bg_light]),
        ("GRID",          (0, 0), (-1, -1), 0.5, HSE.border_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]

    # Risk seviyesi renklendirme
    before_level = risk.get("risk_level_before", "")
    after_level  = risk.get("risk_level_after",  "")
    before_color = SEVERITY_COLORS.get(before_level, HSE.warning_yellow)
    after_color  = SEVERITY_COLORS.get(after_level,  HSE.success_green)

    risk_style_cmds.append(("BACKGROUND", (1, 4), (1, 4), before_color))
    risk_style_cmds.append(("TEXTCOLOR",  (1, 4), (1, 4), HSE.white))
    risk_style_cmds.append(("BACKGROUND", (2, 4), (2, 4), after_color))
    risk_style_cmds.append(("TEXTCOLOR",  (2, 4), (2, 4), HSE.white))

    risk_tbl.setStyle(TableStyle(risk_style_cmds))
    story.append(risk_tbl)
    story.append(Spacer(1, 20))

    # Risk Matrisi Görsel
    story.append(Paragraph("RİSK MATRİSİ (5×5)", h2))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=HSE.border_light, spaceAfter=10
    ))

    matrix_flowable = RiskMatrixFlowable(
        risk,
        width=PAGE_WIDTH - 2 * MARGIN,
        height=240
    )
    story.append(matrix_flowable)
    story.append(Spacer(1, 20))

    # Katkıda Bulunan Faktörler
    contributing = data.get("contributing_factors", [])
    if contributing:
        story.append(Paragraph("KATKI SAGLAYAN FAKTÖRLER", h2))
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=HSE.border_light, spaceAfter=8
        ))
        factor_rows = [[Paragraph(f"• {f}", body)] for f in contributing]
        factor_table = Table(factor_rows, colWidths=[PAGE_WIDTH - 2 * MARGIN])
        factor_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), HSE.bg_light),
            ("LEFTPADDING",   (0, 0), (-1, -1), 16),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBEFORE",    (0, 0), (0, -1), 4, HSE.medium_orange),
        ]))
        story.append(factor_table)
        story.append(Spacer(1, 15))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SAYFA 4: DÜZELTİCİ FAALİYETLER
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("DÜZELTİCİ VE ÖNLEYİCİ FAALİYETLER", h1))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.success_green, spaceAfter=12
    ))
    story.append(build_corrective_actions_table(data))
    story.append(Spacer(1, 25))

    # ══════════════════════════════════════════════════════════════
    # SAYFA 4 (devam): ÇIKARILAN DERSLER
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("ÇIKARILAN DERSLER", h1))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=HSE.primary_light, spaceAfter=10
    ))

    lessons_style = ParagraphStyle(
        "Lessons", fontName="Helvetica-Oblique", fontSize=11,
        textColor=HSE.primary_dark, leading=17,
        leftIndent=15, rightIndent=15
    )
    lessons_box = Table(
        [[Paragraph(data.get("lessons_learned", "Ders bilgisi mevcut degil."), lessons_style)]],
        colWidths=[PAGE_WIDTH - 2 * MARGIN]
    )
    lessons_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HSE.bg_light),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("LINEBEFORE",    (0, 0), (0, -1), 5, HSE.primary_mid),
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, HSE.border_light),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, HSE.border_light),
    ]))
    story.append(lessons_box)
    story.append(Spacer(1, 30))

    # ── İmza Alanları ──────────────────────────────────────────────
    story.append(Paragraph("ONAY VE İMZALAR", h2))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=HSE.border_light, spaceAfter=20
    ))

    sig_line = ParagraphStyle(
        "SigLine", fontName="Helvetica", fontSize=9,
        textColor=HSE.text_medium, alignment=TA_CENTER
    )
    sig_name = ParagraphStyle(
        "SigName", fontName="Helvetica-Bold", fontSize=9,
        textColor=HSE.text_dark, alignment=TA_CENTER
    )
    sig_date = ParagraphStyle(
        "SigDate", fontName="Helvetica", fontSize=8,
        textColor=HSE.text_medium, alignment=TA_CENTER
    )

    sig_data = [
        [Paragraph("_" * 25, sig_line),
         Paragraph("_" * 25, sig_line),
         Paragraph("_" * 25, sig_line)],
        [Paragraph("HSE Yöneticisi",       sig_name),
         Paragraph("Departman Müdürü",     sig_name),
         Paragraph("İnceleme Sorumlusu",   sig_name)],
        [Paragraph("Tarih: ___/___/______", sig_date),
         Paragraph("Tarih: ___/___/______", sig_date),
         Paragraph("Tarih: ___/___/______", sig_date)],
    ]

    sig_table = Table(sig_data, colWidths=[170, 170, 170])
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 20))

    # ── Rapor Meta Bilgisi ─────────────────────────────────────────
    meta_style = ParagraphStyle(
        "Meta", fontName="Helvetica", fontSize=7,
        textColor=HSE.text_medium, alignment=TA_CENTER
    )
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=HSE.border_light, spaceAfter=6
    ))
    story.append(Paragraph(
        f"Bu rapor HSE RCA PDF Generator v2.0 tarafından {gen_time} tarihinde otomatik olarak üretilmiştir. "
        f"Rapor ID: {data.get('incident_id', 'N/A')} | "
        f"Metot: {data.get('analysis_method', 'HSG245 5-Why')}",
        meta_style
    ))

    # ── PDF Oluştur ────────────────────────────────────────────────
    print(f"PDF oluşturuluyor: {output_path}")
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"✅ Rapor başarıyla oluşturuldu: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════
# MAIN — GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # ── RCA Verisi ─────────────────────────────────────────────────
    rca_data = {
        "incident_id": "INC-2026-02-0000",
        "incident_title": "Root Cause Analysis",
        "incident_date": "2026-02-23",
        "location": "Uretim Sahasi / Fabrika",
        "department": "HSE & Operations",
        "severity": "HIGH",
        "incident_type": "Root Cause Analysis",
        "reported_by": "Sistem Operatoru",
        "investigated_by": "Agentic AI RCA Sistemi",
        "investigation_date": "2026-02-23",
        "description": (
            "Uretim sahasinda gerceklestirilen hiyerarsik 5-Why analizi kapsaminda "
            "detayli kok neden incelemesi yapilmistir. HSG245 metodolojisi uygulanarak "
            "olayin temel nedenleri sistematik bicimde tespit edilmistir."
        ),
        "immediate_consequences": [
            "Hiyerarsik 5-Why metodolojisi uygulandı",
            "Organizasyonel ve sistemsel faktorler incelendi",
            "Kok neden analizi tamamlandi",
        ],
        "five_whys": [
            {
                "why": 1,
                "question": "Neden 1: Olay neden meydana geldi?",
                "answer": "Ekipman arızası tespit edildi, detaylı inceleme devam ediyor.",
                "evidence": "Saha gozlem kayitlari, operatör raporlari",
                "confidence": "MEDIUM",
            },
            {
                "why": 2,
                "question": "Neden 2: Ekipman neden ariza yapti?",
                "answer": "Periyodik bakim prosedurlerinin eksik uygulandigi belirlendi.",
                "evidence": "Bakim is emirleri, CMMS kayitlari",
                "confidence": "MEDIUM",
            },
            {
                "why": 3,
                "question": "Neden 3: Bakim prosedürleri neden eksik uygulandı?",
                "answer": "Kontrol listelerinde kritik adimlar yer almiyordu.",
                "evidence": "Mevcut prosedur dokumanlari v2.1",
                "confidence": "MEDIUM",
            },
        ],
        "root_cause": "Kok neden belirleniyor — Prosedur eksikligi on plana cikiyor.",
        "contributing_factors": [],
        "corrective_actions": [],
        "risk_assessment": {
            "likelihood_before": 4,
            "severity_before":   5,
            "risk_score_before": 20,
            "risk_level_before": "CRITICAL",
            "likelihood_after":  2,
            "severity_after":    4,
            "risk_score_after":  8,
            "risk_level_after":  "MEDIUM",
        },
        "lessons_learned": (
            "Hiyerarsik 5-Why metodolojisi ile coklu kok neden basariyla tespit edildi. "
            "Organizasyonel ve sistemsel faktorler oncelikli olarak ele alinmalidir. "
            "Bakim prosedurlerinin periyodik gozden gecirilmesi ve kritik guvenlik "
            "unsurlarinin kontrol listelerinde yer almasi zorunludur."
        ),
        "similar_incidents": 0,
        "estimated_cost": 0,
        "analysis_method": "HSG245 5-Why Hierarchical Analysis",
        "total_branches": 0,
        "total_root_causes": 0,
    }

    # JSON dosyası olarak da okuyabilir
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                rca_data = json.load(f)
            print(f"JSON dosyası okundu: {sys.argv[1]}")
        except Exception as e:
            print(f"JSON okuma hatası: {e} — Varsayılan veri kullanılıyor.")

    # Çıktı yolu
    output_file = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "outputs/reports/HSE_RCA_Report_20260223_014925.pdf"
    )

    try:
        result = generate_hse_rca_report(rca_data, output_file)
        print(f"\n{'='*60}")
        print(f"  HSE RCA RAPORU BASARIYLA OLUSTURULDU")
        print(f"  Dosya: {result}")
        print(f"  Boyut: {os.path.getsize(result):,} bytes")
        print(f"{'='*60}\n")
    except ImportError as e:
        print(f"HATA: Eksik kütüphane — {e}")
        print("Çözüm: pip install reportlab --break-system-packages")
        sys.exit(1)
    except Exception as e:
        print(f"HATA: Rapor oluşturulamadı — {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
