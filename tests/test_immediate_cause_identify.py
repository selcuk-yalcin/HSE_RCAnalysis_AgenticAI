"""Doğrudan neden tanımlama — form şablonu yerine olay metni."""

from agents.hitl_question_service import _immediate_causes_from_payload, identify_immediate_causes_for_hitl

GENERIC_RCI = """1. Makine çalışır durumdayken elle müdahale
2. Koruyucu kapak/sensör sistemi yok
3. Üretim baskısı - durdurmayalım kültürü
4. Sık sıkışma sorunu (kronik) - normalleşmiş risk
5. Acil durdurma butonlarının konumu uygunsuz"""

INCIDENT = (
    "Forklift operatörü depo koridorunda yaya ile çarpıştı. "
    "Yaya korkuluk olmayan geçişten geçmişti; görüş mesafesi palet yığını nedeniyle kapalıydı."
)


def test_immediate_causes_from_payload_uses_narrative_not_rci():
    causes = _immediate_causes_from_payload(None, INCIDENT)
    assert isinstance(causes, list)
    if causes:
        assert all(c.get("identify_source") == "narrative_infer" for c in causes)
        assert all("Makine çalışır" not in str(c.get("cause_tr") or "") for c in causes)


def test_immediate_causes_from_payload_ignores_generic_root_cause_initial():
    """API listesi yokken formdaki numaralı şablon satırları neden olarak dönmemeli."""
    causes = identify_immediate_causes_for_hitl(
        how_happened=INCIDENT,
        root_cause_initial=GENERIC_RCI,
        output_language="tr",
        max_causes=4,
    )
    for row in causes:
        label = " ".join(
            str(row.get(k) or "")
            for k in ("cause_tr", "evidence_tr", "standard_title_tr")
        )
        assert "elle müdahale" not in label.lower()
        assert "koruyucu kapak" not in label.lower()
        assert "üretim baskısı" not in label.lower()
