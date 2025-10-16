# Presidio PII Analyzer 🔒

Microsoft Presidio tabanlı güçlü bir **Kişisel Bilgi Tespit ve Maskeleme** sistemi. PDF, resim ve CSV dosyalarındaki hassas verileri otomatik olarak tespit edip maskeler.

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Modül Detayları](#modül-detayları)
- [Örnekler](#örnekler)
- [Teknik Detaylar](#teknik-detaylar)

---

## 🚀 Özellikler

### Ana Özellikler
- ✅ **Çoklu Format Desteği**: PDF, Resim (PNG, JPG, etc.), CSV
- 🔍 **Akıllı PII Tespiti**: Microsoft Presidio ile yapay zeka destekli tespit
- 🎭 **Otomatik Maskeleme**: Tespit edilen verileri otomatik gizleme
- 🖼️ **OCR Desteği**: Resimlerden metin çıkarma (Tesseract)
- 📊 **Detaylı Raporlama**: JSON ve konsol çıktısı
- 🎨 **Renkli Terminal**: Kullanıcı dostu görsel arayüz
- ⚡ **Performans Optimizasyonu**: Büyük CSV dosyaları için örnekleme desteği
- 🎯 **Güven Eşiği Ayarı**: Hassasiyet kontrolü (threshold)

### Tespit Edilebilen PII Türleri
- 👤 **Kişi İsimleri** (PERSON)
- 📧 **E-posta Adresleri** (EMAIL_ADDRESS)
- 📱 **Telefon Numaraları** (PHONE_NUMBER)
- 🏦 **Kredi Kartı Numaraları** (CREDIT_CARD)
- 🆔 **SSN/TC No** (US_SSN gibi)
- 📍 **Adres Bilgileri** (LOCATION)
- 🔢 **IP Adresleri** (IP_ADDRESS)
- 💳 **IBAN Numaraları**
- Ve daha fazlası...

---

## 📁 Proje Yapısı

```
presidio-image/
│
├── main.py                      # Ana uygulama ve CLI arayüzü
├── requirements.txt             # Python bağımlılıkları
│
├── analyzers/                   # Analiz modülleri
│   ├── pdf_analyzer.py         # PDF dosyaları için PII analizi
│   ├── image_analyzer.py       # Resim dosyaları için OCR + PII analizi
│   └── csv_analyzer.py         # CSV dosyaları için PII analizi
│
├── maskers/                     # Maskeleme modülleri
│   ├── pdf_masker.py           # PDF maskeleme (yeni PDF oluşturma)
│   └── image_masker.py         # Resim maskeleme (siyah kutular)
│
└── examples/                    # Örnek dosyalar
    ├── example_data.pdf
    ├── example_data.png
    ├── example_data.csv
    ├── example_data_masked.pdf
    ├── example_data_masked.png
    └── example_data_masked.csv
```

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Tesseract OCR (sistem seviyesinde kurulu olmalı)

### Adım 1: Tesseract Kurulumu

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
- [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki) adresinden indirin

### Adım 2: Python Ortamı

```bash
# Depoyu klonlayın veya indirin
cd presidio-image

# Virtual environment oluşturun (önerilen)
python3 -m venv venv

# Virtual environment'ı aktif edin
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Spacy dil modelini indirin (önemli!)
python -m spacy download en_core_web_lg
```

### Adım 3: Test Edin

```bash
python main.py examples/example_data.csv
```

---

## 🎯 Kullanım

### Temel Komutlar

```bash
# 1. Sadece analiz (PII tespiti)
python main.py dosya.pdf

# 2. Analiz + maskeleme (otomatik dosya adı: dosya_masked.pdf)
python main.py dosya.pdf --anonymize

# 3. Özel çıktı dosyası ile maskeleme
python main.py dosya.pdf --anonymize --output gizli_dosya.pdf

# 4. Resim maskeleme (siyah kutular ile)
python main.py foto.jpg --anonymize

# 5. CSV maskeleme
python main.py veriler.csv --anonymize

# 6. JSON rapor kaydetme
python main.py dosya.pdf --json rapor.json

# 7. Güven eşiği ayarlama (0.0-1.0 arası)
python main.py dosya.pdf --threshold 0.5

# 8. Büyük CSV için örnekleme
python main.py buyuk_veri.csv --sample-size 1000 --anonymize

# 9. Sadece belirli entity tiplerini tespit et
python main.py dosya.pdf --entities PERSON EMAIL_ADDRESS PHONE_NUMBER

# 10. JSON formatında çıktı al
python main.py dosya.pdf --format json

# 11. Sadece e-posta adreslerini maskele
python main.py veriler.csv --entities EMAIL_ADDRESS --anonymize

# 12. Tam iş akışı
python main.py veriler.csv --anonymize --json rapor.json --threshold 0.4
```

### Entity Filtreleme (Yeni Özellik!)

Artık hangi PII tiplerinin tespit edileceğini seçebilirsiniz! `--entities` parametresi ile sadece ilgilendiğiniz veri tiplerini tespit edebilirsiniz:

```bash
# Sadece kişi isimleri ve e-posta adresleri
python main.py dosya.pdf --entities PERSON EMAIL_ADDRESS

# Sadece iletişim bilgileri
python main.py foto.jpg --entities EMAIL_ADDRESS PHONE_NUMBER URL

# Sadece finansal bilgiler
python main.py belgeler.pdf --entities CREDIT_CARD IBAN_CODE US_BANK_NUMBER

# JSON çıktısı ile birlikte
python main.py data.csv --entities PERSON EMAIL_ADDRESS --format json
```

**Desteklenen Entity Tipleri:**
- `PERSON` - Kişi isimleri
- `EMAIL_ADDRESS` - E-posta adresleri
- `PHONE_NUMBER` - Telefon numaraları
- `CREDIT_CARD` - Kredi kartı numaraları
- `US_SSN` - Sosyal güvenlik numaraları
- `LOCATION` - Konum bilgileri
- `DATE_TIME` - Tarih ve saat
- `IP_ADDRESS` - IP adresleri
- `URL` - Web adresleri
- Ve daha fazlası...

Daha detaylı liste için `ENTITY_TYPES.md` dosyasına bakın.

**Avantajları:**
- ✅ **Daha hızlı analiz**: Sadece ihtiyacınız olan entity'leri kontrol eder
- ✅ **Daha az false positive**: İstemediğiniz tespitleri engeller  
- ✅ **Özelleştirilebilir**: Her dosya tipine göre farklı entity seçimi
- ✅ **Compliance**: Sadece yasal gerekliliklere uyan verileri maskele
```

### Parametreler

| Parametre | Kısa | Açıklama | Varsayılan |
|-----------|------|----------|------------|
| `file` | - | Analiz edilecek dosya (zorunlu) | - |
| `--anonymize` | `-a` | Maskelenmiş versiyon oluştur | False |
| `--output` | `-o` | Çıktı dosyası yolu | `[dosya]_masked.[ext]` |
| `--json` | `-j` | JSON rapor dosyası | - |
| `--sample-size` | `-s` | CSV için örnek boyutu | Tüm satırlar |
| `--threshold` | `-t` | Minimum güven skoru (0.0-1.0) | 0.35 |
| `--entities` | `-e` | Tespit edilecek entity tipleri | Tümü |
| `--format` | `-f` | Çıktı formatı (text/json) | text |
| `--no-summary` | - | Konsol özetini atla | False |

---

## 📦 Modül Detayları

### 1. `main.py` - Ana Uygulama

**Sınıf:** `PresidioAnalyzerCLI`

**Amaç:** Komut satırı arayüzü ve iş akışı koordinasyonu

**Ana Fonksiyonlar:**
- `get_file_type()`: Dosya uzantısına göre tip belirleme
- `analyze_file()`: Dosya analizi ve maskeleme koordinasyonu
- `print_results_summary()`: Sonuçları renkli konsola yazdırma
- `run()`: CLI argüman işleme ve ana akış

**Önemli Noktalar:**
- `colorama` ile renkli terminal çıktısı (platformlar arası uyumluluk)
- Otomatik dosya adı üretimi (`_masked` eki)
- Hata yönetimi ve kullanıcı dostu mesajlar
- JSON çıktısında büyük metin alanlarının boyut bilgisine dönüştürülmesi

---

### 2. `analyzers/pdf_analyzer.py` - PDF Analiz Modülü

**Sınıf:** `PDFAnalyzer`

**Amaç:** PDF dosyalarından metin çıkarıp PII tespit etme

**Ana Fonksiyonlar:**

#### `extract_text_from_pdf(pdf_path: str) -> str`
- **Görev:** PDF'den metin çıkarma
- **Kütüphane:** `pdfplumber` (PyPDF2'ye göre daha iyi metin çıkarma)
- **Detay:** Tüm sayfaları döngüyle okur, metinleri birleştirir

#### `analyze_text(text: str, threshold: float = 0.35) -> List[Dict]`
- **Görev:** Metinde PII tespiti
- **Motor:** Presidio AnalyzerEngine
- **Çıktı:** Entity tipi, metin, pozisyon, güven skoru

#### `anonymize_text(text: str, analyzer_results: List) -> str`
- **Görev:** Tespit edilen PII'ları maskeleme
- **Motor:** Presidio AnonymizerEngine
- **Detay:** Dict formatını RecognizerResult'a dönüştürür

#### `analyze_pdf(pdf_path: str, anonymize: bool, threshold: float) -> Dict`
- **Görev:** Tam PDF analiz iş akışı
- **Adımlar:**
  1. Metin çıkarma
  2. PII analizi
  3. (Opsiyonel) Anonymizasyon
- **Çıktı:** Detaylı sonuç dictionary'si

**Neden Bu Kod Yazıldı:**
PDF dosyaları iş dünyasında en çok kullanılan formattır. Sözleşmeler, faturalar, raporlar genelde PDF'dir ve kişisel bilgi içerebilir. Bu modül PDF'leri güvenli şekilde işler.

---

### 3. `analyzers/image_analyzer.py` - Resim Analiz Modülü

**Sınıf:** `ImageAnalyzer`

**Amaç:** Resimlerdeki metni OCR ile okuyup PII tespit etme

**Ana Fonksiyonlar:**

#### `extract_text_from_image(image_path: str) -> str`
- **Görev:** OCR ile metin çıkarma
- **Kütüphane:** `pytesseract` (Google Tesseract wrapper)
- **Detay:** PIL Image açar, Tesseract OCR uygular
- **Kullanım Alanları:** Fotoğraflar, taranmış belgeler, ekran görüntüleri

#### `get_image_info(image_path: str) -> Dict`
- **Görev:** Resim metadata bilgisi
- **Bilgiler:** Format, mod, boyut, genişlik, yükseklik
- **Neden:** Debug ve loglama için faydalı

#### `analyze_text()` ve `anonymize_text()`
- PDF analyzer ile aynı mantık
- Kod tekrarı yerine paylaşılan fonksiyonlar

#### `analyze_image(image_path: str, anonymize: bool, threshold: float) -> Dict`
- **Görev:** Tam resim analiz iş akışı
- **Özel Durum:** Resim metadata'sı da sonuçta döndürülür

**Neden Bu Kod Yazıldı:**
Kullanıcılar kimlik kartları, sürücü belgeleri, pasaportlar fotoğraflayabilir. Sosyal medyada paylaşılan ekran görüntüleri kişisel bilgi içerebilir. Bu modül bu riskleri tespit eder.

---

### 4. `analyzers/csv_analyzer.py` - CSV Analiz Modülü

**Sınıf:** `CSVAnalyzer`

**Amaç:** CSV/Excel tablolarında kolon bazlı PII analizi

**Ana Fonksiyonlar:**

#### `read_csv(csv_path: str, encoding: str = 'utf-8') -> pd.DataFrame`
- **Görev:** CSV okuma
- **Özellik:** Otomatik encoding düzeltme (UTF-8 hata verirse Latin-1 dener)
- **Neden:** Farklı kaynaklardan gelen CSV'ler farklı encoding'e sahip olabilir

#### `analyze_text(text: str, threshold: float = 0.35) -> List[Dict]`
- **Özellik:** Pandas NaN kontrolü (boş hücre kontrolü)
- **Detay:** Her hücre değerini string'e çevirip analiz eder

#### `analyze_dataframe(df: DataFrame, sample_size: int, threshold: float) -> Dict`
- **Görev:** Tüm DataFrame'i kolon bazlı analiz
- **Önemli Özellik:** Sampling (büyük dosyalar için)
- **Çıktı Yapısı:**
  ```python
  {
    "total_columns": int,
    "total_rows": int,
    "analyzed_rows": int,
    "is_sampled": bool,
    "column_results": {
      "column_name": {
        "has_pii": bool,
        "pii_count": int,
        "pii_types": {"PERSON": 5, "EMAIL": 3},
        "all_findings": [
          {
            "row_index": int,
            "value": str,
            "pii_findings": [...]
          }
        ]
      }
    }
  }
  ```

#### `anonymize_dataframe(df: DataFrame, threshold: float) -> DataFrame`
- **Görev:** Tüm DataFrame'i hücre hücre maskele
- **Performans:** Her hücre için ayrı analiz (büyük dosyalarda yavaş olabilir)
- **Çıktı:** Yeni bir DataFrame (orijinal değiştirilmez)

#### `analyze_csv()` - Ana İş Akışı
- CSV okuma → DataFrame analizi → İstatistik hesaplama → (Opsiyonel) Anonymizasyon → (Opsiyonel) Kaydetme

**Neden Bu Kod Yazıldı:**
CSV dosyaları veri biliminde, CRM sistemlerinde, Excel ihracatında sıkça kullanılır. Müşteri listeleri, kullanıcı veritabanları, anket sonuçları genelde CSV formatındadır. Her kolon farklı tip veri içerebilir, bu yüzden kolon bazlı analiz önemlidir.

---

### 5. `maskers/pdf_masker.py` - PDF Maskeleme Modülü

**Sınıf:** `PDFMasker`

**Amaç:** Maskelenmiş metni yeni PDF dosyası olarak kaydetme

**Ana Fonksiyonlar:**

#### `escape_html_entities(text: str) -> str`
- **Problem:** Reportlab, `<`, `>` karakterlerini HTML tag olarak yorumlar
- **Çözüm:** `<` → `&lt;`, `>` → `&gt;` dönüşümü
- **Örnek:** `<EMAIL_ADDRESS>` → `&lt;EMAIL_ADDRESS&gt;`

#### `create_masked_pdf(original_pdf_path: str, anonymized_text: str, output_path: str)`
- **Görev:** Yeni PDF oluşturma
- **Kütüphane:** `reportlab` (Python'da PDF oluşturma için standart)
- **Yapı:**
  - `SimpleDocTemplate`: PDF yapısı
  - `Paragraph`: Metin blokları
  - `Spacer`: Paragraflar arası boşluk
- **Stil:** 11pt font, 14pt satır aralığı, custom paragraph style
- **Detaylar:**
  - `\n\n` ile paragraf ayrımı
  - `\n` ile satır ayrımı → `<br/>` tag'ine dönüşüm
  - Gereksiz boşlukları temizleme

**Neden Bu Kod Yazıldı:**
Orijinal PDF'in layout'unu korumak zor olduğundan, maskelenmiş metin yeni bir PDF olarak oluşturulur. Bu, programatik olarak en güvenilir yöntemdir. Kullanıcı orijinal PDF ile maskelenmiş PDF'i karşılaştırabilir.

---

### 6. `maskers/image_masker.py` - Resim Maskeleme Modülü

**Sınıf:** `ImageMasker`

**Amaç:** Resim üzerinde tespit edilen PII'ların üzerine siyah kutular çizme

**Ana Fonksiyonlar:**

#### `get_text_boxes(image_path: str) -> Dict`
- **Görev:** Tesseract OCR ile her kelimenin koordinatlarını alma
- **API:** `pytesseract.image_to_data()` with `Output.DICT`
- **Çıktı:** Her kelime için x, y, width, height

#### `find_text_positions(ocr_data: Dict, text_to_mask: str) -> List[Dict]`
- **Görev:** Belirli bir metni OCR sonuçlarında bulma
- **Algoritma:**
  1. Her iki metni normalize et (küçük harf, boşluksuz)
  2. Kelime kelime karşılaştır
  3. Eşleşen kelimelerin koordinatlarını döndür
- **Önemli:** Partial matching yapıyor (örn: "John" içinde "ohn" da bulunur)

#### `create_masked_image(image_path: str, pii_findings: List, output_path: str, mask_color: str = 'black')`
- **Görev:** Maskelenmiş resim oluşturma
- **Adımlar:**
  1. Resmi PIL ile aç
  2. `ImageDraw` nesnesi oluştur
  3. Her PII için OCR koordinatlarını bul
  4. Her koordinat üzerine siyah dikdörtgen çiz
  5. 2 piksel padding ekle (kelimeleri tam kapsasın)
  6. Maskelenmiş resmi kaydet

**Teknik Detaylar:**
- PIL (Pillow) kullanarak in-memory image manipulation
- OCR ve maskeleme aynı resim üzerinde (koordinat eşleşmesi garanti)
- Mask color parametrik (siyah dışında blur da eklenebilir)

**Neden Bu Kod Yazıldı:**
Resimlerde metin maskelemek için iki yöntem var:
1. OCR + yeni resim oluşturma (zor, layout bozulur)
2. Orijinal resim üzerine çizim (bu yaklaşım)

İkinci yöntem daha hızlı, daha güvenilir ve orijinal resmin kalitesini korur.

---

## 🧪 Örnekler

### Örnek 1: PDF Analizi

```bash
python main.py examples/example_data.pdf
```

**Çıktı:**
```
===========================================================
  Presidio PII Analyzer
  Analyze PDF, Images, and CSV files for PII
===========================================================

Analyzing PDF file: examples/example_data.pdf
Please wait...

Analysis Results:
──────────────────────────────────────────────────────────
File: examples/example_data.pdf
PII Found: True
Total PII Instances: 8

PII Details:

  PERSON:
    - John Doe (confidence: 0.85)
    - Jane Smith (confidence: 0.90)

  EMAIL_ADDRESS:
    - john@example.com (confidence: 1.00)
    - jane@example.com (confidence: 1.00)

  PHONE_NUMBER:
    - +1-555-0123 (confidence: 0.95)
    ... and 3 more

──────────────────────────────────────────────────────────

✓ Analysis complete!
```

### Örnek 2: CSV Maskeleme

```bash
python main.py examples/example_data.csv --anonymize
```

**Orijinal CSV:**
```csv
Name,Email,Phone
John Doe,john@example.com,555-0123
Jane Smith,jane@example.com,555-0456
```

**Maskelenmiş CSV (`example_data_masked.csv`):**
```csv
Name,Email,Phone
<PERSON>,<EMAIL_ADDRESS>,<PHONE_NUMBER>
<PERSON>,<EMAIL_ADDRESS>,<PHONE_NUMBER>
```

### Örnek 3: Resim Maskeleme

```bash
python main.py examples/example_data.png --anonymize --output secure.png
```

**Sonuç:**
- Orijinal resim: `example_data.png`
- Maskelenmiş: `secure.png` (PII'lar üzerinde siyah kutular)

### Örnek 4: JSON Rapor

```bash
python main.py data.csv --json report.json --threshold 0.5
```

**JSON Çıktı:**
```json
{
  "file_path": "data.csv",
  "analysis": {
    "total_columns": 3,
    "total_rows": 100,
    "analyzed_rows": 100,
    "is_sampled": false,
    "column_results": {
      "Email": {
        "has_pii": true,
        "pii_count": 100,
        "pii_types": {
          "EMAIL_ADDRESS": 100
        }
      }
    }
  },
  "summary": {
    "columns_with_pii": 1,
    "total_pii_instances": 100
  }
}
```

---

## 🔬 Teknik Detaylar

### Microsoft Presidio Nedir?

**Presidio**, Microsoft tarafından geliştirilen açık kaynaklı PII tespit ve maskeleme kütüphanesidir.

**Çalışma Prensibi:**
1. **Pattern Matching**: Regex ile format tespiti (email, telefon, kredi kartı)
2. **Named Entity Recognition (NER)**: Spacy ile AI tabanlı isim tespiti
3. **Checksum Validation**: Luhn algoritması ile kredi kartı doğrulama
4. **Context Awareness**: "SSN:" yazısının yanındaki sayıları SSN olarak tanıma

**Desteklenen Modüller:**
- `presidio-analyzer`: PII tespiti
- `presidio-anonymizer`: PII maskeleme
- `presidio-image-redactor`: Resim redaksiyonu (bu projede kullanılmıyor, custom çözüm var)

### Spacy ve NLP

**Spacy** modern NLP kütüphanesidir. Bu projede `en_core_web_lg` modeli kullanılıyor:
- **lg** (large): 560MB boyut, yüksek doğruluk
- **Alternatifler:** `en_core_web_sm` (küçük, hızlı) veya `en_core_web_md` (orta)

**NER (Named Entity Recognition):**
- Cümledeki varlıkları tanır (PERSON, ORG, GPE, DATE, etc.)
- Machine learning ile eğitilmiş
- Türkçe için `tr_core_news_lg` modeli kullanılabilir

### Tesseract OCR

**Tesseract**, Google'ın açık kaynaklı OCR motorudur.

**Özellikler:**
- 100+ dil desteği
- Eğitilebilir (custom model eğitimi)
- Farklı Page Segmentation Modes (PSM)

**Bu Projede Kullanımı:**
```python
# Basit metin çıkarma
text = pytesseract.image_to_string(image)

# Koordinat bilgisiyle çıkarma
data = pytesseract.image_to_data(image, output_type=Output.DICT)
# data['text'], data['left'], data['top'], data['width'], data['height']
```

### Threshold (Güven Eşiği) Nedir?

**Threshold**, tespitin ne kadar emin olunması gerektiğini belirler (0.0 - 1.0).

**Örnekler:**
- `threshold=0.35` (varsayılan): Orta hassasiyet, daha fazla tespit
- `threshold=0.50`: Dengeli
- `threshold=0.70`: Yüksek hassasiyet, sadece çok emin olanlar
- `threshold=0.20`: Çok düşük, false positive (yanlış pozitif) artar

**Kullanım Senaryoları:**
- **Düşük threshold (0.2-0.4)**: Hiçbir PII kaçırılmasın
- **Yüksek threshold (0.6-0.8)**: Sadece kesin olanları maskele

### Encoding Sorunları

CSV modülünde encoding otomatik düzeltmesi var:

```python
try:
    df = pd.read_csv(csv_path, encoding='utf-8')  # İlk deneme
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding='latin-1')  # Alternatif
```

**Neden:** Windows Excel'den export edilen CSV'ler genelde Latin-1 (ISO-8859-1) encoding'e sahiptir.

### Sampling (Örnekleme)

Büyük CSV dosyaları için performans optimizasyonu:

```python
if sample_size and len(df) > sample_size:
    df_to_analyze = df.sample(n=sample_size, random_state=42)
```

**Örnek:**
- 1 milyon satırlık CSV → `--sample-size 10000` ile 10.000 satır analiz edilir
- `random_state=42`: Her çalıştırmada aynı örneklemi seçer (reproducible)

---

## 📊 Performans ve Sınırlamalar

### Performans

| Dosya Tipi | Boyut | Yaklaşık Süre | Notlar |
|------------|-------|---------------|--------|
| PDF | 10 sayfa | 5-10 saniye | Metin yoğunluğuna bağlı |
| Resim | 1920x1080 | 3-5 saniye | OCR süresi dominant |
| CSV | 10.000 satır | 30-60 saniye | Kolon sayısına bağlı |
| CSV | 100.000 satır | 5-10 dakika | Sampling önerilir |

### Sınırlamalar

1. **OCR Doğruluğu**: Düşük kaliteli resimler veya el yazısı metinler zor okunur
2. **PDF Layout**: Maskelenmiş PDF orijinal formatı korumaz
3. **Büyük Dosyalar**: CSV anonymizasyon tüm satırlar için tekrar analiz yapar (yavaş)
4. **Dil Desteği**: Sadece İngilizce NER modeli yüklü (Türkçe için ek kurulum gerekir)
5. **Bağlam**: Presidio her zaman bağlamı anlayamayabilir ("John" bir isim mi yoksa "John Doe Pizza" marka mı?)

### Optimizasyon İpuçları

```bash
# Büyük CSV için sampling kullan
python main.py large.csv --sample-size 5000

# Threshold yükselterek false positive'leri azalt
python main.py data.pdf --threshold 0.6

# JSON kaydetmeyerek çıktıyı hızlandır
python main.py data.csv --no-summary
```

---

## 🔐 Güvenlik ve Gizlilik

### Veri Güvenliği

✅ **Yerel İşleme**: Tüm analiz lokal makinede yapılır, veri internete gönderilmez
✅ **Orijinal Korunur**: Maskeleme yeni dosya oluşturur, orijinal değişmez
✅ **No API Calls**: Microsoft Presidio yerel çalışır, API key gerekmez

⚠️ **Dikkat Edilmesi Gerekenler:**
- Maskelenmiş dosyalar hassas bilgi içerebilir (threshold'a göre)
- JSON raporları PII örnekleri içerir (güvenli saklayın)
- OCR hatası yüzünden bazı PII'lar kaçabilir

### Önerilen İş Akışı

1. **Test Edin**: Önce örnek dosyalarla test edin
2. **Threshold Ayarı**: Veri tipinize göre optimize edin
3. **Manuel Kontrol**: Maskelenmiş dosyaları manuel kontrol edin
4. **Güvenli Saklama**: Raporları şifreli ortamda saklayın
5. **Log Temizliği**: Eski analiz sonuçlarını düzenli silin

---

## 🛠️ Geliştirme ve Katkı

### Yeni Entity Tipi Ekleme

Presidio'ya custom recognizer ekleyebilirsiniz:

```python
from presidio_analyzer import PatternRecognizer

tc_recognizer = PatternRecognizer(
    supported_entity="TR_ID_NUMBER",
    patterns=[{"name": "tc_pattern", "regex": r"\b[1-9]\d{10}\b", "score": 0.8}]
)

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(tc_recognizer)
```

### Hata Ayıklama

```python
# Debug modu için loglama ekleyin
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Etme

```bash
# Tüm örnek dosyaları test et
for file in examples/example_data.*; do
    echo "Testing: $file"
    python main.py "$file" --anonymize
done
```

---

## 📚 Kaynaklar

### Dokümantasyon
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [Spacy Documentation](https://spacy.io/usage)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

### İlgili Projeler
- [presidio-demo](https://github.com/microsoft/presidio-demo): Web UI demo
- [pdfplumber](https://github.com/jsvine/pdfplumber): PDF extraction
- [pytesseract](https://github.com/madmaze/pytesseract): Python Tesseract wrapper

---

## 🤝 Destek ve İletişim

### Sorun Giderme

**Problem:** Tesseract bulunamıyor
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

**Problem:** Spacy modeli yok
```bash
python -m spacy download en_core_web_lg
```

**Problem:** PDF okuma hatası
- pdfplumber yerine PyPDF2 deneyin
- PDF şifreli olabilir (şifre kaldırın)

**Problem:** Türkçe metin tespit edilmiyor
```bash
# Türkçe Tesseract dili
sudo apt-get install tesseract-ocr-tur  # Ubuntu
brew install tesseract-lang  # macOS

# Türkçe Spacy modeli
pip install spacy-tr-model
python -m spacy download tr_core_news_lg
```

---

## 📄 Lisans

Bu proje eğitim ve araştırma amaçlıdır. Ticari kullanım için ilgili kütüphanelerin lisanslarını kontrol edin:
- Presidio: MIT License
- Tesseract: Apache License 2.0
- Spacy: MIT License

---

## 🎓 Sonuç

Bu proje, **veri gizliliği** ve **GDPR/KVKK uyumluluğu** için güçlü bir araçtır. Özellikle:
- 📋 Veri paylaşımından önce PII temizleme
- 🔍 Compliance audit için PII tespiti
- 🎓 Veri bilimi projelerinde hassas veri maskeleme
- 📊 Test ortamları için anonymize veri setleri oluşturma

senaryolarında kullanılabilir.

---

**🔒 Güvenli veri işleme!**

