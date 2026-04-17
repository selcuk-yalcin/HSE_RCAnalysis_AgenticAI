# HSE RCA Test Suite

Incident analiz sisteminin test dosyalarını içeren klasör.

## Test Dosyaları

### `test_mpt_falling_part_dspy.py`
MPT (Multi-Purpose Test) Test Sahasında meydana gelen sarmal kapı düşen parça ramak kala (near-miss) olayının DSpy framework'ü kullanılarak yapılandırılmış incident analizi.

**Özellikler:**
- DSpy Signatures ile yapılandırılmış giriş/çıktı
- Chain-of-Thought reasoning (TypedChainOfThought)
- 4-stage pipeline: Overview → Assessment → Root Cause → Corrective Actions
- 5-WHY metodolojisi
- Meta kök neden (ortak payda) analizi
- JSON output ile sonuç kaydetme
- Otomatik test validasyonu

**Çalıştırma:**
```bash
python test_mpt_falling_part_dspy.py
```

**Gerekli Kütüphaneler:**
- dspy-ai
- openai (or anthropic)

**Ortam Değişkenleri:**
```bash
export OPENAI_API_KEY=sk-...  # veya
export ANTHROPIC_API_KEY=sk-ant-...
```

## Test Yapısı

Tüm testler aşağıdaki yapıyı takip eder:

1. **Overview Phase** - Olay özeti ve ilk değerlendirme
2. **Assessment Phase** - Risk değerlendirmesi ve potansiyel zarar analizi
3. **Root Cause Analysis** - 5-WHY metodolojisi ile kök nedenleri bulma
4. **Corrective Actions** - Düzeltici ve önleyici tedbirler belirleme

## Yeni Test Ekleme

Yeni bir test eklemek için:

1. Test dosyasını `test_*.py` formatında adlandır
2. `tests/` klasörü içine koy
3. DSpy signatures ve modules kullan
4. JSON output ile sonuçları kaydet
5. Otomatik validasyon yapısı ekle

Örnek template:
```python
import dspy
from dspy.signatures.signature import Signature
from dspy.functional.functional import TypedChainOfThought

class MyTestSignature(Signature):
    """Test açıklaması."""
    input_field: str = dspy.InputField(desc="Input açıklaması")
    output_field: str = dspy.OutputField(desc="Output açıklaması")

class MyTestModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.chain = TypedChainOfThought(MyTestSignature)
    
    def forward(self, data):
        return self.chain(input_field=data)

if __name__ == "__main__":
    # Test kodu
    pass
```

## Proje Yapısı

```
HSE_RCAnalysis_AgenticAI/
├── agents/              # Incident analiz ajanları
├── hitl_test/           # Human-in-the-loop test klasörü
├── tests/               # 📍 Test suite
│   ├── __init__.py
│   ├── README.md
│   └── test_mpt_falling_part_dspy.py
├── README.md
└── V3_1_ARCHITECTURE.md
```

## Lisans

Bu test suite HSE RCA projesi kapsamında geliştirilmiştir.
