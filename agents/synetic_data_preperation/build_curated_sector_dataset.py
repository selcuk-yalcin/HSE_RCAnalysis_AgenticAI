#!/usr/bin/env python3
"""
Curated multi-sector 5-Why dataset for DSPy MIPROv2.

Sources:
  - User-provided cross-industry good examples (manufacturing, SaaS, healthcare, …)
  - BARSEL-aligned Turkish HSE scenarios (petrol, kimya, elektrik, inşaat)
  - Negative (bad) chains: circularity, generic labels, solution language, D4-only snap

Outputs:
  hse_5why_train.jsonl  (70%)
  hse_5why_dev.jsonl    (15%)
  hse_5why_test.jsonl   (15%)
  hse_dataset_metadata.json

Usage:
  python agents/synetic_data_preperation/build_curated_sector_dataset.py
  python agents/synetic_data_preperation/build_curated_sector_dataset.py --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

OUTPUT_DIR = Path(__file__).resolve().parent


def _chain(steps: Sequence[Tuple[str, str]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, (question, answer) in enumerate(steps):
        out.append(
            {
                "depth": i + 1,
                "question": question,
                "answer": answer,
                "is_root_cause": i == len(steps) - 1,
            }
        )
    return out


def _ex(
    *,
    incident_description: str,
    sector: str,
    why_chain: List[Dict[str, Any]],
    root_cause: str,
    corrective_actions: List[str],
    contributing_factors: Optional[List[str]] = None,
    severity: str = "Moderate",
    language: str = "en",
    barsel_codes: Optional[List[str]] = None,
    bands: Optional[List[str]] = None,
    is_negative_example: bool = False,
    negative_reason: Optional[str] = None,
    example_id: str = "",
) -> Dict[str, Any]:
    return {
        "example_id": example_id,
        "incident_description": incident_description,
        "sector": sector,
        "language": language,
        "why_chain": why_chain,
        "root_cause": root_cause,
        "contributing_factors": contributing_factors or [],
        "corrective_actions": corrective_actions,
        "severity": severity,
        "barsel_codes": barsel_codes or [],
        "bands": bands or [],
        "is_negative_example": is_negative_example,
        "negative_reason": negative_reason,
    }


def good_examples() -> List[Dict[str, Any]]:
    """High-quality cross-sector chains (depth 5, system-level root, evidence-based)."""
    return [
        # ── 1. Manufacturing: CNC downtime (user example) ──
        _ex(
            example_id="good_mfg_cnc_downtime",
            sector="manufacturing / automotive",
            language="en",
            barsel_codes=["B2.3", "D6.1"],
            bands=["B", "D"],
            incident_description=(
                "A production line in an automotive parts factory experienced recurring unplanned "
                "CNC milling machine stops, costing an estimated $15,000 per incident in lost output."
            ),
            why_chain=_chain([
                (
                    "Why does the CNC milling machine stop unexpectedly?",
                    "The thermal overload protection trips due to excessive motor temperature during continuous operation.",
                ),
                (
                    "Why does the motor overheat?",
                    "Coolant flow is insufficient to dissipate heat during continuous milling cycles.",
                ),
                (
                    "Why is coolant flow insufficient?",
                    "The coolant filter is partially clogged with metal shavings, restricting flow by approximately 40%.",
                ),
                (
                    "Why is the filter clogged?",
                    "The filter has not been replaced in 6 months, well past its 2-month service interval.",
                ),
                (
                    "Why was the filter not replaced on schedule?",
                    "There is no preventive maintenance schedule for coolant system components; replacements only happen after breakdowns.",
                ),
            ]),
            root_cause=(
                "Absence of a preventive maintenance schedule for coolant system components, "
                "causing deferred filter replacement until failure."
            ),
            contributing_factors=[
                "No visual coolant flow indicator on the machine panel.",
                "Maintenance backlog prioritized production uptime over PM tasks.",
            ],
            corrective_actions=[
                "Implement PM checklist with coolant filter replacement every 8 weeks.",
                "Add real-time coolant flow gauge with low-flow alarm.",
            ],
            severity="Production loss / near-miss to equipment damage",
        ),
        # ── 2. Software: payment outage ──
        _ex(
            example_id="good_saas_payment_outage",
            sector="software / SaaS",
            language="en",
            barsel_codes=["D7.2", "D4.3"],
            bands=["D"],
            incident_description=(
                "A SaaS company's payment processing service returned 500 errors for 47 minutes "
                "during peak hours, blocking all checkout transactions."
            ),
            why_chain=_chain([
                (
                    "Why did the payment API return 500 errors?",
                    "The database connection pool was exhausted; all 50 connections were held by long-running queries.",
                ),
                (
                    "Why were queries running so long?",
                    "A new report query scanned 12 million rows without an index on the created_at column.",
                ),
                (
                    "Why was there no index on created_at?",
                    "The migration adding the report feature did not include index creation and passed code review without a database review.",
                ),
                (
                    "Why was there no database review?",
                    "The team has no mandatory database review step for migrations touching tables with more than 1 million rows.",
                ),
                (
                    "Why is there no such process?",
                    "Database performance guidelines exist in a wiki but are not enforced in the CI/CD pipeline or PR checklist.",
                ),
            ]),
            root_cause=(
                "Database performance guidelines are documented but not enforced in CI/CD or PR workflows "
                "for high-volume table migrations."
            ),
            corrective_actions=[
                "Add CI check flagging migrations on large tables without index changes.",
                "Require 'database review' label on migration PRs affecting tables >1M rows.",
            ],
            severity="Major service outage",
        ),
        # ── 3. E-commerce: cart abandonment ──
        _ex(
            example_id="good_ecommerce_cart_abandon",
            sector="e-commerce / retail",
            language="en",
            barsel_codes=["D7.5", "D10.6"],
            bands=["D"],
            incident_description=(
                "Checkout abandonment rate increased from 35% to 58% over 8 weeks, "
                "resulting in approximately $120K lost monthly revenue."
            ),
            why_chain=_chain([
                (
                    "Why are customers abandoning checkout?",
                    "Session recordings show 73% of drop-offs occur at the shipping cost reveal on step 3 of 5.",
                ),
                (
                    "Why does the shipping cost cause drop-offs?",
                    "A new carrier contract increased standard shipping from $4.99 to $11.99; customers see the price only at checkout.",
                ),
                (
                    "Why do customers only see the cost at checkout?",
                    "Shipping is calculated after entering a delivery address on step 3, with no upfront estimate on product or cart pages.",
                ),
                (
                    "Why was no upfront estimate built into the original flow?",
                    "Checkout was designed when shipping was flat-rate $4.99, so early cost communication was not perceived as necessary.",
                ),
                (
                    "Why wasn't checkout redesigned when the carrier contract changed?",
                    "The product team treated the carrier switch as a backend-only change; no UX review is triggered by pricing changes affecting customer experience.",
                ),
            ]),
            root_cause=(
                "No cross-functional UX review process when backend pricing changes affect the customer checkout experience."
            ),
            corrective_actions=[
                "Add shipping cost estimator on product and cart pages via IP geolocation.",
                "Mandate UX review for any pricing change affecting checkout.",
            ],
            severity="Revenue impact",
        ),
        # ── 4. Healthcare: medication errors ──
        _ex(
            example_id="good_healthcare_med_errors",
            sector="healthcare",
            language="en",
            barsel_codes=["D3.1", "C2.4", "D7.1"],
            bands=["C", "D"],
            incident_description=(
                "Seven wrong-dosage medication errors were reported in the oncology ward over one quarter, "
                "up from one in the previous quarter."
            ),
            why_chain=_chain([
                (
                    "Why are wrong dosages being administered?",
                    "Nurses manually calculate doses from weight-based tables instead of using the electronic prescribing system.",
                ),
                (
                    "Why are doses calculated manually?",
                    "The electronic system frequently times out during peak hours (8-10 AM), forcing staff to use paper charts.",
                ),
                (
                    "Why does the system time out during peak hours?",
                    "Hospital network bandwidth was not upgraded when the oncology ward added 30 new connected devices last quarter.",
                ),
                (
                    "Why was the network not upgraded?",
                    "IT resource planning is annual during budget season, but ward equipment purchases are approved independently throughout the year.",
                ),
                (
                    "Why are equipment purchases not coordinated with IT?",
                    "There is no cross-departmental procurement policy requiring an IT infrastructure impact assessment before adding networked devices to any ward.",
                ),
            ]),
            root_cause=(
                "Missing cross-departmental procurement policy requiring IT infrastructure impact assessment "
                "before purchasing networked clinical devices."
            ),
            corrective_actions=[
                "Implement procurement policy with mandatory IT impact assessment.",
                "Upgrade oncology ward bandwidth with 50% headroom.",
            ],
            severity="Patient safety — serious",
        ),
        # ── 5. Customer support SLA breach ──
        _ex(
            example_id="good_b2b_support_sla",
            sector="B2B software / customer support",
            language="en",
            barsel_codes=["D7.5", "D7.2"],
            bands=["D"],
            incident_description=(
                "Average first-response time to support tickets increased from 2 hours to 11 hours, "
                "breaching SLA for 34% of enterprise accounts."
            ),
            why_chain=_chain([
                (
                    "Why are response times so long?",
                    "The support queue grew from 40 to 130 daily tickets while team size remained unchanged.",
                ),
                (
                    "Why did ticket volume triple?",
                    "About 60% of new tickets concern the same issue: users cannot export reports after the v4.2 update.",
                ),
                (
                    "Why is this known bug generating so many tickets?",
                    "The status page and in-app banner were not updated to inform users about the issue and expected fix timeline.",
                ),
                (
                    "Why was proactive communication not sent?",
                    "Engineering reported the bug in Slack, but support/comms were not notified because there is no automatic alert when critical bugs are flagged.",
                ),
                (
                    "Why is there no automatic cross-team alert?",
                    "There is no incident communication workflow connecting engineering bug tracking to customer-facing channels; teams operate in separate tools.",
                ),
            ]),
            root_cause=(
                "No incident communication workflow linking engineering critical-bug flags to support and customer comms channels."
            ),
            corrective_actions=[
                "Auto-notify support/comms when engineering flags critical bugs.",
                "Playbook: status page + in-app banner when bug affects 100+ users.",
            ],
            severity="SLA breach / customer churn risk",
        ),
        # ── 6. Logistics: shipping delays ──
        _ex(
            example_id="good_logistics_late_ship",
            sector="logistics / supply chain",
            language="en",
            barsel_codes=["D6.2", "D7.2"],
            bands=["D"],
            incident_description=(
                "22% of shipments to a key retail client arrived 1-3 days late, up from 4% last quarter; "
                "contract penalty threshold is 10%."
            ),
            why_chain=_chain([
                (
                    "Why are shipments arriving late?",
                    "Trucks depart the warehouse 2-4 hours behind the scheduled cutoff time.",
                ),
                (
                    "Why are trucks departing late?",
                    "Picking and packing for RetailCo orders takes 6 hours instead of the planned 3 hours.",
                ),
                (
                    "Why does picking take twice as long?",
                    "RetailCo's new SKU assortment is stored in a distant warehouse zone, doubling walking distance per order.",
                ),
                (
                    "Why are new SKUs stored in a distant zone?",
                    "Warehouse slotting is reviewed only annually; high-velocity new SKUs were placed in leftover slots far from the primary picking area.",
                ),
                (
                    "Why is slotting only reviewed annually?",
                    "The WMS does not support incremental zone-by-zone optimization; reslotting requires a full warehouse replan during annual inventory shutdown.",
                ),
            ]),
            root_cause=(
                "Warehouse management system lacks incremental reslotting capability, forcing annual-only slotting reviews "
                "and poor placement of high-velocity SKUs."
            ),
            corrective_actions=[
                "Upgrade WMS for incremental zone reslotting.",
                "Reslot RetailCo top 50 SKUs to primary picking zone immediately.",
            ],
            severity="Contract penalty risk",
        ),
        # ── 7. HR: engineering turnover ──
        _ex(
            example_id="good_hr_eng_turnover",
            sector="technology / HR",
            language="en",
            barsel_codes=["D7.1", "C3.2"],
            bands=["C", "D"],
            incident_description=(
                "Five of twelve platform-team engineers resigned in six months (42% turnover vs 12% company average)."
            ),
            why_chain=_chain([
                (
                    "Why did engineers leave?",
                    "Exit interviews cite lack of career growth and repetitive maintenance work as the primary reason.",
                ),
                (
                    "Why is work perceived as repetitive?",
                    "The team spends 70% of time on legacy maintenance and only 30% on new features, versus 50/50 on peer teams.",
                ),
                (
                    "Why is maintenance load so high?",
                    "The legacy system was built without automated tests or documentation, making every change slow and risky.",
                ),
                (
                    "Why has technical debt not been addressed?",
                    "Sprint planning is driven entirely by the product backlog; the engineering manager has no formal mechanism to reserve capacity for non-feature work.",
                ),
                (
                    "Why can't engineering reserve capacity for tech debt?",
                    "Product OKRs measure only feature delivery velocity, not engineering health metrics, so tech debt work has no organizational support.",
                ),
            ]),
            root_cause=(
                "Product OKRs exclude engineering health metrics (deploy frequency, change failure rate, tech debt ratio), "
                "leaving no organizational support for legacy modernization."
            ),
            corrective_actions=[
                "Add engineering health metrics to team OKRs.",
                "Reserve 20% sprint capacity for tech debt and test coverage.",
            ],
            severity="Organizational / retention",
        ),
        # ── 8. Marketing: landing page conversion drop ──
        _ex(
            example_id="good_marketing_conversion",
            sector="SaaS / marketing",
            language="en",
            barsel_codes=["D7.5", "D7.2"],
            bands=["D"],
            incident_description=(
                "Landing page conversion dropped from 4.2% to 1.8% within 3 weeks of a website redesign, "
                "cutting qualified leads from 840 to 360 per month."
            ),
            why_chain=_chain([
                (
                    "Why did conversion drop after the redesign?",
                    "Heatmaps show visitors scroll past the CTA; only 12% of visitors see the main call-to-action.",
                ),
                (
                    "Why do so few visitors see the CTA?",
                    "The new design moved the primary CTA below a 900px hero image and a testimonial section.",
                ),
                (
                    "Why was the CTA moved below the fold?",
                    "The design agency prioritized brand storytelling and visual impact over conversion-focused layout.",
                ),
                (
                    "Why did the agency prioritize brand over conversion?",
                    "The creative brief did not include performance benchmarks or conversion goals—only visual and brand guidelines.",
                ),
                (
                    "Why did the brief exclude performance requirements?",
                    "There is no cross-functional review for creative briefs; the brand team approved it without involving the growth team that owns conversion metrics.",
                ),
            ]),
            root_cause=(
                "No cross-functional review of creative briefs for high-traffic pages; growth/conversion requirements are omitted."
            ),
            corrective_actions=[
                "Add secondary CTA above the fold immediately.",
                "Require growth team co-sign on briefs with CTA visibility and conversion targets.",
            ],
            severity="Revenue / lead generation",
        ),
        # ── 9. Construction: budget overruns ──
        _ex(
            example_id="good_construction_budget",
            sector="construction",
            language="en",
            barsel_codes=["D8.3", "D7.1"],
            bands=["D"],
            incident_description=(
                "Four of five recent commercial projects exceeded budget by 15-25%, "
                "reducing average project margin from 18% to 4%."
            ),
            why_chain=_chain([
                (
                    "Why are projects over budget?",
                    "Material costs consistently exceed estimates by 12-20% across all four over-budget projects.",
                ),
                (
                    "Why are material estimates too low?",
                    "Estimators use a price database updated only once per year while material prices fluctuate quarterly.",
                ),
                (
                    "Why is the database updated only annually?",
                    "The update process is manual, takes three full days, and is deprioritized during busy estimating seasons.",
                ),
                (
                    "Why is the update manual?",
                    "Estimating software purchased in 2018 predates suppliers' modern API pricing systems; no integration was built.",
                ),
                (
                    "Why was no integration built?",
                    "IT budget is allocated exclusively to field operations tools; back-office estimating software has no dedicated technology improvement budget or owner.",
                ),
            ]),
            root_cause=(
                "No dedicated back-office technology budget or owner for estimating systems, "
                "preventing integration with supplier pricing APIs."
            ),
            corrective_actions=[
                "Create back-office technology budget with owner accountability.",
                "Integrate estimating software with top-3 supplier pricing APIs.",
            ],
            severity="Financial / project delivery",
        ),
        # ── 10. EdTech: low course completion ──
        _ex(
            example_id="good_edtech_completion",
            sector="EdTech / online learning",
            language="en",
            barsel_codes=["D7.2", "C2.1"],
            bands=["C", "D"],
            incident_description=(
                "Average course completion rate is 11% versus a 35% industry benchmark; "
                "68% of drop-offs occur between modules 2 and 3."
            ),
            why_chain=_chain([
                (
                    "Why do students drop off at module 3?",
                    "Module 3 is the first graded assignment; 54% of students who attempt it score below the passing threshold.",
                ),
                (
                    "Why do most students fail the first graded assignment?",
                    "The assignment requires skills demonstrated in video lectures but never practiced in modules 1-2.",
                ),
                (
                    "Why is there no practice before grading?",
                    "Modules 1-2 are lecture-only with no interactive exercises; the course template omits practice before graded work.",
                ),
                (
                    "Why does the template skip practice activities?",
                    "The template was designed for instructor-led classrooms where the instructor provides live practice between lectures.",
                ),
                (
                    "Why was the template never adapted for self-paced online delivery?",
                    "The platform scaled from 5 to 200+ courses by cloning the original template; there is no instructional design review for new courses.",
                ),
            ]),
            root_cause=(
                "No instructional design review process when cloning course templates for self-paced online delivery."
            ),
            corrective_actions=[
                "Add practice activities before first graded module in the template.",
                "Establish instructional design review for all new course launches.",
            ],
            severity="Learning outcome / product quality",
        ),
        # ── Turkish HSE: kontaktör / thermal (BARSEL B2 + D6) ──
        _ex(
            example_id="good_tr_kontaktor_termal",
            sector="imalat / üretim hattı",
            language="tr",
            barsel_codes=["B2.3", "D6.1", "D6.7"],
            bands=["B", "D"],
            incident_description=(
                "Üretim hattındaki bir ekipmanda kontaktörün yapışık kalması sonucu ısı yükselmesi ve dumanlama "
                "meydana gelmiş; rezistanslarda yanık olmamasına rağmen koruma mekanizması devreye girmemiştir."
            ),
            why_chain=_chain([
                (
                    "Neden kontaktör yapışık kalarak ısı yükselmesi ve dumanlama meydana geldi?",
                    "Kontaktörün zamanla eskimesi ve uzun süreli yüksek sıcaklıkta çalışması nedeniyle yapışık kaldı.",
                ),
                (
                    "Kontaktörün yapışık kalmasına hangi alt mekanizma yol açtı?",
                    "Kontaktörün kritik arıza modu için periyodik kontrol ve aşınma izleme bakım planına dahil edilmemişti.",
                ),
                (
                    "Neden periyodik kontrol plana dahil değildi?",
                    "Bakım stratejisi olay bazlıydı; son bakımda çentik eksikliği tespit edilmemiş ve kritik mod göz ardı edilmişti.",
                ),
                (
                    "Neden bakımda çentik eksikliği tespit edilmedi?",
                    "Bakım kontrol listesinde kontaktör mekanik durumu ve yardımcı kontak bağlantıları için spesifik madde yoktu.",
                ),
                (
                    "Neden kontrol listesinde bu maddeler yoktu?",
                    "Ekipman için risk temelli bakım analizi yapılmamış; bakım kapsamı üretici önerisi dışında güncellenmemişti.",
                ),
            ]),
            root_cause=(
                "Kritik ekipman için risk temelli bakım analizinin yapılmaması ve bakım kapsamının "
                "kritik arıza modlarını kapsayacak şekilde güncellenmemesi."
            ),
            contributing_factors=[
                "Yardımcı kontak sigortalarının çentik ile bağlı olmaması.",
                "Üretim baskısı nedeniyle planlı duruşların ertelenmesi.",
            ],
            corrective_actions=[
                "Kontaktör ve yardımcı kontaklar için PM kontrol listesi güncelle.",
                "Risk temelli bakım analizi ile kritik modlar için periyodik kontrol tanımla.",
            ],
            severity="Yüksek potansiyelli olay (MPT)",
        ),
        # ── Turkish: LOTO / rotating equipment (petrol & gaz) ──
        _ex(
            example_id="good_tr_loto_pump",
            sector="petrol & gaz",
            language="tr",
            barsel_codes=["A1.1", "D7.2", "D4.3"],
            bands=["A", "D"],
            incident_description=(
                "Bakım teknisyeni, tıkalı bir pompadaki blokajı temizlerken pompa beklenmedik şekilde çalıştı "
                "ve eli gövde ile dönen emme kanadı arasında sıkışarak ezilme yaralanması yaşadı."
            ),
            why_chain=_chain([
                (
                    "Neden teknisyenin eli pompa içinde sıkıştı?",
                    "Pompa, teknisyen gövde içinde çalışırken beklenmedik şekilde devreye girdi.",
                ),
                (
                    "Neden pompa beklenmedik şekilde devreye girdi?",
                    "Enerji kesme-kilitleme (LOTO) uygulanmamış veya doğrulanmamıştı.",
                ),
                (
                    "Neden LOTO uygulanmadı veya doğrulanmadı?",
                    "Bu pompa ve görev için LOTO prosedürü belirsizdi; ikinci yetkili doğrulama adımı zorunlu değildi.",
                ),
                (
                    "Neden prosedür belirsiz ve doğrulama zorunlu değildi?",
                    "Mevcut LOTO prosedürü geneldi; dönen ekipmanda blokaj temizliği için görev-spesifik enerji izolasyonu tanımlanmamıştı.",
                ),
                (
                    "Neden görev-spesifik LOTO güncellenmedi?",
                    "Kritik güvenlik prosedürlerinin periyodik gözden geçirme ve ekipman/tehdit değişimine göre güncelleme süreci yoktu.",
                ),
            ]),
            root_cause=(
                "Kritik güvenlik prosedürleri (LOTO) için periyodik gözden geçirme ve görev-spesifik "
                "özelleştirme sürecinin bulunmaması."
            ),
            corrective_actions=[
                "Dönen ekipman LOTO prosedürünü görev-spesifik olarak revize et.",
                "İki kişili zorunlu LOTO doğrulaması uygula.",
            ],
            severity="Kayıp zamanlı yaralanma (LTI)",
        ),
        # ── Turkish: kimya tesisi sızıntı ──
        _ex(
            example_id="good_tr_kimya_sizinti",
            sector="kimya tesisi",
            language="tr",
            barsel_codes=["B2.1", "D6.1", "D4.3"],
            bands=["B", "D"],
            incident_description=(
                "Solvent transfer hattında flanş bağlantısından küçük sızıntı tespit edildi; operatör "
                "bölgede KKD olmadan kısa süre kaldı ve baş dönmesi şikayetiyle sağlık birimine yönlendirildi."
            ),
            why_chain=_chain([
                (
                    "Neden operatör solvent buharına maruz kaldı?",
                    "Flanş bağlantısından sürekli küçük sızıntı vardı ve bölgede yeterli havalandırma sağlanmamıştı.",
                ),
                (
                    "Neden flanştan sızıntı devam ediyordu?",
                    "Flanş contası yaşlanmış ve son haftalarda tork kontrolü yapılmamıştı.",
                ),
                (
                    "Neden tork kontrolü yapılmadı?",
                    "Haftalık hattı tarama listesinde flanş tork kontrolü maddesi yoktu.",
                ),
                (
                    "Neden tarama listesinde flanş torku yoktu?",
                    "Hat için son risk değerlendirmesinde küçük sızıntı senaryosu düşük öncelikli sayılmış ve PM kapsamına alınmamıştı.",
                ),
                (
                    "Neden sızıntı senaryosu PM kapsamına alınmadı?",
                    "Proses hatları için risk değerlendirme çıktılarının bakım planlarına aktarımı için zorunlu bir köprü süreç tanımlı değildi.",
                ),
            ]),
            root_cause=(
                "Risk değerlendirme çıktılarının bakım planlarına aktarımını zorunlu kılan "
                "köprü sürecin tanımlı olmaması."
            ),
            corrective_actions=[
                "Flanş tork kontrolünü haftalık tarama listesine ekle.",
                "Risk değerlendirme–bakım planı aktarım kontrol listesi oluştur.",
            ],
            severity="Maruziyet / sağlık etkisi",
        ),
        # ── Mining: roof fall near-miss ──
        _ex(
            example_id="good_mining_roof_support",
            sector="madencilik",
            language="en",
            bands=["B", "D"],
            barsel_codes=["B1.2", "D6.1", "D4.3"],
            incident_description=(
                "In an underground coal section, a roof bolt plate detached during bolting operations; "
                "the operator escaped injury but production was halted for 6 hours."
            ),
            why_chain=_chain([
                (
                    "Why did the roof bolt plate detach during bolting?",
                    "The bolt encountered a void in the rock strata and lost anchorage torque.",
                ),
                (
                    "Why was there a void not detected before bolting?",
                    "Pre-bolt ground scanning was skipped in this panel due to time pressure.",
                ),
                (
                    "Why was ground scanning skipped?",
                    "The shift target prioritized meters bolted over the mandatory scan-every-3-meters rule.",
                ),
                (
                    "Why did production targets override the scanning rule?",
                    "Weekly KPIs reward advance rate without a balanced metric for ground support compliance.",
                ),
                (
                    "Why are KPIs imbalanced?",
                    "The mine's performance management system was not updated after the last roof-fall near-miss to include support-compliance weighting.",
                ),
            ]),
            root_cause=(
                "Performance management KPIs reward advance rate without weighting ground-support compliance, "
                "encouraging skipping of mandatory pre-bolt scanning."
            ),
            corrective_actions=[
                "Rebalance KPIs to include ground-scan compliance.",
                "Enforce scan-every-3-meters with automatic work-stop interlock.",
            ],
            severity="Near-miss / high potential",
        ),
        # ── Food processing: foreign body ──
        _ex(
            example_id="good_food_foreign_body",
            sector="gıda işleme",
            language="en",
            barsel_codes=["B2.3", "D6.1", "D7.2"],
            bands=["B", "D"],
            incident_description=(
                "A metal fragment was found in a packaged ready-meal during customer complaint investigation; "
                "traceability pointed to a worn mixer blade in the preparation line."
            ),
            why_chain=_chain([
                (
                    "Why was a metal fragment present in the packaged meal?",
                    "A fragment detached from a worn mixer blade during the preparation step.",
                ),
                (
                    "Why was the mixer blade worn enough to shed metal?",
                    "The blade had exceeded its recommended service life by 4 months without replacement.",
                ),
                (
                    "Why was the blade not replaced on time?",
                    "The preventive maintenance schedule for mixer blades was not linked to production run-hours counters.",
                ),
                (
                    "Why was maintenance not linked to run-hours?",
                    "When the line was upgraded, run-hour telemetry was installed but not integrated into the CMMS work-order triggers.",
                ),
                (
                    "Why was telemetry not integrated into CMMS?",
                    "Capital projects hand over equipment to operations without a mandatory digital-integration checklist for maintenance systems.",
                ),
            ]),
            root_cause=(
                "No mandatory digital-integration checklist when capital projects hand equipment to operations, "
                "leaving CMMS disconnected from run-hour telemetry."
            ),
            corrective_actions=[
                "Integrate mixer run-hours into CMMS PM triggers.",
                "Add capital-project handover checklist for maintenance system integration.",
            ],
            severity="Product safety / recall risk",
        ),
        # ── Electrical: arc flash near-miss ──
        _ex(
            example_id="good_electrical_arc_flash",
            sector="elektrik / enerji",
            language="tr",
            barsel_codes=["A1.1", "B1.1", "D7.2"],
            bands=["A", "B", "D"],
            incident_description=(
                "Orta gerilim panosunda yük ayırıcısı kapatılırken ark flaşı oluştu; teknisyen pano önünde "
                "duruyordu ancak KKD ve çalışma izni prosedürü uygulandığı için yaralanma olmadı."
            ),
            why_chain=_chain([
                (
                    "Neden ark flaşı oluştu?",
                    "Ayırıcı kontaklar aşınmış ve kapanma sırasında kısa süreli ark oluştu.",
                ),
                (
                    "Neden kontaklar aşınmış durumdaydı?",
                    "Panel için kontak durumu kontrolü son iki yılda yapılmamıştı.",
                ),
                (
                    "Neden kontak kontrolü yapılmadı?",
                    "OG panolar için periyodik kontak muayenesi bakım planında tanımlı değildi.",
                ),
                (
                    "Neden bakım planında tanımlı değildi?",
                    "Enerji dağıtım ekipmanı envanteri güncellenmiş ancak bakım stratejisi revizyonu tetiklenmemişti.",
                ),
                (
                    "Neden envanter güncellemesi bakım revizyonunu tetiklemedi?",
                    "Envanter değişiklikleri ile bakım stratejisi güncellemesi arasında zorunlu bağlantı süreci yoktu.",
                ),
            ]),
            root_cause=(
                "Enerji ekipmanı envanter değişikliklerinin bakım stratejisi revizyonunu otomatik "
                "tetikleyen sürecin bulunmaması."
            ),
            corrective_actions=[
                "OG panolar için kontak muayenesini bakım planına ekle.",
                "Envanter–bakım stratejisi değişiklik köprüsü tanımla.",
            ],
            severity="Yüksek potansiyelli olay (MPT)",
        ),
        # ── Warehouse: forklift (existing quality pattern) ──
        _ex(
            example_id="good_warehouse_forklift",
            sector="depo / lojistik",
            language="en",
            barsel_codes=["B2.3", "D6.1", "D7.2"],
            bands=["B", "D"],
            incident_description=(
                "A forklift collided with a pedestrian in the warehouse, resulting in a fractured leg."
            ),
            why_chain=_chain([
                (
                    "Why did the forklift collide with the pedestrian?",
                    "The driver did not see the pedestrian due to a blind spot and the pedestrian was not aware of the approaching forklift.",
                ),
                (
                    "Why did the driver not see the pedestrian and why was the pedestrian unaware?",
                    "The forklift reverse alarm was not functioning and the pedestrian walked in an area without designated walkways.",
                ),
                (
                    "Why was the reverse alarm not functioning?",
                    "The alarm was faulty and had not been identified during the pre-shift inspection.",
                ),
                (
                    "Why was the faulty alarm not identified during pre-shift inspection?",
                    "The checklist did not include a functional check of the reverse alarm.",
                ),
                (
                    "Why was the reverse alarm check missing from the checklist?",
                    "Equipment inspection procedures were outdated and not revised when new safety-critical features were added to the fleet.",
                ),
            ]),
            root_cause=(
                "Outdated equipment inspection procedures missing checks for safety-critical features such as reverse alarms."
            ),
            corrective_actions=[
                "Update pre-shift checklists to include all safety alarms.",
                "Establish designated pedestrian walkways in high-traffic zones.",
            ],
            severity="Serious injury",
        ),
        # ── Petrol: oil on grating slip ──
        _ex(
            example_id="good_petrol_oil_grating",
            sector="petrol & gaz",
            language="en",
            barsel_codes=["B2.1", "D3.1"],
            bands=["B", "D"],
            incident_description=(
                "An operator slipped on oil accumulated on grating during a pump skid routine check, "
                "sustaining a sprained ankle."
            ),
            why_chain=_chain([
                (
                    "Why did the operator slip?",
                    "A thin oil layer had accumulated on the grating surface.",
                ),
                (
                    "Why had oil accumulated on the grating?",
                    "Oil seeped from a poorly sealed flange and the grating design prevented drainage.",
                ),
                (
                    "Why did the grating design prevent drainage?",
                    "A solid plate section beneath the flange caused pooling instead of drain-through.",
                ),
                (
                    "Why was a solid plate included in the design?",
                    "The original skid design prioritized structural support without assessing leak accumulation risk.",
                ),
                (
                    "Why was leak accumulation risk not assessed in design review?",
                    "The design review process did not require hazard assessment for minor leak pooling on solid surfaces.",
                ),
            ]),
            root_cause=(
                "Design review process lacking hazard assessment for fluid accumulation from minor leaks on solid surfaces."
            ),
            corrective_actions=[
                "Modify grating to allow drainage under flange connections.",
                "Add design review criterion for leak pooling on solid plates.",
            ],
            severity="Minor injury",
        ),
    ]


def bad_examples() -> List[Dict[str, Any]]:
    """Intentionally weak chains for contrast learning (MIPRO negative examples)."""
    return [
        _ex(
            example_id="bad_mfg_circular_thermal",
            sector="manufacturing / automotive",
            language="en",
            barsel_codes=["D4.3"],
            bands=["D"],
            is_negative_example=True,
            negative_reason=(
                "INVALID: (1) W2 repeats W1 (overheat/thermal overload circularity), "
                "(2) jumps to 'risk assessment missing' at W5 without intermediate evidence, "
                "(3) all steps collapse to generic D4.3 risk assessment."
            ),
            incident_description="CNC machine stops 3 times per week due to thermal overload trips.",
            why_chain=_chain([
                ("Why does the machine stop?", "Because the motor overheats and thermal protection trips."),
                ("Why does the motor overheat?", "Because thermal overload protection trips when the motor is too hot."),
                ("Why is the motor too hot?", "Because cooling is insufficient when the motor overheats."),
                ("Why is cooling insufficient?", "Because maintenance was not done."),
                ("Why was maintenance not done?", "Because risk assessment for the machine was not performed."),
            ]),
            root_cause="Risk assessment was not performed for the CNC machine.",
            corrective_actions=["Perform risk assessment.", "Train operators on heat issues."],
            severity="Production loss",
        ),
        _ex(
            example_id="bad_saas_human_error",
            sector="software / SaaS",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Generic 'human error' and 'lack of training' labels; no technical mechanism; "
                "answers are symptoms not organizational/system causes."
            ),
            incident_description="Payment API returned 500 errors for 47 minutes during peak checkout.",
            why_chain=_chain([
                ("Why did the API fail?", "Because the developer made a mistake."),
                ("Why did the developer make a mistake?", "Because of human error."),
                ("Why human error?", "Because they lacked training on databases."),
                ("Why lacked training?", "Because training program was insufficient."),
                ("Why insufficient?", "Because management did not prioritize training."),
            ]),
            root_cause="Human error and lack of training.",
            corrective_actions=["More training.", "Warn developers."],
            severity="Outage",
        ),
        _ex(
            example_id="bad_healthcare_careless_nurses",
            sector="healthcare",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Blames individual nurses ('careless'); W1 answer is already root-cause level; "
                "no system/IT/procurement mechanism explored."
            ),
            incident_description="Seven wrong-dosage medication errors in oncology ward last quarter.",
            why_chain=_chain([
                ("Why wrong dosages?", "Because nurses were careless."),
                ("Why careless?", "Because they did not double-check doses."),
                ("Why no double-check?", "Because they were busy."),
                ("Why busy?", "Because staffing was low."),
                ("Why low staffing?", "Because hospital did not hire enough nurses."),
            ]),
            root_cause="Nurses were careless and hospital understaffed.",
            corrective_actions=["Discipline nurses.", "Hire more nurses immediately."],
            severity="Patient safety",
        ),
        _ex(
            example_id="bad_construction_solution_language",
            sector="construction",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Answers use solution/future tense ('should integrate API', 'need to buy software'); "
                "5-Why requires past-state organizational facts, not recommendations."
            ),
            incident_description="Four of five commercial projects exceeded budget by 15-25%.",
            why_chain=_chain([
                ("Why over budget?", "Material costs were higher than estimates."),
                ("Why higher?", "Price database was outdated."),
                ("Why outdated?", "Team should update prices monthly but does not."),
                ("Why not update?", "They need to integrate supplier APIs."),
                ("Why no integration?", "Management should approve a software purchase."),
            ]),
            root_cause="Management should approve estimating software integration.",
            corrective_actions=["Buy new software.", "Management must approve budget."],
            severity="Financial",
        ),
        _ex(
            example_id="bad_logistics_all_d4_risk",
            sector="logistics / supply chain",
            language="en",
            barsel_codes=["D4.3", "D4.1", "D4.5"],
            bands=["D"],
            is_negative_example=True,
            negative_reason=(
                "INVALID: Every step mapped to risk assessment / permit / JSA gaps (D4 band only); "
                "ignores warehouse slotting, WMS, and operational mechanisms."
            ),
            incident_description="22% of shipments to RetailCo arrived 1-3 days late.",
            why_chain=_chain([
                ("Why late?", "Because risk assessment for shipping was inadequate."),
                ("Why inadequate?", "Because JSA for warehouse was not updated."),
                ("Why not updated?", "Because permit to work system was weak."),
                ("Why weak PTW?", "Because risk register did not include logistics."),
                ("Why not in risk register?", "Because formal risk assessment process was missing."),
            ]),
            root_cause="Formal risk assessment process was missing for logistics.",
            corrective_actions=["Update risk register.", "Conduct JSA."],
            severity="Contract risk",
        ),
        _ex(
            example_id="bad_tr_petrol_immediate_repeat",
            sector="petrol & gaz",
            language="tr",
            is_negative_example=True,
            negative_reason=(
                "INVALID (P1.24 circularity): W1 sorusu doğrudan nedeni içeriyor ve W1 cevabı "
                "immediate cause'u tekrar ediyor; zincir baştan kırık."
            ),
            incident_description="Operatör pompa sahasındaki grid üzerinde kayarak ayak burkulması yaşadı.",
            why_chain=_chain([
                (
                    "Neden operatör grid üzerinde kayarak ayak burkulması yaşadı hangi alt mekanizmayla gerçekleşti?",
                    "Operatör grid üzerinde biriken ince yağ tabakasında kaydı.",
                ),
                (
                    "Neden yağ birikmişti?",
                    "Çünkü operatör dikkatsizce yağlı alanda yürüdü.",
                ),
                (
                    "Neden dikkatsiz yürüdü?",
                    "Çünkü eğitim eksikti.",
                ),
                (
                    "Neden eğitim eksikti?",
                    "Çünkü eğitim planı yoktu.",
                ),
                (
                    "Neden plan yoktu?",
                    "Çünkü yönetim güvenliğe önem vermiyor.",
                ),
            ]),
            root_cause="Yönetim güvenliğe önem vermiyor.",
            corrective_actions=["Eğitim ver.", "Operatörü uyar."],
            severity="Minor injury",
        ),
        _ex(
            example_id="bad_tr_tarim_dikkatsizlik",
            sector="tarım",
            language="tr",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Her adım 'dikkatsizlik/eğitim eksikliği' belirtisi; fiziksel mekanizma yok; "
                "kök neden bireysel davranış."
            ),
            incident_description="Zeytin hasadında mevsimlik işçi merdivenden düşerek kol kırığı yaşadı.",
            why_chain=_chain([
                ("Neden kaza oldu?", "Çalışan dikkatsizdi."),
                ("Neden dikkatsizdi?", "Yeterli eğitim almamıştı."),
                ("Neden eğitim almamıştı?", "Eğitim programı yetersizdi."),
                ("Neden program yetersizdi?", "İK bütçesi kısıtlıydı."),
                ("Neden bütçe kısıtlıydı?", "Yönetim güvenliğe öncelik vermiyor."),
            ]),
            root_cause="Yönetim güvenlik kültürünü benimsememiş.",
            corrective_actions=["Daha fazla eğitim ver.", "Çalışanları uyar."],
            severity="Serious injury",
        ),
        _ex(
            example_id="bad_edtech_blame_students",
            sector="EdTech / online learning",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Attributes dropout to student laziness; no instructional-design or "
                "curriculum mechanism; root cause at individual level."
            ),
            incident_description="Course completion rate is 11%; 68% drop off between modules 2 and 3.",
            why_chain=_chain([
                ("Why drop off?", "Students are lazy and do not finish."),
                ("Why lazy?", "They do not study enough."),
                ("Why not study?", "They lack motivation."),
                ("Why lack motivation?", "Course is boring."),
                ("Why boring?", "Students do not engage with content."),
            ]),
            root_cause="Students are lazy and unmotivated.",
            corrective_actions=["Send reminder emails.", "Penalize incomplete students."],
            severity="Product quality",
        ),
        _ex(
            example_id="bad_ecommerce_vendor_blame",
            sector="e-commerce / retail",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Blames external carrier/vendor without internal process analysis; "
                "W3-W5 repeat 'carrier increased price' without deeper organizational cause."
            ),
            incident_description="Checkout abandonment rose from 35% to 58% after shipping price increase.",
            why_chain=_chain([
                ("Why abandonment?", "Shipping cost is too high at checkout."),
                ("Why too high?", "Carrier increased prices."),
                ("Why carrier increase?", "Because carrier contract changed."),
                ("Why contract change?", "Because new carrier charges more."),
                ("Why more charges?", "Because vendor pricing went up."),
            ]),
            root_cause="Vendor pricing went up.",
            corrective_actions=["Switch carrier.", "Negotiate with vendor."],
            severity="Revenue",
        ),
        _ex(
            example_id="bad_mining_supervisor_blame",
            sector="madencilik",
            language="tr",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Kök neden vardiya amirine atfedilmiş; destek sistemleri, KPI ve "
                "zemin tarama mekanizması araştırılmamış."
            ),
            incident_description="Yeraltı kömür bölümünde cevher damarında tavan boltu plakası koptu.",
            why_chain=_chain([
                ("Neden plaka koptu?", "Çünkü operatör hatalı deldi."),
                ("Neden hatalı deldi?", "Çünkü vardiya amiri acele ettirdi."),
                ("Neden acele ettirdi?", "Çünkü üretim hedefi vardı."),
                ("Neden hedef baskısı?", "Çünkü amir baskı yaptı."),
                ("Neden baskı yaptı?", "Çünkü amir kötü yönetici."),
            ]),
            root_cause="Vardiya amiri kötü yönetici.",
            corrective_actions=["Amiri cezalandır.", "Operatöre ek eğitim."],
            severity="Near-miss",
        ),
        _ex(
            example_id="bad_food_training_only",
            sector="gıda işleme",
            language="tr",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Düzeltici aksiyonlar yalnızca eğitim; W5 kök nedeni W4 ile aynı "
                "(parafraz döngüsü); bakım/CMMS/tesisat mekanizması yok."
            ),
            incident_description="Paketli hazır yemekte müşteri şikayeti sonrası metal parça bulundu.",
            why_chain=_chain([
                ("Neden metal parça vardı?", "Mikserde aşınmış bıçak parçası koptu."),
                ("Neden bıçak aşındı?", "Bakım yapılmadı."),
                ("Neden bakım yapılmadı?", "Bakım planı uygulanmadı."),
                ("Neden plan uygulanmadı?", "Bakım departmanı plana uymadı."),
                ("Neden uymadı?", "Bakım planı yeterince uygulanmıyordu."),
            ]),
            root_cause="Bakım planı yeterince uygulanmıyordu.",
            corrective_actions=["Personele eğitim ver.", "Planı tekrar anlat."],
            severity="Product safety",
        ),
        _ex(
            example_id="bad_hr_individual_performance",
            sector="technology / HR",
            language="en",
            is_negative_example=True,
            negative_reason=(
                "INVALID: Frames turnover as individual performance failure; no OKR, tech-debt, "
                "or organizational capacity mechanism."
            ),
            incident_description="Five of twelve platform engineers resigned in six months.",
            why_chain=_chain([
                ("Why resignations?", "Engineers were underperforming and unhappy."),
                ("Why underperforming?", "They could not deliver features fast enough."),
                ("Why slow delivery?", "They were not skilled enough."),
                ("Why not skilled?", "Hiring bar was too low."),
                ("Why low bar?", "Recruiting team made poor decisions."),
            ]),
            root_cause="Recruiting team made poor hiring decisions.",
            corrective_actions=["Replace recruiters.", "Performance-manage remaining engineers."],
            severity="Retention",
        ),
    ]


def stratified_split(
    examples: List[Dict[str, Any]],
    *,
    train_ratio: float = 0.70,
    dev_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Proportional pos/neg allocation per split (≈70/15/15, min 1 negative in dev+test)."""
    pos = [e for e in examples if not e.get("is_negative_example")]
    neg = [e for e in examples if e.get("is_negative_example")]
    rng = random.Random(seed)
    rng.shuffle(pos)
    rng.shuffle(neg)

    n = len(examples)
    n_neg = len(neg)
    n_train = max(1, int(n * train_ratio))
    n_dev = max(1, int(n * dev_ratio))
    n_test = max(1, n - n_train - n_dev)
    if n_train + n_dev + n_test > n:
        n_train = max(1, n - n_dev - n_test)

    neg_train = max(1, round(n_train * n_neg / n))
    neg_dev = max(1, round(n_dev * n_neg / n))
    neg_test = n_neg - neg_train - neg_dev
    while neg_test < 1 and neg_dev > 1:
        neg_dev -= 1
        neg_test += 1
    while neg_test < 0 and neg_train > 1:
        neg_train -= 1
        neg_test += 1

    pos_train = n_train - neg_train
    pos_dev = n_dev - neg_dev
    pos_test = n_test - neg_test

    train = pos[:pos_train] + neg[:neg_train]
    dev = pos[pos_train : pos_train + pos_dev] + neg[neg_train : neg_train + neg_dev]
    test = pos[pos_train + pos_dev :] + neg[neg_train + neg_dev :]
    rng.shuffle(train)
    rng.shuffle(dev)
    rng.shuffle(test)
    return train, dev, test


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_metadata(
    train: List[Dict],
    dev: List[Dict],
    test: List[Dict],
    *,
    seed: int,
) -> Dict[str, Any]:
    all_rows = train + dev + test
    n_pos = sum(1 for r in all_rows if not r.get("is_negative_example"))
    n_neg = sum(1 for r in all_rows if r.get("is_negative_example"))
    sectors = sorted({r.get("sector", "") for r in all_rows})
    return {
        "dataset_id": f"curated_sector_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "tenant_id": "default",
        "profile": "curated_sector",
        "source": "curated_cross_industry+barsel_hse",
        "language": "mixed_en_tr",
        "use_abs_context": False,
        "mode": "curated",
        "model": "n/a",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "random_seed": seed,
        "n_total": len(all_rows),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "sectors": sectors,
        "splits": {
            "train": len(train),
            "dev": len(dev),
            "test": len(test),
        },
        "barsel_taxonomy_ref": "rag_pipeline/data/processed/barsel_taxonomy_multilingual.json",
        "notes": (
            "10 cross-industry good examples from RCA best-practice literature; "
            "8 Turkish/English HSE scenarios aligned to BARSEL bands; "
            "12 negative examples for circularity, generic labels, D4-only, solution language."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build curated sector 5-Why MIPRO dataset")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_examples = good_examples() + bad_examples()
    train, dev, test = stratified_split(all_examples, seed=args.seed)

    write_jsonl(out_dir / "hse_5why_train.jsonl", train)
    write_jsonl(out_dir / "hse_5why_dev.jsonl", dev)
    write_jsonl(out_dir / "hse_5why_test.jsonl", test)

    meta = build_metadata(train, dev, test, seed=args.seed)
    (out_dir / "hse_dataset_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # DSPy-friendly JSON array (train only)
    (out_dir / "hse_dspy_trainset.json").write_text(
        json.dumps(train, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(train)} train, {len(dev)} dev, {len(test)} test examples to {out_dir}")
    print(f"Positive: {meta['n_positive']}, Negative: {meta['n_negative']}")
    print(f"Sectors ({len(meta['sectors'])}): {', '.join(meta['sectors'][:6])}…")


if __name__ == "__main__":
    main()
