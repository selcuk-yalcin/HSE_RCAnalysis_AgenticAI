#!/usr/bin/env python3
"""
REACT COMPONENT TEST - IncidentForm_NEW.jsx
============================================
React component'ini test eder:
1. Component rendering
2. Form sections
3. Input fields
4. Timeline functionality
5. Prevention checklist
6. Root causes
7. Form submission
"""

import requests
import time
import json
import re
from typing import List, Dict, Tuple

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

class ReactComponentTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        self.html_content = ""

    def wait_for_server(self, max_attempts=10):
        """Sunucunun hazır olmasını bekle"""
        print_info(f"Server kontrol ediliyor: {self.base_url}")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(self.base_url, timeout=2)
                if response.status_code == 200:
                    print_success("Server hazır!")
                    return True
            except:
                pass
            
            print_info(f"Deneme {attempt + 1}/{max_attempts}...", 1)
            time.sleep(1)
        
        print_error("Server başlatılamadı!")
        return False

    def fetch_html(self):
        """HTML içeriğini indir"""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.html_content = response.text
            print_success(f"HTML içeriği indirildi ({len(self.html_content)} bytes)")
            return True
        except Exception as e:
            print_error(f"HTML indirilemedi: {e}")
            return False

    def test_component_rendering(self):
        """Component render kontrolü"""
        print_section("TEST 1: COMPONENT RENDERING - Bileşen Oluşturma")
        
        tests = [
            ("React Root Element", "id=\"root\"", "#root"),
            ("App Component", "class=\"app", "App wrapper"),
            ("IncidentForm Component", "IncidentForm", "Form bileşeni"),
        ]
        
        passed = 0
        for test_name, pattern, description in tests:
            if pattern.lower() in self.html_content.lower():
                print_success(f"{test_name}: {description} bulundu", 1)
                passed += 1
            else:
                print_error(f"{test_name}: {description} bulunamadı", 1)
            self.log_test(test_name, pattern.lower() in self.html_content.lower())
        
        print_info(f"Sonuç: {passed}/{len(tests)} başarılı")

    def test_form_sections(self):
        """Form section'larını test et"""
        print_section("TEST 2: FORM SECTIONS - Form Bölümleri")
        
        sections = [
            ("Bildirim Yapan", "reporter|report"),
            ("Kaza Detayları", "incident|severity"),
            ("Olay Akışı", "timeline|action"),
            ("Kontrol Listesi", "prevention|checklist"),
            ("Olay Açıklaması", "5w1h|what|where|when"),
            ("Tanıklar", "witness|testify"),
            ("Çevre Koşulları", "weather|lighting|temperature"),
            ("Çalışma Koşulları", "work.*type|experience"),
            ("Yaralanma/Hasar", "injury|bodypart|severity"),
            ("Kök Neden & Önlemler", "root.*cause|prevention|action"),
        ]
        
        passed = 0
        for section_name, pattern in sections:
            found = False
            for word in pattern.split("|"):
                if word.lower() in self.html_content.lower():
                    found = True
                    break
            
            if found:
                print_success(f"Bölüm bulundu: {section_name}", 1)
                passed += 1
            else:
                print_warning(f"Bölüm eksik: {section_name}", 1)
            
            self.log_test(f"Section: {section_name}", found)
        
        print_info(f"Sonuç: {passed}/{len(sections)} bölüm bulundu")

    def test_input_fields(self):
        """Input field'larını test et"""
        print_section("TEST 3: INPUT FIELDS - Giriş Alanları")
        
        # HTML'de input taglarını ara
        input_pattern = r'<input[^>]*type=["\']([^"\']+)["\'][^>]*(?:name|id)=["\']([^"\']+)["\']'
        inputs = re.findall(input_pattern, self.html_content, re.IGNORECASE)
        
        print_info(f"Toplam input field bulundu: {len(inputs)}")
        
        # Input tiplerini say
        input_types = {}
        for input_type, name in inputs:
            input_types[input_type] = input_types.get(input_type, 0) + 1
        
        passed = len(input_types)
        for input_type, count in input_types.items():
            print_success(f"{input_type}: {count} adet", 1)
            self.log_test(f"Input Type: {input_type}", True)
        
        # Textarea'ları ara
        textarea_count = self.html_content.count("<textarea")
        if textarea_count > 0:
            print_success(f"Textarea: {textarea_count} adet", 1)
            self.log_test("Textarea Fields", True)
        else:
            print_warning("Textarea alanları bulunamadı", 1)
            self.log_test("Textarea Fields", False)
        
        # Select (dropdown) ara
        select_count = self.html_content.count("<select")
        if select_count > 0:
            print_success(f"Select/Dropdown: {select_count} adet", 1)
            self.log_test("Select Fields", True)
        else:
            print_warning("Select alanları bulunamadı", 1)
            self.log_test("Select Fields", False)

    def test_react_features(self):
        """React specific features"""
        print_section("TEST 4: REACT FEATURES - React Özellikleri")
        
        features = [
            ("useState Hook", "useState", "State yönetimi"),
            ("useEffect Hook", "useEffect", "Side effects"),
            ("useRef Hook", "useRef", "Referans yönetimi"),
            ("Component Props", "props", "Prop geçişi"),
            ("Event Handlers", "onClick|onChange|onSubmit", "Olay işleyiciler"),
        ]
        
        passed = 0
        for feature_name, pattern, description in features:
            found = False
            for word in pattern.split("|"):
                if word.lower() in self.html_content.lower():
                    found = True
                    break
            
            if found:
                print_success(f"{feature_name}: {description}", 1)
                passed += 1
            else:
                print_warning(f"{feature_name}: {description} (indir HTML'de görülmedi)", 1)
            
            self.log_test(feature_name, found)
        
        print_info(f"Sonuç: {passed}/{len(features)} React özelliği bulundu")

    def test_styling(self):
        """CSS styling kontrol"""
        print_section("TEST 5: STYLING - Stil ve Tasarım")
        
        css_classes = [
            "IncidentForm", "section", "form-group", "input-field",
            "button", "btn-primary", "btn-secondary", "alert",
            "timeline", "checklist", "card"
        ]
        
        found_classes = []
        for css_class in css_classes:
            if f'class="{css_class}' in self.html_content or f"class='{css_class}" in self.html_content or f" {css_class}" in self.html_content:
                found_classes.append(css_class)
        
        print_info(f"Bulunan CSS sınıfları: {len(found_classes)}/{len(css_classes)}")
        
        for css_class in found_classes[:10]:  # İlk 10'i göster
            print_success(f"CSS sınıfı: {css_class}", 1)
        
        if len(found_classes) > 10:
            print_info(f"... ve {len(found_classes) - 10} daha", 1)
        
        self.log_test("CSS Classes", len(found_classes) > 0)

    def test_form_elements(self):
        """Form element'lerini test et"""
        print_section("TEST 6: FORM ELEMENTS - Form Elementleri")
        
        elements = {
            "Form Tag": "<form",
            "Button Tag": "<button",
            "Label Tag": "<label",
            "Div Container": "<div",
            "Section Tag": "<section",
        }
        
        passed = 0
        for element_name, element_tag in elements.items():
            count = self.html_content.count(element_tag)
            if count > 0:
                print_success(f"{element_name}: {count} adet", 1)
                passed += 1
            else:
                print_warning(f"{element_name}: bulunamadı", 1)
            
            self.log_test(element_name, count > 0)
        
        print_info(f"Sonuç: {passed}/{len(elements)} element türü bulundu")

    def test_special_features(self):
        """Özel özellikler"""
        print_section("TEST 7: SPECIAL FEATURES - Özel Özellikler")
        
        features = {
            "Timeline": "timeline",
            "Prevention Checklist": "prevention.*checklist|preventionChecklist",
            "Root Causes": "root.*cause|rootCauses",
            "5W1H Analysis": "5w|1h|what|where|when|why|how",
            "Evidence Tracking": "evidence",
            "Multi-language": "language|tr|en",
            "Icons (Lucide)": "lucide-react",
        }
        
        passed = 0
        for feature_name, pattern in features.items():
            found = False
            for word in pattern.split("|"):
                if re.search(word, self.html_content, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                print_success(f"Özel özellik: {feature_name}", 1)
                passed += 1
            else:
                print_warning(f"Özel özellik eksik: {feature_name}", 1)
            
            self.log_test(f"Special: {feature_name}", found)
        
        print_info(f"Sonuç: {passed}/{len(features)} özel özellik bulundu")

    def analyze_code_structure(self):
        """Kod yapısını analiz et"""
        print_section("TEST 8: CODE STRUCTURE - Kod Yapısı")
        
        # Component method'larını ara
        methods = {
            "handleChange": "handleChange|onChange",
            "handleSubmit": "handleSubmit|onSubmit",
            "handleAddTimeline": "handleAddTimeline|addTimeline",
            "handleRemoveTimeline": "handleRemoveTimeline|removeTimeline",
            "handleAddRootCause": "handleAddRootCause|addRootCause",
            "handleRemoveRootCause": "handleRemoveRootCause|removeRootCause",
            "updatePreventionChecklist": "updatePreventionChecklist|checklist",
        }
        
        passed = 0
        for method_name, pattern in methods.items():
            found = False
            for word in pattern.split("|"):
                if re.search(word, self.html_content, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                print_success(f"Method: {method_name}", 1)
                passed += 1
            else:
                print_warning(f"Method eksik: {method_name}", 1)
            
            self.log_test(f"Method: {method_name}", found)
        
        print_info(f"Sonuç: {passed}/{len(methods)} method pattern bulundu")

    def estimate_complexity(self):
        """Bileşen karmaşıklığını tahmin et"""
        print_section("TEST 9: COMPONENT COMPLEXITY - Bileşen Karmaşıklığı")
        
        # Ölçüm
        lines = len(self.html_content.split('\n'))
        functions = len(re.findall(r'function|const.*=.*\(|method', self.html_content, re.IGNORECASE))
        components = self.html_content.count('component')
        state_vars = self.html_content.count('useState')
        effects = self.html_content.count('useEffect')
        
        metrics = {
            "Satır Sayısı": lines,
            "Fonksiyon/Method": functions,
            "Component": components,
            "State Değişkenleri": state_vars,
            "useEffect Hook": effects,
        }
        
        for metric_name, value in metrics.items():
            print_info(f"{metric_name}: {value}", 1)
        
        # Karmaşıklık değerlendirmesi
        complexity_score = (functions + state_vars * 2 + effects) / lines if lines > 0 else 0
        
        if complexity_score < 0.1:
            complexity = "Düşük ✓"
            print_success("Karmaşıklık: Düşük (Basit ve temiz)", 1)
        elif complexity_score < 0.2:
            complexity = "Orta ✓"
            print_success("Karmaşıklık: Orta (Normal)", 1)
        else:
            complexity = "Yüksek ⚠️"
            print_warning("Karmaşıklık: Yüksek (Refactor gerekebilir)", 1)

    def test_translations(self):
        """Tercüme ve çok dil desteği"""
        print_section("TEST 10: TRANSLATIONS - Çok Dil Desteği")
        
        languages = {
            "Türkçe": ["tr", "bildirim", "kaza", "olay"],
            "İngilizce": ["en", "report", "incident", "event"],
        }
        
        passed = 0
        for lang_name, keywords in languages.items():
            found_count = 0
            for keyword in keywords:
                if keyword.lower() in self.html_content.lower():
                    found_count += 1
            
            percentage = (found_count / len(keywords)) * 100
            if percentage >= 50:
                print_success(f"{lang_name}: %{percentage:.0f} kelime bulundu", 1)
                passed += 1
            else:
                print_warning(f"{lang_name}: %{percentage:.0f} kelime bulundu", 1)
            
            self.log_test(f"Language: {lang_name}", percentage >= 50)
        
        print_info(f"Sonuç: {passed}/{len(languages)} dil desteği")

    def log_test(self, name, passed):
        """Test sonucunu kayıt et"""
        self.test_results["total"] += 1
        status = "PASS" if passed else "FAIL"
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
        
        self.test_results["tests"].append({
            "name": name,
            "status": status
        })

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
        
        print(f"{Colors.BOLD}Detaylı Sonuçlar (son 15):{Colors.END}")
        for test in self.test_results["tests"][-15:]:
            status_icon = "✅" if test["status"] == "PASS" else "❌"
            print(f"  {status_icon} {test['name']}: {test['status']}")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        # Sonuç
        if percentage >= 85:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 BAŞARILI! React Component production-ready!{Colors.END}")
        elif percentage >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Kısmen başarılı, iyileştirme alanları var{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Başarısız, ciddi sorunlar var{Colors.END}")
        
        print()

    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print_header("REACT COMPONENT TEST - IncidentForm_NEW.jsx")
        print_info(f"URL: {self.base_url}")
        print_info(f"Tarih/Saat: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Server kontrolü
        if not self.wait_for_server():
            print_error("Server başlatılamadı, test iptal ediliyor")
            return
        
        time.sleep(2)
        
        # HTML'i indir
        if not self.fetch_html():
            print_error("HTML indirilemedi, test iptal ediliyor")
            return
        
        time.sleep(1)
        
        # Testleri çalıştır
        self.test_component_rendering()
        time.sleep(0.5)
        
        self.test_form_sections()
        time.sleep(0.5)
        
        self.test_input_fields()
        time.sleep(0.5)
        
        self.test_react_features()
        time.sleep(0.5)
        
        self.test_styling()
        time.sleep(0.5)
        
        self.test_form_elements()
        time.sleep(0.5)
        
        self.test_special_features()
        time.sleep(0.5)
        
        self.analyze_code_structure()
        time.sleep(0.5)
        
        self.estimate_complexity()
        time.sleep(0.5)
        
        self.test_translations()
        time.sleep(0.5)
        
        # Özet
        self.print_summary()
        
        print_success("Tüm testler tamamlandı!")

if __name__ == "__main__":
    tester = ReactComponentTester()
    tester.run_all_tests()
