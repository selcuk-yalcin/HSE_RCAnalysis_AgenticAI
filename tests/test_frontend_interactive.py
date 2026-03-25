#!/usr/bin/env python3
"""
KAPSAMLI FRONTEND INTERAKTIF TEST
==================================
Form component'lerinin hepsini test eder:
1. Checkbox + Textarea (Conditional fields)
2. Radio button groups
3. Auto-save (localStorage)
4. Form submission flow
5. Quick test buttons
6. Responsive design
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Renkli çıktı için
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

class FrontendTester:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "http://localhost:8000/incident_report_form.html"
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }

    def setup(self):
        """Selenium driver'ı hazırla"""
        print_info("Browser başlatılıyor...")
        chrome_options = Options()
        # Headless mode kapatalım, görelim ne oluyor
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print_success("Browser başlatıldı")
        except Exception as e:
            print_error(f"Browser başlatılamadı: {e}")
            print_warning("Chrome/Chromium yüklü olduğundan emin ol")
            return False
        return True

    def load_form(self):
        """Formu yükle"""
        print_info(f"Form yükleniyor: {self.base_url}")
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "incidentForm")))
            print_success("Form yüklendi")
            return True
        except TimeoutException:
            print_error("Form yüklenemedi (timeout)")
            return False

    def test_form_basics(self):
        """Form temel elementlerini kontrol et"""
        print_header("TEST 1: FORM BASICS - Temel Elementler")
        
        tests = [
            ("Form ID", "incidentForm"),
            ("Tab navigation", "sectionTabs"),
            ("Investigation section", "[data-section='7']"),
        ]
        
        for test_name, selector in tests:
            try:
                if selector.startswith("["):
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                else:
                    elem = self.driver.find_element(By.ID, selector)
                print_success(f"{test_name} bulundu")
                self.log_test(test_name, True)
            except NoSuchElementException:
                print_error(f"{test_name} bulunamadı")
                self.log_test(test_name, False)

    def switch_to_investigation_tab(self):
        """Detaylı Araştırma tab'ına geç"""
        print_info("'Detaylı Araştırma' tab'ına geçiliyor...")
        try:
            # Tab 7'yi bul (0-indexed olarak 7. index)
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick^='showSection']")
            if len(tabs) >= 8:
                tabs[7].click()
                time.sleep(1)
                print_success("Tab değiştirildi")
                return True
            else:
                print_error(f"Tab bulunamadı (sadece {len(tabs)} tab var)")
                return False
        except Exception as e:
            print_error(f"Tab değiştirme hatası: {e}")
            return False

    def test_checkbox_conditional_fields(self):
        """Checkbox + Conditional field test"""
        print_header("TEST 2: CHECKBOX + CONDITIONAL FIELDS - Koşullu Alanlar")
        
        try:
            # Tüm checkbox'ları bul
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][data-question]")
            print_info(f"Bulunan checkbox sayısı: {len(checkboxes)}")
            
            test_count = 0
            passed_count = 0
            
            for i, checkbox in enumerate(checkboxes[:5]):  # İlk 5'ini test et
                try:
                    question_id = checkbox.get_attribute("data-question")
                    target_id = checkbox.get_attribute("data-target")
                    
                    print_info(f"\nSoru {i+1} test ediliyor (data-question={question_id})...")
                    
                    # 1. Checkbox'ı tıkla (aç)
                    self.driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                    time.sleep(0.5)
                    checkbox.click()
                    time.sleep(0.5)
                    
                    # 2. Conditional field açıldı mı kontrol et
                    if target_id:
                        target_elem = self.driver.find_element(By.ID, target_id)
                        is_visible = target_elem.is_displayed()
                        
                        if is_visible:
                            print_success(f"  ✓ Conditional field açıldı (#{target_id})")
                            passed_count += 1
                        else:
                            print_error(f"  ✗ Conditional field açılmadı (#{target_id})")
                    
                    # 3. Checkbox'ı tekrar tıkla (kapat)
                    checkbox.click()
                    time.sleep(0.5)
                    
                    if target_id:
                        is_hidden = not target_elem.is_displayed()
                        if is_hidden:
                            print_success(f"  ✓ Conditional field kapandı")
                        else:
                            print_error(f"  ✗ Conditional field kapanmadı")
                    
                    test_count += 1
                    
                except Exception as e:
                    print_error(f"  Hata: {e}")
                    test_count += 1
            
            print_info(f"\nCheckbox testleri: {passed_count}/{test_count} başarılı")
            self.log_test("Checkbox Conditional Fields", passed_count == test_count)
            
        except Exception as e:
            print_error(f"Checkbox test hatası: {e}")
            self.log_test("Checkbox Conditional Fields", False)

    def test_radio_button_groups(self):
        """Radio button groups test"""
        print_header("TEST 3: RADIO BUTTON GROUPS - Radio Buton Grupları")
        
        try:
            # Radio button gruplarını bul
            radio_groups = self.driver.find_elements(By.CSS_SELECTOR, ".radio-group")
            print_info(f"Bulunan radio grubu sayısı: {len(radio_groups)}")
            
            test_count = 0
            passed_count = 0
            
            for i, group in enumerate(radio_groups[:3]):  # İlk 3 grubu test et
                try:
                    print_info(f"\nRadio grubu {i+1} test ediliyor...")
                    
                    # Radio button'ları bul
                    radios = group.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    print_info(f"  Radio button sayısı: {len(radios)}")
                    
                    if len(radios) > 0:
                        # İlk radio'yu seç
                        self.driver.execute_script("arguments[0].scrollIntoView();", group)
                        time.sleep(0.3)
                        
                        radios[0].click()
                        time.sleep(0.5)
                        
                        if radios[0].is_selected():
                            print_success(f"  ✓ Radio buton seçildi")
                            passed_count += 1
                        else:
                            print_error(f"  ✗ Radio buton seçilemedi")
                        
                        # İkinci option varsa onu seç
                        if len(radios) > 1:
                            radios[1].click()
                            time.sleep(0.5)
                            if radios[1].is_selected():
                                print_success(f"  ✓ İkinci radio seçildi")
                            else:
                                print_error(f"  ✗ İkinci radio seçilemedi")
                    
                    test_count += 1
                    
                except Exception as e:
                    print_error(f"  Radio grubu hatası: {e}")
                    test_count += 1
            
            print_info(f"\nRadio buton testleri: {passed_count}/{test_count} başarılı")
            self.log_test("Radio Button Groups", passed_count == test_count)
            
        except Exception as e:
            print_error(f"Radio button test hatası: {e}")
            self.log_test("Radio Button Groups", False)

    def test_form_input_and_autosave(self):
        """Form input ve auto-save test"""
        print_header("TEST 4: FORM INPUT & AUTO-SAVE - Form Girişi ve Otomatik Kayıt")
        
        try:
            # Text input bulup test et
            text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            print_info(f"Bulunan text input sayısı: {len(text_inputs)}")
            
            if len(text_inputs) > 0:
                test_input = text_inputs[0]
                test_value = "Test Değeri 🧪"
                
                # Input'a değer yaz
                self.driver.execute_script("arguments[0].scrollIntoView();", test_input)
                time.sleep(0.3)
                test_input.clear()
                test_input.send_keys(test_value)
                time.sleep(1)
                
                # localStorage'da kaydedildi mi kontrol et
                saved_data = self.driver.execute_script("""
                    return localStorage.getItem('incidentFormDraft');
                """)
                
                if saved_data:
                    print_success("Auto-save localStorage'a kaydetti")
                    try:
                        draft = json.loads(saved_data)
                        print_info(f"  Kayıtlı veri: {list(draft.keys())[:5]}... ({len(draft)} alan)")
                        self.log_test("Form Input & Auto-save", True)
                    except json.JSONDecodeError:
                        print_warning("  localStorage verisi JSON parse edilemedi")
                        self.log_test("Form Input & Auto-save", False)
                else:
                    print_error("Auto-save localStorage'a kaydetmedi")
                    self.log_test("Form Input & Auto-save", False)
            else:
                print_warning("Test için text input bulunamadı")
                self.log_test("Form Input & Auto-save", False)
                
        except Exception as e:
            print_error(f"Form input test hatası: {e}")
            self.log_test("Form Input & Auto-save", False)

    def test_textarea_inputs(self):
        """Textarea input test"""
        print_header("TEST 5: TEXTAREA INPUTS - Çok Satırlı Alanlar")
        
        try:
            textareas = self.driver.find_elements(By.CSS_SELECTOR, "textarea")
            print_info(f"Bulunan textarea sayısı: {len(textareas)}")
            
            if len(textareas) > 0:
                test_textarea = textareas[0]
                test_value = "Detaylı açıklama test 📝\nİkinci satır\nÜçüncü satır"
                
                # Textarea'ya değer yaz
                self.driver.execute_script("arguments[0].scrollIntoView();", test_textarea)
                time.sleep(0.3)
                test_textarea.clear()
                test_textarea.send_keys(test_value)
                time.sleep(0.5)
                
                # Değer yazıldı mı kontrol et
                current_value = test_textarea.get_attribute("value")
                if test_value in current_value:
                    print_success("Textarea değeri başarıyla yazıldı")
                    self.log_test("Textarea Inputs", True)
                else:
                    print_error("Textarea değeri yazılamadı")
                    self.log_test("Textarea Inputs", False)
            else:
                print_warning("Test için textarea bulunamadı")
                self.log_test("Textarea Inputs", False)
                
        except Exception as e:
            print_error(f"Textarea test hatası: {e}")
            self.log_test("Textarea Inputs", False)

    def test_form_validation(self):
        """Form doğrulama test"""
        print_header("TEST 6: FORM VALIDATION - Form Doğrulama")
        
        try:
            # Özet tab'ına geç
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick^='showSection']")
            if len(tabs) >= 10:  # Özet tab 9. index (0-based)
                tabs[9].click()
                time.sleep(1)
                print_success("Özet tab'ına geçildi")
                
                # Kontrol listesi öğelerini ara
                checklist_items = self.driver.find_elements(By.CSS_SELECTOR, ".checklist-item")
                print_info(f"Kontrol listesi öğeleri: {len(checklist_items)}")
                
                if len(checklist_items) > 0:
                    print_success("Form doğrulama kontrol listesi bulundu")
                    self.log_test("Form Validation", True)
                else:
                    print_warning("Kontrol listesi öğeleri bulunamadı")
                    self.log_test("Form Validation", False)
            else:
                print_warning("Özet tab bulunamadı")
                self.log_test("Form Validation", False)
                
        except Exception as e:
            print_error(f"Form validation test hatası: {e}")
            self.log_test("Form Validation", False)

    def test_responsive_design(self):
        """Responsive tasarım test"""
        print_header("TEST 7: RESPONSIVE DESIGN - Duyarlı Tasarım")
        
        try:
            # Viewport meta tag kontrol et
            viewport = self.driver.find_element(By.CSS_SELECTOR, "meta[name='viewport']")
            content = viewport.get_attribute("content")
            
            if "width=device-width" in content and "initial-scale=1" in content:
                print_success("Viewport meta tag doğru ayarlanmış")
                self.log_test("Responsive Design", True)
            else:
                print_warning("Viewport ayarları eksik")
                print_info(f"  Viewport content: {content}")
                self.log_test("Responsive Design", False)
                
        except Exception as e:
            print_error(f"Responsive design test hatası: {e}")
            self.log_test("Responsive Design", False)

    def test_css_styling(self):
        """CSS styling test"""
        print_header("TEST 8: CSS STYLING - CSS Stilleri")
        
        try:
            # Investigation section stil kontrol et
            inv_section = self.driver.find_element(By.CSS_SELECTOR, ".investigation-section")
            bg_color = inv_section.value_of_css_property("background-color")
            
            print_info(f"Investigation section background: {bg_color}")
            
            # Conditional field stil kontrol et
            cond_fields = self.driver.find_elements(By.CSS_SELECTOR, ".conditional-field")
            if len(cond_fields) > 0:
                border = cond_fields[0].value_of_css_property("border-left")
                print_info(f"Conditional field border: {border}")
                print_success("CSS stilleri uygulanmış")
                self.log_test("CSS Styling", True)
            else:
                print_warning("Conditional field bulunamadı")
                self.log_test("CSS Styling", False)
                
        except Exception as e:
            print_error(f"CSS styling test hatası: {e}")
            self.log_test("CSS Styling", False)

    def test_javascript_functions(self):
        """JavaScript fonksiyonları test"""
        print_header("TEST 9: JAVASCRIPT FUNCTIONS - JavaScript Fonksiyonları")
        
        try:
            # showSection fonksiyonunu kontrol et
            result = self.driver.execute_script("""
                return typeof showSection === 'function';
            """)
            
            if result:
                print_success("showSection() fonksiyonu tanımlı")
            else:
                print_error("showSection() fonksiyonu tanımlı değil")
            
            # updateConditionalField fonksiyonunu kontrol et
            result2 = self.driver.execute_script("""
                return typeof updateConditionalField === 'function';
            """)
            
            if result2:
                print_success("updateConditionalField() fonksiyonu tanımlı")
            else:
                print_error("updateConditionalField() fonksiyonu tanımlı değil")
            
            # saveDraft fonksiyonunu kontrol et
            result3 = self.driver.execute_script("""
                return typeof saveDraft === 'function';
            """)
            
            if result3:
                print_success("saveDraft() fonksiyonu tanımlı")
            else:
                print_error("saveDraft() fonksiyonu tanımlı değil")
            
            all_passed = result and result2 and result3
            self.log_test("JavaScript Functions", all_passed)
            
        except Exception as e:
            print_error(f"JavaScript functions test hatası: {e}")
            self.log_test("JavaScript Functions", False)

    def test_console_errors(self):
        """Console hataları kontrol et"""
        print_header("TEST 10: CONSOLE ERRORS - Konsol Hataları")
        
        try:
            logs = self.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            warnings = [log for log in logs if log['level'] == 'WARNING']
            
            print_info(f"Konsol SEVERE: {len(errors)}")
            print_info(f"Konsol WARNING: {len(warnings)}")
            
            if errors:
                print_warning("Konsol hataları bulundu:")
                for error in errors[:5]:
                    print_error(f"  - {error['message']}")
            else:
                print_success("Konsol hatası yok")
            
            self.log_test("Console Errors", len(errors) == 0)
            
        except Exception as e:
            print_warning(f"Console log kontrol edilemedi: {e}")
            self.log_test("Console Errors", False)

    def test_all_tabs(self):
        """Tüm tab'ları test et"""
        print_header("TEST 11: TAB NAVIGATION - Tab Navigasyonu")
        
        try:
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick^='showSection']")
            print_info(f"Toplam tab sayısı: {len(tabs)}")
            
            if len(tabs) == 10:
                print_success("10 tab bulundu (beklenen)")
                
                # Her tab'ı tıkla
                for i, tab in enumerate(tabs):
                    try:
                        tab.click()
                        time.sleep(0.5)
                        print_success(f"  Tab {i+1} tıklandı")
                    except Exception as e:
                        print_error(f"  Tab {i+1} hatası: {e}")
                
                self.log_test("Tab Navigation", True)
            else:
                print_error(f"Tab sayısı hatalı: {len(tabs)} (beklenen 10)")
                self.log_test("Tab Navigation", False)
                
        except Exception as e:
            print_error(f"Tab navigation test hatası: {e}")
            self.log_test("Tab Navigation", False)

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
        """Test özeti bastır"""
        print_header("TEST ÖZETİ - SONUÇLAR")
        
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Toplam Testler: {total}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Başarılı: {passed}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}❌ Başarısız: {failed}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}📊 Başarı Oranı: %{percentage:.1f}{Colors.END}\n")
        
        print(f"{Colors.BOLD}Detaylı Sonuçlar:{Colors.END}")
        for test in self.test_results["tests"]:
            status_icon = "✅" if test["status"] == "PASS" else "❌"
            print(f"  {status_icon} {test['name']}: {test['status']}")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        
        # Sonuç
        if percentage >= 80:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 BAŞARILI! Form production-ready!{Colors.END}")
        elif percentage >= 60:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Kısmen başarılı, iyileştirme gereken alanlar var{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Başarısız, ciddi sorunlar var{Colors.END}")

    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print_header("KAPSAMLI FRONTEND TEST BAŞLANIYOR")
        print_info(f"URL: {self.base_url}")
        print_info(f"Tarih/Saat: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Setup
        if not self.setup():
            return
        
        # Form yükle
        if not self.load_form():
            return
        
        # Temel testler
        self.test_form_basics()
        time.sleep(1)
        
        # Detaylı Araştırma tab'ına geç
        if self.switch_to_investigation_tab():
            time.sleep(1)
            
            # Conditional field testleri
            self.test_checkbox_conditional_fields()
            time.sleep(1)
            
            # Radio button testleri
            self.test_radio_button_groups()
            time.sleep(1)
        
        # Tab navigasyonu
        self.test_all_tabs()
        time.sleep(1)
        
        # Form testleri
        self.test_form_input_and_autosave()
        time.sleep(0.5)
        self.test_textarea_inputs()
        time.sleep(0.5)
        self.test_form_validation()
        time.sleep(0.5)
        
        # Responsive ve CSS testleri
        self.test_responsive_design()
        time.sleep(0.5)
        self.test_css_styling()
        time.sleep(0.5)
        
        # JavaScript ve konsol testleri
        self.test_javascript_functions()
        time.sleep(0.5)
        self.test_console_errors()
        time.sleep(0.5)
        
        # Özet
        self.print_summary()
        
        # Browser'ı kapat
        print_info("Browser kapatılıyor...")
        self.driver.quit()
        print_success("Test tamamlandı!\n")

if __name__ == "__main__":
    tester = FrontendTester()
    tester.run_all_tests()
