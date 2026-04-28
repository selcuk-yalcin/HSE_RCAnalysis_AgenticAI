"""
Dinamik HITL soru üretimi: disambiguation bankası + HybridInputProcessor + QuestionEngine
(knowledge_base taxonomy şablonları). Sabit frontend listesi yok.
"""

from __future__ import annotations

import hashlib
import re
import os
import json
from typing import Any
from openai import OpenAI

from agents.hitl_disambiguation_bank import build_questions_for_causes
from agents.hgs_taxonomy import parse_hsg_taxonomy_items, infer_codes_from_text
from agents.model_constants import resolve_openrouter_chat_model

_HS_CODE_RE = re.compile(r"\b([ABCD][0-9]+\.[0-9]+)\b", re.IGNORECASE)
_GENERIC_PATTERNS = (
    "olay hangi tarih ve saatte",
    "risk değerlendirmesi yapılmış mıydı",
    "risk degerlendirmesi yapilmis miydi",
)
_GENERIC_QUESTION_REGEXES = (
    r"olay\s+öncesi\s+son\s+\d+\s+saat",
    r"kaç\s+saatlik\s+vardiya",
    r"fazla\s+mesai",
    r"olay\s+s[ıi]ras[ıi]nda\s+ba[sş]ka\s+kimler",
    r"g[öo]zetmen/formen\s+olay\s+s[ıi]ras[ıi]nda",
    r"hangi\s+ekipman/alet\s+kullan[ıi]ld[ıi]",
    r"bu\s+i[sş]\s+i[çc]in\s+hangi\s+kkd",
    r"çal[ıi][sş]an\s+gerekli\s+t[üu]m\s+kkd",
)

_INCIDENT_SIGNAL_HINTS = {
    r"olay\s+öncesi\s+son\s+\d+\s+saat|kaç\s+saatlik\s+vardiya|fazla\s+mesai": (
        "vardiya",
        "mesai",
        "yorgun",
        "uyku",
        "nobet",
        "shift",
        "fatigue",
    ),
    r"olay\s+s[ıi]ras[ıi]nda\s+ba[sş]ka\s+kimler|g[öo]zetmen/formen": (
        "tanik",
        "gorgu",
        "formen",
        "gözetmen",
        "gozetmen",
        "supervisor",
        "witness",
        "ekip",
        "yalniz",
        "yalnız",
    ),
    r"hangi\s+ekipman/alet|ekipman|alet": (
        "ekipman",
        "iskele",
        "merdiven",
        "platform",
        "tool",
        "equipment",
        "makine",
    ),
    r"\bkkd\b|ppe|kişisel\s+koruyucu|kisisel\s+koruyucu": (
        "kkd",
        "baret",
        "kemer",
        "lanyard",
        "ppe",
        "koruyucu",
    ),
}

_KNOWN_FIELD_GUARD_PATTERNS = {
    "risk_assessment": (r"risk\s+de[ğg]erlendirmesi",),
    "timeline_known": (r"hangi\s+tarih", r"hangi\s+saat", r"ne\s+zaman"),
    "training_known": (r"e[ğg]itim", r"sertifika", r"yetki belgesi"),
    "ppe_known": (r"\bkkd\b", r"\bppe\b"),
    "permit_known": (r"i[sş]\s+izni", r"\bptw\b", r"permit"),
    "weather_known": (r"hava\s+ko[şs]ullar", r"ya[ğg]mur|r[üu]zgar|s[ıi]cak"),
    "lighting_known": (r"ayd[ıi]nlatma",),
}

try:
    _TAXONOMY_ITEMS = parse_hsg_taxonomy_items("agents/knowledge.json")
except Exception:
    _TAXONOMY_ITEMS = []

_HITL_LLM_ENABLED = (os.getenv("HITL_USE_LLM") or "1").strip().lower() in ("1", "true", "yes", "on")

# "free_text" = cevap Evet/Hayır/Bilinmiyor olamaz (sebep, seçenek, açıklama beklenir).
# "choice" = arayüzde sabit/LLM listesi; çoklu veya tek seçim (PPE, ekipman).

_DEFAULT_PPE_TR_OPTIONS: tuple[str, ...] = (
    "Baret (baş koruması)",
    "Gözlük / yüz kalkanı",
    "İşitme koruyucu (kulak tıkacı/ earmuff)",
    "Solunum (FFP/ maske / SCBA'ya göre iş riski)",
    "Eldiven (kimyasal/ kesim/ ısıya uygun türde)",
    "Koruyucu elbise, ön veya tulum",
    "Güvenlik ayakkabısı / çizme (çelik burun, kaymaz taban)",
    "Düşmeye karşı emniyet kemeri / lanyard / can halatı",
    "Yüksek görünürlüklü yelek (EN ISO 20471 benzeri)",
    "Kemirgen / biyolojik riske uygun KKD (gerekliyse belirtin)",
    "Diğer / o olayda kullanılması en kritik 1–2 KKD'yi açık yazın",
)

_DEFAULT_PPE_EN_OPTIONS: tuple[str, ...] = (
    "Helmet (head protection)",
    "Safety glasses / face shield",
    "Hearing protection (earplugs/ earmuff)",
    "R respirator / mask (type per risk — FFP, half/full face, SCBA)",
    "Gloves (chemical/cut/heat-appropriate type)",
    "Coveralls, apron, or full-body PPE as required",
    "Safety shoes / boots (steel-toe, slip resistance)",
    "Fall protection: harness, lanyard, lifeline",
    "High-visibility vest (e.g. EN ISO 20471 class)",
    "PPE for biological/rodent risk (specify if relevant)",
    "Other — name the 1–2 PPE that mattered most in this case",
)


def _normalize_str_list(v: Any, max_n: int = 30) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [s.strip() for s in re.split(r"[,;\n|]", v) if s.strip()][:max_n]
    if isinstance(v, (list, tuple)):
        return [str(x).strip() for x in v if str(x).strip()][:max_n]
    return []


def _enrich_hitl_ui(soru: str, q: dict) -> dict[str, Any]:
    """
    response_mode: yes_no_unknown | free_text | choice
    choice_options: Trafik etiketleri (TR); aynı uzunlukta choice_options_en = gösterim dili.
    """
    s = (soru or "").strip()
    low = s.lower()
    o_tr = _normalize_str_list((q or {}).get("choice_options") or (q or {}).get("options"))
    o_en = _normalize_str_list(
        (q or {}).get("choice_options_en") or (q or {}).get("options_en"),
    )

    # 1) Açık seçenek listesi (LLM / şablon)
    if len(o_tr) >= 2:
        if len(o_en) != len(o_tr) or not o_en:
            o_en = o_tr[:]
        multi = bool(
            (q or {}).get("choice_multi", (q or {}).get("multi", False)) or
            re.search(
                r"(k?kd[''´` ]?ler|korumal|neler|hangileri|birden|fazla|hepsi|t[üu]m(ünü)?|list|se[çc]|belirt|çeşit|cesit|veya|and)",
                low,
            ) or
            re.search(
                r"\bve\s+birden|,\s*ve\s+",
                low,
            ) or
            bool((q or {}).get("force_choice_multi", False))
        )
        return {
            "response_mode": "choice",
            "choice_options": o_tr,
            "choice_options_en": o_en,
            "choice_multi": bool(multi),
        }

    # 2) "Hangi KKD" vb. — varsayılan PPE / koruma listesi
    if re.search(r"\bhangi\b", low) and re.search(
        r"(\bkkd\b|kisisel\s+koruyucu|kişisel\s+koruyucu|ppe|baret|eldiven|ayakkab|gözlük|göz|isitme|dusm|düşm|can\s+halat|kemer|emniyet)",
        low,
    ):
        ppe_multi = bool(
            re.search(
                r"kkd[''´` ]?ler|korumal|neler|hangileri|gerekli(ydi|ydı|ydu)?|gerek(irdi)?|list|belirt|çeşit|cesit",
                low,
            ) or
            re.search(
                r"\bve\s+birden|,\s*ve\s+", low,
            ),
        )
        return {
            "response_mode": "choice",
            "choice_options": list(_DEFAULT_PPE_TR_OPTIONS),
            "choice_options_en": list(_DEFAULT_PPE_EN_OPTIONS),
            "choice_multi": bool(ppe_multi),
        }

    # 3) Sadece mode + metin türü (free_text vs evet-hayır)
    ex = str((q or {}).get("response_mode", "") or "").strip().lower()
    if ex in ("free_text", "freetext", "text"):
        m3 = "free_text"
    elif ex in ("yes_no", "yesno", "yes_no", "yes_no_unknown", "bool"):
        m3 = "yes_no_unknown"
    else:
        m3 = _infer_response_mode(s)
    if m3 not in ("free_text", "yes_no_unknown"):
        m3 = "yes_no_unknown"
    return {
        "response_mode": m3,
        "choice_options": [],
        "choice_options_en": [],
        "choice_multi": False,
    }


def _infer_response_mode(soru: str) -> str:
    """
    UI'nin Evet/Hayır/Bilinmiyor mı yoksa serbest metin mi toplayacağını seçer.
    Açık choice-style sorularda (ör. 'A mı, B mı, C mü?') free_text.
    """
    t = (soru or "").strip()
    if len(t) < 8:
        return "yes_no_unknown"
    low = t.lower()
    # Birden fazla mı/mi sorusu eki = çoklu seçenek; Evet/Hayır yeterli değil
    tr_q_particles = re.findall(r"(?i)\b(mı|mi|mu|mü)\b", t)
    if len(tr_q_particles) >= 2:
        return "free_text"
    if ("—" in t or " – " in t) and re.search(
        r"(?i)(mı|mi|mu|mü).*(mı|mi|mu|mü)|,\s*[^,]{2, 80}(mı|mi|mu|mü)", t
    ):
        return "free_text"
    if " veya " in low and "?" in t and len(t) > 40:
        return "free_text"
    if re.search(r"\b(or|versus|rather than)\b", low) and "?" in t and len(t) > 35:
        return "free_text"
    if re.search(r"\byoksa\b", low) and "?" in t and len(t) > 20:
        return "free_text"
    if re.search(
        r"\b(hangi|açıkla|acikla|detaylandır|açıkça|açıkla:)\b",
        low,
        re.IGNORECASE,
    ) and "?" in t:
        return "free_text"
    if re.search(
        r"neden(ler|i)?\s*(\(|—|:|\s+)(.|\n)*(yoksa| veya )",
        low,
    ):
        return "free_text"
    return "yes_no_unknown"


def extract_hs_codes(text: str) -> list[str]:
    if not text:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for m in _HS_CODE_RE.finditer(text):
        code = m.group(1).upper()
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{h}"


_QUESTION_NOISE_RX = re.compile(r"\b([abcd]\d+\.\d+|vs|veya|yoksa|icin|için)\b", re.IGNORECASE)


def _question_fingerprint(text: str) -> str:
    """
    Aynı niyeti taşıyan soruları normalize et:
    - HSG kodlarını ve bağlaç gürültüsünü temizle
    - Noktalama/boşluk farklarını yok say
    """
    s = str(text or "").lower().strip()
    if not s:
        return ""
    s = _QUESTION_NOISE_RX.sub(" ", s)
    s = re.sub(r"[^\wçğıöşü\s]", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tokenize_question(text: str) -> set[str]:
    s = _question_fingerprint(text)
    if not s:
        return set()
    toks = {t for t in s.split(" ") if len(t) >= 3}
    stop = {
        "nedir", "neden", "mi", "mı", "mu", "mü", "icin", "için", "gore", "göre",
        "oldu", "olabilir", "var", "yok", "bu", "soru", "olay", "durum", "kadar",
        "sahada", "miydi", "yardim", "yardım", "kanit", "kanıt", "ne", "hangi",
    }
    return {t for t in toks if t not in stop}


def _is_overlapping_question(text: str, seen_fingerprints: set[str], seen_token_sets: list[set[str]]) -> bool:
    fp = _question_fingerprint(text)
    if not fp:
        return True
    if fp in seen_fingerprints:
        return True
    cur = _tokenize_question(text)
    if not cur:
        return False
    # Yüksek örtüşen soruları ele (ör. "neden KKD yoktu..." varyantları)
    for prev in seen_token_sets:
        if not prev:
            continue
        inter = len(cur.intersection(prev))
        union = len(cur.union(prev))
        if union <= 0:
            continue
        jacc = inter / union
        if jacc >= 0.72:
            return True
    return False


def _register_question(text: str, seen_fingerprints: set[str], seen_token_sets: list[set[str]]) -> None:
    fp = _question_fingerprint(text)
    if fp:
        seen_fingerprints.add(fp)
    seen_token_sets.append(_tokenize_question(text))


def _immediate_causes_from_payload(
    immediate_causes: list[dict] | None,
    root_cause_initial: str,
) -> list[dict]:
    if immediate_causes:
        return [c for c in immediate_causes if isinstance(c, dict)]
    codes = extract_hs_codes(root_cause_initial or "")
    if not codes:
        # fallback: derive candidate codes from first immediate-cause lines
        lines = [
            re.sub(r"^\s*\d+[\.)-]?\s*", "", ln).strip()
            for ln in str(root_cause_initial or "").splitlines()
            if ln.strip()
        ][:6]
        for ln in lines:
            for c in infer_codes_from_text(ln, _TAXONOMY_ITEMS, top_k=2):
                if c not in codes:
                    codes.append(c)
    return [{"code": c, "cause_tr": c} for c in codes[:5]]


def _build_deep_questions_from_taxonomy(code: str, why_level: int) -> list[dict]:
    if not code or not _TAXONOMY_ITEMS:
        return []
    item = next((x for x in _TAXONOMY_ITEMS if x.code == code), None)
    if item is None:
        return []

    out: list[dict] = []
    # Prefer "choose_if" lines as targeted disambiguation probes.
    for idx, choose in enumerate(item.choose_if[:2], start=1):
        q = f"{item.code} ({item.title}) icin: {choose} Bu olayda sahaya ne kadar uyuyordu?"
        out.append(
            {
                "id": _stable_id("tx-c", code, str(why_level), str(idx), q),
                "source": "why_probe_taxonomy_code",
                "code": item.code,
                "cause_desc": item.title,
                "hsg245": item.code,
                "soru": q,
                "yönler": {},
                "why_level": why_level,
            }
        )
    # One deepening question from "not this if" to reduce wrong mapping.
    if item.not_this_if:
        nt = item.not_this_if[0]
        q = f"Bu durum `{item.code}` yerine `{nt}` olabilir mi? Ayirmamiza yardim edecek kanit var mi?"
        out.append(
            {
                "id": _stable_id("tx-n", code, str(why_level), q),
                "source": "why_probe_taxonomy_code",
                "code": item.code,
                "cause_desc": item.title,
                "hsg245": item.code,
                "soru": q,
                "yönler": {},
                "why_level": why_level,
            }
        )
    return out


def _filter_questions(
    questions: list[dict[str, Any]],
    known_fields: list[str] | None,
    incident_context: str = "",
) -> list[dict[str, Any]]:
    known = {str(k or "").strip().lower() for k in (known_fields or []) if str(k or "").strip()}
    context_low = str(incident_context or "").lower()
    out: list[dict[str, Any]] = []
    for q in questions:
        text = str(q.get("soru") or "").strip()
        if not text:
            continue
        low = text.lower()
        if any(p in low for p in _GENERIC_PATTERNS):
            continue
        # Hard-filter generic checklist style prompts unless incident text carries matching signals.
        blocked = False
        for generic_rx in _GENERIC_QUESTION_REGEXES:
            if re.search(generic_rx, low, flags=re.IGNORECASE):
                signal_keywords = ()
                for signal_rx, hints in _INCIDENT_SIGNAL_HINTS.items():
                    if re.search(signal_rx, generic_rx, flags=re.IGNORECASE):
                        signal_keywords = hints
                        break
                if signal_keywords and not any(k in context_low for k in signal_keywords):
                    blocked = True
                elif not signal_keywords:
                    blocked = True
                break
        if blocked:
            continue
        skip = False
        for field in known:
            for patt in _KNOWN_FIELD_GUARD_PATTERNS.get(field, ()):
                if re.search(patt, low, flags=re.IGNORECASE):
                    skip = True
                    break
            if skip:
                break
        if not skip:
            out.append(q)
    return out


def _taxonomy_gap_questions(full_text: str, max_categories: int = 4, per_cat: int = 2) -> list[dict]:
    # Local imports: hitl_test modülleri repo kökünden import edilir (api/main sys.path).
    from hitl_test.hybrid_input_processor import HybridInputProcessor
    from hitl_test.question_engine import QuestionEngine

    _, det = HybridInputProcessor().detect_input_level(full_text or "")
    missing = det.get("missing") or []
    if not missing:
        return []
    qe = QuestionEngine()
    out: list[dict] = []
    for cat in missing[:max_categories]:
        rows = qe.generate_questions_for_missing_categories([cat])
        for i, row in enumerate(rows[:per_cat]):
            qtext = row.get("question") or ""
            if not qtext:
                continue
            hid = _stable_id("kb", cat, str(i), qtext)
            out.append(
                {
                    "id": hid,
                    "source": "taxonomy_gap",
                    "code": "",
                    "cause_desc": row.get("category_description", cat),
                    "hsg245": row.get("hsg245_link") or row.get("hsg245_codes", ""),
                    "soru": qtext,
                    "yönler": {},
                    "category": cat,
                    "required": bool(row.get("required")),
                }
            )
    return out


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    if not text:
        return []
    s = text.strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3].rstrip()
    try:
        data = json.loads(s)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except Exception:
        pass
    m = re.search(r"\[[\s\S]*\]", s)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except Exception:
        return []
    return []


def _taxonomy_prompt_context(focus_codes: list[str], max_items: int = 4) -> str:
    if not focus_codes or not _TAXONOMY_ITEMS:
        return ""
    rows: list[str] = []
    for code in focus_codes[:max_items]:
        item = next((x for x in _TAXONOMY_ITEMS if x.code == code), None)
        if not item:
            continue
        choose = "; ".join(item.choose_if[:2])
        not_this = "; ".join(item.not_this_if[:1])
        rows.append(
            f"- {item.code} | {item.title} | choose_if: {choose} | not_this_if: {not_this}"
        )
    return "\n".join(rows)


def _llm_question_candidates(
    *,
    how_happened: str,
    root_cause_initial: str,
    focus_codes: list[str],
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
    known_fields: list[str] | None = None,
    max_questions: int = 6,
) -> list[dict[str, Any]]:
    if not _HITL_LLM_ENABLED:
        return []
    api_key = (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return []
    taxonomy_ctx = _taxonomy_prompt_context(focus_codes)
    if not taxonomy_ctx:
        return []
    model = resolve_openrouter_chat_model()
    if not model.startswith("openrouter/"):
        model = f"openrouter/{model}"

    known = ", ".join(known_fields or [])
    prompt = f"""
Sen HSE RCA HITL soru asistanısın.
Yalnızca olayla doğrudan ilgili, dalı derinleştiren, non-generic sorular üret.

Olay özeti:
{how_happened}

İlk kök neden çıktısı:
{root_cause_initial}

Why seviyesi: {why_level}
Mevcut Why sorusu: {current_why_question}
Önceki Why cevabı: {previous_why_answer}
Bilinen form alanları (bunları tekrar sorma): {known}

Taxonomy odak kodları:
{taxonomy_ctx}

Kurallar:
- Olaya özgü sor; yalnız kopya-şablon sorma. Kanıt veya ayrıntı ister.
- HSG koduna bağla.
- Türkçe, kısa, net.
- Cevap türü: (1) basit "answer_format": "yes_no" (2) açık metin: "free_text" (3) tıklanabilir etiket listesi: "answer_format": "choice", "options": ["3–8 kısa kategori"], "options_en" (aynı sıra, İngilizce), "multi": true bir veya false tek seçim.
- "hangi KKD" gibi cevabı belli liste olan sorulara "choice" + options koy; Evet/Hayır yeterli değilse "yes_no" kullanma.
- JSON array: [{{"question_tr":"...","code":"A1.1","answer_format":"yes_no"|"free_text"|"choice","options":[]|null,"options_en":[]|null,"multi":false,"reason":"..."}}]
- En fazla {max_questions} soru.
""".strip()

    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200,
        )
        content = (resp.choices[0].message.content or "").strip()
        items = _extract_json_array(content)
        out: list[dict[str, Any]] = []
        for i, it in enumerate(items[:max_questions], start=1):
            q = str(it.get("question_tr") or "").strip()
            code = str(it.get("code") or "").strip().upper()
            if not q:
                continue
            af = str(it.get("answer_format") or "").strip().lower()
            c_opts = _normalize_str_list(it.get("options") or it.get("choice_options"))
            c_en = _normalize_str_list(it.get("options_en") or it.get("choice_options_en"))
            c_multi = bool(it.get("multi", it.get("choice_multi", False)))
            if af in ("choice", "options", "list", "multi_choice") and len(c_opts) >= 2:
                rmode = "choice"
            elif af in ("free_text", "freetext", "text", "açık"):
                rmode = "free_text"
            elif af in ("yes_no", "yesno", "boolean", "bool"):
                rmode = "yes_no_unknown"
            else:
                rmode = _infer_response_mode(q)
            row: dict[str, Any] = {
                "id": _stable_id("llm", str(why_level), code, str(i), q),
                "source": "why_probe_llm",
                "code": code,
                "cause_desc": code,
                "hsg245": code,
                "soru": q,
                "yönler": {},
                "why_level": why_level,
                "response_mode": rmode,
            }
            if c_opts:
                row["choice_options"] = c_opts
            if c_en and len(c_en) == len(c_opts):
                row["choice_options_en"] = c_en
            if c_multi:
                row["choice_multi"] = True
            out.append(row)
        return out
    except Exception:
        return []


def build_hitl_question_pool(
    how_happened: str,
    root_cause_initial: str,
    immediate_causes: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """
    API + Gradio için tek havuz: önce immediate cause disambiguation, sonra eksik kategori soruları.
    """
    causes = _immediate_causes_from_payload(immediate_causes, root_cause_initial or "")
    focus_codes = [str((c or {}).get("code") or "").strip().upper() for c in causes if (c or {}).get("code")]
    disamb_raw = build_questions_for_causes(causes)
    pool: list[dict[str, Any]] = []
    seen_q_fp: set[str] = set()
    seen_q_tokens: list[set[str]] = []

    for row in disamb_raw:
        soru = str(row.get("soru") or "").strip()
        if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
            continue
        _register_question(soru, seen_q_fp, seen_q_tokens)
        code = row.get("code", "")
        qid = _stable_id("d", code, soru)
        pool.append(
            {
                "id": qid,
                "source": "disambiguation",
                "code": code,
                "cause_desc": row.get("cause_desc", code),
                "hsg245": row.get("hsg245", ""),
                "soru": soru,
                "yönler": row.get("yönler") or {},
            }
        )

    full_text = "\n\n".join(
        s for s in (how_happened or "", root_cause_initial or "") if s.strip()
    )
    for row in _taxonomy_gap_questions(full_text):
        soru = str(row.get("soru") or "").strip()
        if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
            continue
        _register_question(soru, seen_q_fp, seen_q_tokens)
        pool.append(row)

    llm_rows = _llm_question_candidates(
        how_happened=how_happened or "",
        root_cause_initial=root_cause_initial or "",
        focus_codes=focus_codes[:4],
        why_level=1,
        known_fields=[],
        max_questions=6,
    )
    for row in llm_rows:
        soru = str(row.get("soru") or "").strip()
        if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
            continue
        _register_question(soru, seen_q_fp, seen_q_tokens)
        pool.insert(0, row)

    return pool[:20]


def next_hitl_questions(
    how_happened: str,
    root_cause_initial: str,
    answered_ids: list[str],
    immediate_causes: list[dict] | None = None,
    batch_size: int = 1,
    known_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Cevaplanmış id'leri düşürür; sıradaki batch_size soruyu döndürür.
    """
    answered = set(answered_ids or [])
    pool = _filter_questions(
        build_hitl_question_pool(how_happened, root_cause_initial, immediate_causes),
        known_fields=known_fields,
        incident_context="\n".join([how_happened or "", root_cause_initial or ""]),
    )
    pending = [q for q in pool if q.get("id") not in answered]
    batch = pending[: max(1, batch_size)]

    def _shape(q: dict) -> dict[str, Any]:
        soru = str(q.get("soru", "") or "")
        u = _enrich_hitl_ui(soru, q)
        return {
            "id": q["id"],
            "source": q.get("source", "disambiguation"),
            "hsg_hint": q.get("hsg245", ""),
            "code": q.get("code", ""),
            "cause_desc": q.get("cause_desc", ""),
            "question_tr": soru,
            "question_en": soru,
            "yönler": q.get("yönler") or {},
            "response_mode": u.get("response_mode", "yes_no_unknown"),
            "choice_options": u.get("choice_options") or [],
            "choice_options_en": u.get("choice_options_en") or [],
            "choice_multi": bool(u.get("choice_multi", False)),
        }

    return {
        "questions": [_shape(q) for q in batch],
        "total_pool": len(pool),
        "remaining_after_batch": max(0, len(pending) - len(batch)),
        "done": len(pending) == 0,
    }


def build_why_probe_question_pool(
    how_happened: str,
    root_cause_initial: str,
    immediate_code: str = "",
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
    known_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Why zinciri içinde ara netleştirme soruları üretir.

    Sıra:
      1) Immediate code için disambiguation
      2) Code-specific taxonomy soruları
      3) Eksik bilgi kategorileri (HybridInputProcessor + QuestionEngine)
    """
    from hitl_test.question_engine import QuestionEngine

    focus_codes: list[str] = []
    if immediate_code:
        focus_codes.append(immediate_code.upper())
    for code in extract_hs_codes("\n".join([root_cause_initial or "", current_why_question or ""])):
        if code not in focus_codes:
            focus_codes.append(code)
    focus_codes = focus_codes[:3]

    pool: list[dict[str, Any]] = []
    seen_q_fp: set[str] = set()
    seen_q_tokens: list[set[str]] = []

    # 1) Code-grounded deep questions directly from taxonomy item.
    llm_rows = _llm_question_candidates(
        how_happened=how_happened or "",
        root_cause_initial=root_cause_initial or "",
        focus_codes=focus_codes,
        why_level=why_level,
        current_why_question=current_why_question or "",
        previous_why_answer=previous_why_answer or "",
        known_fields=known_fields or [],
        max_questions=6,
    )
    for row in llm_rows:
        soru = str(row.get("soru") or "").strip()
        if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
            continue
        _register_question(soru, seen_q_fp, seen_q_tokens)
        pool.append(row)

    # 2) Code-grounded deep questions directly from taxonomy item.
    for code in focus_codes:
        for row in _build_deep_questions_from_taxonomy(code, why_level):
            soru = str(row.get("soru") or "").strip()
            if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
                continue
            _register_question(soru, seen_q_fp, seen_q_tokens)
            pool.append(row)

    # 3) Disambiguation (hedef immediate code)
    if focus_codes:
        causes = [{"code": c, "cause_tr": c} for c in focus_codes]
        for row in build_questions_for_causes(causes)[:4]:
            soru = str(row.get("soru") or "").strip()
            if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
                continue
            _register_question(soru, seen_q_fp, seen_q_tokens)
            qid = _stable_id("wp-d", str(why_level), row.get("code", ""), soru)
            pool.append(
                {
                    "id": qid,
                    "source": "why_probe_disambiguation",
                    "code": row.get("code", ""),
                    "cause_desc": row.get("cause_desc", ""),
                    "hsg245": row.get("hsg245", ""),
                    "soru": soru,
                    "yönler": row.get("yönler") or {},
                    "why_level": why_level,
                }
            )

    # 4) Code-specific questions (knowledge_base bağlı template'ler)
    qe = QuestionEngine()
    for i, row in enumerate(qe.get_code_specific_questions(focus_codes)[:6]):
        soru = str(row.get("question") or "").strip()
        code = row.get("hsg245_code", "")
        if not soru or _is_overlapping_question(soru, seen_q_fp, seen_q_tokens):
            continue
        _register_question(soru, seen_q_fp, seen_q_tokens)
        qid = _stable_id("wp-c", str(why_level), code, str(i), soru)
        pool.append(
            {
                "id": qid,
                "source": "why_probe_code_specific",
                "code": code,
                "cause_desc": row.get("code_description", ""),
                "hsg245": code,
                "soru": soru,
                "yönler": {},
                "why_level": why_level,
            }
        )

    incident_ctx = "\n".join(
        [
            how_happened or "",
            root_cause_initial or "",
            current_why_question or "",
            previous_why_answer or "",
            " ".join(focus_codes),
        ]
    )
    return _filter_questions(pool[:14], known_fields=known_fields, incident_context=incident_ctx)


def next_why_probe_questions(
    how_happened: str,
    root_cause_initial: str,
    answered_ids: list[str],
    immediate_code: str = "",
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
    batch_size: int = 1,
    known_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Why-level ara sorular: her seviyede daha net sebep ayrımı için döngüsel API.
    """
    answered = set(answered_ids or [])
    pool = build_why_probe_question_pool(
        how_happened=how_happened,
        root_cause_initial=root_cause_initial,
        immediate_code=immediate_code,
        why_level=why_level,
        current_why_question=current_why_question,
        previous_why_answer=previous_why_answer,
        known_fields=known_fields,
    )
    pending = [q for q in pool if q.get("id") not in answered]
    batch = pending[: max(1, batch_size)]

    def _shape(q: dict) -> dict[str, Any]:
        soru = str(q.get("soru", "") or "")
        u = _enrich_hitl_ui(soru, q)
        return {
            "id": q["id"],
            "source": q.get("source", "why_probe"),
            "hsg_hint": q.get("hsg245", ""),
            "code": q.get("code", ""),
            "cause_desc": q.get("cause_desc", ""),
            "question_tr": soru,
            "question_en": soru,
            "yönler": q.get("yönler") or {},
            "why_level": q.get("why_level", why_level),
            "response_mode": u.get("response_mode", "yes_no_unknown"),
            "choice_options": u.get("choice_options") or [],
            "choice_options_en": u.get("choice_options_en") or [],
            "choice_multi": bool(u.get("choice_multi", False)),
        }

    return {
        "questions": [_shape(q) for q in batch],
        "total_pool": len(pool),
        "remaining_after_batch": max(0, len(pending) - len(batch)),
        "done": len(pending) == 0,
    }
