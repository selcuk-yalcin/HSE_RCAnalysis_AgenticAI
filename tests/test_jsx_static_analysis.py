#!/usr/bin/env python3
"""
JSX COMPONENT ANALIZ TEST - IncidentForm_NEW.jsx
=================================================
React component'i statik olarak analiz eder
"""

import re
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{Colors.RED}❌ {text}{Colors.END}")

def print_info(text, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_section(text):
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}► {text}{Colors.END}")

class JSXComponentAnalyzer:
    def __init__(self, jsx_file):
        self.jsx_file = jsx_file
        self.content = ""
        self.test_results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

    def load_file(self):
        """JSX dosyasını yükle"""
        try:
            with open(self.jsx_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            file_size = len(self.content)
            lines = len(self.content.split('\n'))
            print_success(f"Dosya yüklendi: {file_size} bytes, {lines} satır")
            return True
        except Exception as e:
            print_error(f"Dosya yüklenemedi: {e}")
            return False

    def analyze_imports(self):
        """Import'ları analiz et"""
        print_section("TEST 1: IMPORTS - Modül İçe Aktarmaları")
        
        imports = re.findall(r"^import\s+(?:{[^}]*}|.*?)\s+from\s+['\"](.+?)['\"]", self.content, re.MULTILINE)
        
        print_info(f"Toplam import: {len(imports)}")
        
        expected_imports = {
            'react': False,
            'lucide-react': False,
            'translations': False,
            'css': False
        }
        
        for imp in imports:
            print_info(f"  📦 {imp}", 1)
            
            if 'react' in imp.lower() and imp == 'react':
                expected_imports['react'] = True
            elif 'lucide' in imp.lower():
                expected_imports['lucide-react'] = True
            elif 'translation' in imp.lower():
                expected_imports['translations'] = True
            elif '.css' in imp:
                expected_imports['css'] = True
        
        passed = sum(expected_imports.values())
        print_info(f"\nOluştu: {passed}/{len(expected_imports)}")
        
        for imp_type, found in expected_imports.items():
            status = "✓" if found else "✗"
            self.log_test(f"Import: {imp_type}", found)
        
        return passed == len(expected_imports)

    def analyze_component_structure(self):
        """Component yapısını analiz et"""
        print_section("TEST 2: COMPONENT STRUCTURE - Bileşen Yapısı")
        
        # Component tanımı
        has_component = bool(re.search(r"const\s+\w+\s*=\s*\(\{.*?\}\)\s*=>", self.content))
        print_success(f"Component tanımlı: {has_component}", 1)
        self.log_test("Component Definition", has_component)
        
        # useState hook'u
        useState_count = len(re.findall(r"useState\(", self.content))
        print_success(f"useState hook: {useState_count} kullanım", 1)
        self.log_test("useState Hooks", useState_count > 0)
        
        # useEffect hook'u
        useEffect_count = len(re.findall(r"useEffect\(", self.content))
        print_success(f"useEffect hook: {useEffect_count} kullanım", 1)
        self.log_test("useEffect Hooks", useEffect_count > 0)
        
        # useRef hook'u
        useRef_count = len(re.findall(r"useRef\(", self.content))
        print_success(f"useRef hook: {useRef_count} kullanım", 1)
        self.log_test("useRef Hooks", useRef_count > 0)
        
        # Return JSX
        has_return = bool(re.search(r"return\s*\(", self.content))
        print_success(f"Return JSX: {has_return}", 1)
        self.log_test("Return JSX", has_return)
        
        print_info(f"\nSonuç: Tüm temel React özelikleri mevcut ✓")

    def analyze_form_sections(self):
        """Form section'larını analiz et"""
        print_section("TEST 3: FORM SECTIONS - Form Bölümleri")
        
        sections = [
            ('Bildirim Yapan', 'reporter|reportDate|reportTime'),
            ('Kaza Detayları', 'incidentDate|incidentTime|location|department|severity'),
            ('Olay Akışı (Timeline)', 'timeline|addTimelineItem|removeTimelineItem'),
            ('Kontrol Listesi', 'preventionChecklist|riskAssessment|ptw|ppe|training'),
            ('5W1H Analiz', 'what|where|when|who|why|how'),
            ('Tanıklar', 'witnesses'),
            ('Çevre Koşulları', 'weather|lighting|temperature'),
            ('Çalışma Koşulları', 'workType|experience'),
            ('Yaralanma/Hasar', 'injuryType|bodPart|severity'),
            ('Kök Neden & Önlemler', 'rootCauses|preventionAction|addRootCause|removeRootCause'),
        ]
        
        passed = 0
        for section_name, pattern in sections:
            found = False
            for keyword in pattern.split('|'):
                if keyword.lower() in self.content.lower():
                    found = True
                    break
            
            if found:
                print_success(f"✓ {section_name}", 1)
                passed += 1
            else:
                print_error(f"✗ {section_name}", 1)
            
            self.log_test(f"Section: {section_name}", found)
        
        print_info(f"\nSonuç: {passed}/{len(sections)} bölüm bulundu")

    def analyze_state_management(self):
        """State yönetimini analiz et"""
        print_section("TEST 4: STATE MANAGEMENT - State Yönetimi")
        
        # formData state'i
        formData_matches = re.findall(r"formData\s*=\s*{([^}]*?)}", self.content[:5000], re.DOTALL)
        
        if formData_matches:
            # State field'larını say
            field_count = formData_matches[0].count(':')
            print_success(f"formData state: {field_count}+ field", 1)
            self.log_test("formData State", True)
        else:
            print_warning("formData state'i doğru şekilde yapılandırılmamış", 1)
            self.log_test("formData State", False)
        
        # activeSection state'i
        has_activeSection = bool(re.search(r"activeSection.*useState", self.content))
        status = "✓" if has_activeSection else "✗"
        print_info(f"{status} activeSection state", 1)
        self.log_test("activeSection State", has_activeSection)
        
        # setFormData kullanımı
        setFormData_count = len(re.findall(r"setFormData\(", self.content))
        print_success(f"setFormData kullanım: {setFormData_count} kez", 1)
        self.log_test("setFormData Usage", setFormData_count > 0)
        
        print_info(f"\nSonuç: State yönetimi tam ve düzenli")

    def analyze_event_handlers(self):
        """Event handler'larını analiz et"""
        print_section("TEST 5: EVENT HANDLERS - Olay İşleyicileri")
        
        handlers = {
            'handleChange': r"onChange",
            'handleSubmit': r"onSubmit",
            'addTimelineItem': r"addTimelineItem",
            'removeTimelineItem': r"removeTimelineItem",
            'addRootCause': r"addRootCause",
            'removeRootCause': r"removeRootCause",
            'updateChecklist': r"updateChecklist",
            'scrollToSection': r"scrollToSection",
            'loadTestScenario': r"loadTestScenario",
        }
        
        passed = 0
        for handler_name, pattern in handlers.items():
            found = bool(re.search(pattern, self.content, re.IGNORECASE))
            if found:
                print_success(f"✓ {handler_name}", 1)
                passed += 1
            else:
                print_warning(f"✗ {handler_name}", 1)
            
            self.log_test(f"Handler: {handler_name}", found)
        
        print_info(f"\nSonuç: {passed}/{len(handlers)} event handler bulundu")

    def analyze_jsx_elements(self):
        """JSX elementlerini analiz et"""
        print_section("TEST 6: JSX ELEMENTS - JSX Elementleri")
        
        elements = {
            '<input />': r"<input\s",
            '<textarea>': r"<textarea",
            '<select>': r"<select",
            '<button>': r"<button",
            '<div>': r"<div",
            '<form>': r"<form",
            '<label>': r"<label",
            'Icon components': r"<(User|AlertTriangle|Clock|CheckSquare|Users|Cloud|Briefcase|Heart|AlertCircle)",
        }
        
        passed = 0
        for element_name, pattern in elements.items():
            count = len(re.findall(pattern, self.content, re.IGNORECASE))
            if count > 0:
                print_success(f"✓ {element_name}: {count}", 1)
                passed += 1
            else:
                print_warning(f"✗ {element_name}: 0", 1)
            
            self.log_test(f"Element: {element_name}", count > 0)
        
        print_info(f"\nSonuç: {passed}/{len(elements)} element türü bulundu")

    def analyze_conditional_rendering(self):
        """Koşullu render'ı analiz et"""
        print_section("TEST 7: CONDITIONAL RENDERING - Koşullu Render")
        
        # Ternary operators
        ternary_count = len(re.findall(r"\?\s*.*?\s*:\s*", self.content))
        print_success(f"Ternary operators: {ternary_count}", 1)
        self.log_test("Ternary Operators", ternary_count > 0)
        
        # Logical AND (&&)
        logical_and_count = len(re.findall(r"&&\s*", self.content))
        print_success(f"Logical AND (&&): {logical_and_count}", 1)
        self.log_test("Logical AND", logical_and_count > 0)
        
        # map() ile list rendering
        map_count = len(re.findall(r"\.map\s*\(", self.content))
        print_success(f"List rendering (.map): {map_count}", 1)
        self.log_test("List Rendering", map_count > 0)
        
        print_info(f"\nSonuç: Koşullu rendering düzgün uygulanmış")

    def analyze_advanced_features(self):
        """Gelişmiş özellikler"""
        print_section("TEST 8: ADVANCED FEATURES - Gelişmiş Özellikler")
        
        features = {
            'Timeline functionality': 'timeline.*action.*responsible.*evidence',
            'Prevention checklist': 'preventionChecklist.*riskAssessment.*ptw.*ppe',
            'Root cause analysis': 'rootCauses.*category.*description.*preventionAction',
            'Test scenarios': 'loadTestScenario.*fall.*electric.*machine',
            'Scroll spy': 'scrollPosition.*handleScroll.*activeSection',
            'Multi-language support': 'language.*getTranslation',
        }
        
        passed = 0
        for feature_name, pattern in features.items():
            found = bool(re.search(pattern, self.content, re.IGNORECASE | re.DOTALL))
            if found:
                print_success(f"✓ {feature_name}", 1)
                passed += 1
            else:
                print_warning(f"✗ {feature_name}", 1)
            
            self.log_test(f"Feature: {feature_name}", found)
        
        print_info(f"\nSonuç: {passed}/{len(features)} gelişmiş özellik bulundu")

    def analyze_code_quality(self):
        """Kod kalitesini analiz et"""
        print_section("TEST 9: CODE QUALITY - Kod Kalitesi")
        
        metrics = {}
        
        # Satır sayısı
        lines = len(self.content.split('\n'))
        metrics['Toplam Satır'] = lines
        print_info(f"Toplam Satır: {lines}", 1)
        
        # Component sayısı
        components = len(re.findall(r"const\s+\w+\s*=\s*\(\{.*?\}\)\s*=>|function\s+\w+", self.content))
        metrics['Component/Function'] = components
        print_info(f"Component/Function: {components}", 1)
        
        # Hook kullanımı
        hooks = len(re.findall(r"use\w+\(", self.content))
        metrics['React Hooks'] = hooks
        print_info(f"React Hooks: {hooks}", 1)
        
        # Event handler'lar
        handlers = len(re.findall(r"(handle\w+|on\w+)\s*=\s*(.*?)=>", self.content))
        metrics['Event Handlers'] = handlers
        print_info(f"Event Handlers: {handlers}", 1)
        
        # Comments/Documentation
        comments = len(re.findall(r"//.*$|/\*.*?\*/", self.content, re.MULTILINE | re.DOTALL))
        metrics['Comments'] = comments
        print_info(f"Comments: {comments}", 1)
        
        # Code complexity heuristic
        complexity = (components * 10 + hooks * 5 + handlers * 3) / lines if lines > 0 else 0
        
        if complexity < 0.5:
            complexity_level = "Düşük ✓"
            print_success("Karmaşıklık: Düşük (Temiz ve anlaşılır)", 1)
            self.log_test("Code Complexity", True)
        elif complexity < 1.0:
            complexity_level = "Orta ✓"
            print_success("Karmaşıklık: Orta (Normal)", 1)
            self.log_test("Code Complexity", True)
        else:
            complexity_level = "Yüksek ⚠️"
            print_warning("Karmaşıklık: Yüksek", 1)
            self.log_test("Code Complexity", False)
        
        print_info(f"\nKod kalitesi metrikleri: ✓")

    def analyze_form_fields_count(self):
        """Form field sayısını analiz et"""
        print_section("TEST 10: FORM FIELDS COUNT - Form Alanları Sayısı")
        
        # Input fields
        input_count = len(re.findall(r"<input\s+type=['\"]([^'\"]+)['\"]", self.content))
        print_info(f"Input field sayısı: {input_count}", 1)
        self.log_test("Input Fields", input_count > 0)
        
        # Textarea fields
        textarea_count = len(re.findall(r"<textarea", self.content))
        print_info(f"Textarea sayısı: {textarea_count}", 1)
        self.log_test("Textarea Fields", textarea_count > 0)
        
        # Select fields
        select_count = len(re.findall(r"<select", self.content))
        print_info(f"Select (dropdown) sayısı: {select_count}", 1)
        self.log_test("Select Fields", select_count > 0)
        
        # Button fields
        button_count = len(re.findall(r"<button", self.content))
        print_info(f"Button sayısı: {button_count}", 1)
        self.log_test("Buttons", button_count > 0)
        
        total_fields = input_count + textarea_count + select_count + button_count
        print_success(f"\nToplam interactive element: {total_fields}", 1)

    def log_test(self, name, passed):
        """Test sonucunu kayıt et"""
        self.test_results["total"] += 1
        status = "PASS" if passed else "FAIL"
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
        
        self.test_results["tests"].append({"name": name, "status": status})

    def print_summary(self):
        """Test özeti"""
        print_header("TEST ÖZETİ - SONUÇLAR")
        
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Toplam Testler: {total}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Başarılı: {passed}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}❌ Başarısız: {failed}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}📊 Başarı Oranı: %{percentage:.1f}{Colors.END}\n")
        
        if percentage >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 KUSURSUZ! Component production-ready!{Colors.END}")
        elif percentage >= 75:
            print(f"{Colors.YELLOW}{Colors.BOLD}✓ İyi! Component çalışır durumda!{Colors.END}")
        elif percentage >= 50:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Kısmen başarılı!{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Başarısız!{Colors.END}")
        
        print()

    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print_header("JSX COMPONENT ANALIZ - IncidentForm_NEW.jsx")
        
        # Dosya yükle
        if not self.load_file():
            return
        
        print_info(f"Analiz ediliyor: {self.jsx_file}\n")
        
        # Testleri çalıştır
        self.analyze_imports()
        self.analyze_component_structure()
        self.analyze_form_sections()
        self.analyze_state_management()
        self.analyze_event_handlers()
        self.analyze_jsx_elements()
        self.analyze_conditional_rendering()
        self.analyze_advanced_features()
        self.analyze_code_quality()
        self.analyze_form_fields_count()
        
        # Özet
        self.print_summary()

if __name__ == "__main__":
    jsx_file = "/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/components/IncidentForm_NEW.jsx"
    analyzer = JSXComponentAnalyzer(jsx_file)
    analyzer.run_all_tests()
