#!/usr/bin/env python3
"""
================================================================================
حادثة السقوط من الارتفاع - اختبار النظام الكامل (النسخة العربية)
FALL FROM HEIGHT INCIDENT - FULL SYSTEM TEST (ARABIC VERSION)
================================================================================

وصف الحادثة:
  سقط عامل بناء من ارتفاع 6 أمتار من السقالة، وأصيب بجروح خطيرة.
  لم يكن العامل يرتدي حزام الأمان، وكانت درابزينات السقالة غير مكتملة.
  تم نقل العامل إلى قسم الطوارئ بكسر في العمود الفقري ونزيف داخلي.

EXPECTED OUTPUT:
  - Language: Arabic (RTL)
  - Report: All content in Arabic
  - HTML: dir="rtl" lang="ar"
  - DOCX: RTL paragraph direction

RUN:
  python tests/test_fall_from_height_arabic.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# بيانات الحادثة - السقوط من الارتفاع (باللغة العربية)
# ============================================================================

INCIDENT_DATA = """
تقرير الحادثة - السقوط من الارتفاع

التاريخ: 18 فبراير 2026، الوقت: 10:35
الموقع: موقع البناء - منطقة السقالة في الطابق الرابع
المُبلِّغ: مدير الموقع - محمد الأحمدي

وصف الحادثة:
سقط عامل تجميع السقالة حسن محمد (32 عاماً) من السقالة على ارتفاع 
ما يقارب 6 أمتار واصطدم بالأرض. أُصيب العامل بجروح بالغة الخطورة 
ونُقل إلى المستشفى بسيارة إسعاف.

الجدول الزمني للحادثة:
- 08:00 - بدأ العامل وردية العمل، وكُلّف بتجميع السقالة في الطابق الرابع
- 09:30 - جاري تجميع منصة السقالة
- 10:30 - فقد العامل توازنه أثناء العمل على حافة السقالة
- 10:35 - سقط من ارتفاع 6 أمتار إلى مستوى الأرض
- 10:37 - هرع زملاؤه للمساعدة واتصلوا بالإسعاف
- 10:42 - تم تقديم الإسعافات الأولية (واعٍ لكنه مصاب بجروح بالغة)
- 10:55 - وصلت سيارة الإسعاف ونُقل إلى المستشفى
- 11:20 - تقرير المستشفى: كسر في الفقرة القطنية L2، نزيف داخلي، حالة حرجة

الشخص المصاب:
- الاسم: حسن محمد
- العمر: 32 سنة
- المنصب: عامل تجميع سقالات
- الخبرة: 8 أشهر في أعمال السقالة
- الوردية: الوردية الصباحية (08:00 - 17:00)

تفاصيل الإصابة:
- كسر في الفقرة القطنية L2
- كسر في الحوض
- نزيف داخلي (الطحال)
- كدمات متعددة
- أُدخل العناية المركزة
- التشخيص: خطير، يحتاج علاجاً طويل الأمد

معدات السلامة:
✗ حزام الأمان: لم يُرتدَ
✗ الدرابزين: غير مكتمل (لم ينته التجميع)
✗ شبكة السلامة: غير موجودة
✓ خوذة السلامة: مرتداة
✓ أحذية السلامة: مرتداة
✗ حزام الأمان الكامل: لم يُرتدَ

حالة السقالة:
- عرض المنصة: 1.2 متر (معياري)
- الدرابزين: موجود على جانب واحد فقط
- حافة العمل: الجانب الخالي من الدرابزين
- فئة السقالة: سقالة من الأنابيب الفولاذية
- آخر فحص: قبل يومين (لم تُلاحَظ نقص الدرابزين)
- تصريح السقالة: متاح (لكن غير حالي)

النتائج الأولية للسبب الجذري:
1. لم يرتدِ العامل حزام الأمان (مخالفة للإجراءات)
2. بدأ العمل قبل اكتمال تجميع الدرابزين
3. نظام تصريح العمل لا يعمل بشكل صحيح (تقييم غير كافٍ للمخاطر)
4. لم يكن مسؤول السلامة موجوداً في الموقع
5. سجلات التدريب الوظيفي غير مكتملة (لم يُقدَّم تدريب العمل على الارتفاع)
6. لم تُجرَ مراقبة استخدام حزام الأمان
7. ضغط الإنتاج (تأخر المشروع، أُعطيت تعليمات بالإنهاء السريع)

شهادات الشهود:
- علي الدرع (عامل): "كان حسن يعمل بدون حزام أمان. الجميع يفعل ذلك.
  كان المشرف يستعجلنا، لذا انتقلنا إلى الجانب الذي لا يوجد فيه درابزين."
- محمد الكرا (مقدم): "كان من المقرر تركيب الدرابزين غداً. كان يجب
  إنهاء تجميع المنصة اليوم. قال المشرف أنهِ بسرعة."
- مدير الموقع: "لم أعلم أن الدرابزين كان غير مكتمل. العمال يعرفون 
  أنهم يجب أن يرتدوا أحزمة الأمان."

العوامل الإدارية:
- تأخر المشروع 3 أسابيع
- ضغط العميل: طلب "إتمام سريع"
- اجتماعات السلامة: لم تُعقد منذ شهرين
- تقييم المخاطر: عمره 6 أشهر (لم يُحدَّث)
- سجلات التدريب الوظيفي: غير مكتملة / غير منتظمة
- تكرار الفحص: مرة في الأسبوع (غير كافٍ)

الإجراءات الفورية:
1. إيقاف جميع أعمال الارتفاع
2. إعادة فحوصات السقالة
3. إلزامية ارتداء حزام الأمان
4. عقد إحاطة سلامة
5. مراجعة جدول المشروع
"""


# ============================================================================
# تنفيذ الاختبار
# ============================================================================

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def main():
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print_header("حادثة السقوط من الارتفاع - اختبار النظام الكامل (النسخة العربية)")
    print_info(f"بدء الاختبار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("الحادثة: سقوط من سقالة في موقع بناء (ارتفاع 6 متر)")

    results = {"timestamp": timestamp, "steps": {}}

    # الخطوة 1: فحص البيئة
    print_header("الخطوة 1: فحص البيئة")
    try:
        assert os.getenv("OPENROUTER_API_KEY"), "مفتاح API غير موجود"
        print_success("مفتاح API متاح")
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"خطأ في البيئة: {e}")
        results["steps"]["environment"] = "FAILED"
        return results

    # الخطوة 2: OverviewAgent
    print_header("الخطوة 2: OverviewAgent - التقييم الأولي")
    try:
        agent = OverviewAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"الرقم المرجعي: {part1.get('ref_no')}")
        print_success(f"نوع الحادثة: {part1.get('incident_type')}")
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"خطأ في OverviewAgent: {e}")
        results["steps"]["overview"] = "FAILED"
        return results

    # الخطوة 3: AssessmentAgent
    print_header("الخطوة 3: AssessmentAgent - تقييم الخطورة")
    try:
        agent = AssessmentAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        print_success(f"مستوى الخطورة: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"خطأ في AssessmentAgent: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results

    # الخطوة 4: RootCauseAgentV2
    print_header("الخطوة 4: RootCauseAgentV2 - تحليل السبب الجذري")
    try:
        agent = RootCauseAgentV2()
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        root_causes = part3.get("final_root_causes", [])
        print_success(f"الأسباب الجذرية المكتشفة: {len(root_causes)}")
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = rc.get("root_cause_title", "N/A")[:60]
            print_info(f"[{i}] {code} - {title}")

        json_path = f"outputs/fall_from_height_arabic_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"تم حفظ JSON: {json_path}")

        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
        results["json_path"] = json_path
    except Exception as e:
        print_error(f"خطأ في RootCauseAgentV2: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results

    # الخطوة 5: SkillBasedDocxAgent
    print_header("الخطوة 5: SkillBasedDocxAgent - إنشاء التقرير")
    try:
        agent = SkillBasedDocxAgent()
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_path = f"outputs/{ref_no}_fall_from_height_ARABIC.docx"

        investigation_data = {
            "part1": part1,
            "part2": part2,
            "part3_rca": part3
        }

        result_path = agent.generate_report(investigation_data, docx_path)
        html_path = result_path.replace('.docx', '.html')

        if Path(result_path).exists():
            size_kb = Path(result_path).stat().st_size / 1024
            print_success(f"تم إنشاء DOCX: {size_kb:.1f} KB")
            print_info(f"الملف: {result_path}")

        if Path(html_path).exists():
            html_kb = Path(html_path).stat().st_size / 1024
            print_success(f"تم إنشاء HTML: {html_kb:.1f} KB")
            print_info(f"الملف: {html_path}")
            # Quick RTL check
            html_content = Path(html_path).read_text(encoding='utf-8')
            rtl_ok = 'dir="rtl"' in html_content
            lang_ok = 'lang="ar"' in html_content
            print_success(f"RTL direction: {'✓' if rtl_ok else '✗'}")
            print_success(f"lang=\"ar\": {'✓' if lang_ok else '✗'}")

        results["steps"]["docx"] = "PASSED"
        results["docx_path"] = result_path
        results["html_path"] = html_path
    except Exception as e:
        print_error(f"خطأ في SkillBasedDocxAgent: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["docx"] = "FAILED"
        return results

    # الملخص
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])

    print_header("ملخص الاختبار")
    print_info(f"الوقت المنقضي: {elapsed:.1f} ثانية")
    print_info(f"الخطوات الناجحة: {passed}/{total}")

    if passed == total:
        print_success("🎉 اجتازت جميع الاختبارات!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ فشلت {total - passed} اختبارات")
        results["overall"] = "FAILED"

    print("\n📄 الملفات المُنشأة:")
    if "docx_path" in results:
        print(f"   DOCX: {results['docx_path']}")
    if "html_path" in results:
        print(f"   HTML: {results['html_path']}")
    if "json_path" in results:
        print(f"   JSON: {results['json_path']}\n")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
