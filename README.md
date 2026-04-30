# 🎲 Mock Data Generator Agent

## Project Overview
Mock Data Generator Agent, kullanıcı tarafından yüklenen örnek veriden veya sıfırdan tanımlanan kolonlardan **gerçekçi sentetik veri setleri** üretmek üzere tasarlanmış bir veri üretim modülüdür.

İki tamamlayıcı modu vardır: **Upload mode** (yüklenen örnek dosyanın şemasını otomatik çıkarır ve aynı yapıda yeni veri üretir) ve **Scratch mode** (sıfırdan kolon-kolon tanımlanan veri setini sıfırdan inşa eder). Her iki mod da aynı üretim motoru, aynı gürültü/kalite kontrolleri ve aynı export seçeneklerini (CSV, Excel, JSON) kullanır. Test, demo, eğitim ve geliştirme süreçleri için **production verisine alternatif** sağlar.

> ⚠️ **LLM entegrasyonu kullanılmaz.** Mevcut versiyon tamamen kural tabanlı (rule-based) ve istatistiksel üretim üzerine kuruludur. Faker kütüphanesi kullanıcı tarafında dağıtılan deterministik kalıplarla çalışır; dış AI servislerine bağımlılık yoktur.

---

## 🎯 Project Purpose
Kurumsal ortamlarda — özellikle bankacılıkta — **gerçek veriye gizlilik ve uyum nedenleriyle erişim sınırlıdır**. Mock Data Generator, geliştirme, test, demo ve eğitim süreçlerinde **gerçek veri açığa çıkmadan** çalışmak için güvenli bir alternatif üretir.

Sadece rastgele veri üretmenin ötesine geçerek, **şema tutarlılığı, kolon tipi uyumluluğu, kategorik ağırlık dağılımları, korelasyon kuralları, iş kuralları ve gürültü modlarını** destekleyerek üretilen verinin **gerçek dünyaya benzer davranmasını** hedefler.

---

## 👥 Target Use Cases

### 1. Development & Testing
- Production verisi olmadan unit / integration test
- Performans testlerinde gerçekçi büyüklükte veri (1M satıra kadar)
- Edge-case test verisi (gürültülü mod ile)

### 2. Demo & Training
- Müşteri / iç ekip demolarında gerçekçi veri ile sunum
- Eğitim materyallerinde anonimleştirilmiş veri seti
- Onboarding sürecinde yeni ekip üyelerine güvenli veri paylaşımı

### 3. Data Pipeline & ML Prototyping
- ML pipeline geliştirmede şemaya uyumlu mock veri
- Schema migration testlerinde format ve tip uyumluluğu doğrulama
- Diğer AI Hub agent'larına (anomaly-detection, segment-intelligence vb.) input olarak kullanım

---

## ⚙️ End-to-End Workflow

Uygulama ana sayfa (mode picker) ile başlar; iki mod 3 adımlı sihirbaz olarak ilerler.

### Upload Mode (örnek dosyadan ölçekleme)

1. **Yükleme** — Kullanıcı CSV / Excel dosyası yükler; önizleme + istatistikler gösterilir.
2. **Şema Analizi** — `analyzer/schema_analyzer.py` her kolonu profiller:
   - Tip tespiti: `numeric_int / numeric_float / categorical / datetime / boolean / text / faker / id / pattern`
   - İstatistik çıkarımı (min/max/mean/std, dağılım, ağırlık)
   - Faker hint tespiti (kolon adı regex eşleşmesi: email, phone, city, vb.)
3. **Yapılandırma** — Her kolon için interaktif kart:
   - Tip override
   - Faker provider seçimi
   - Tip-spesifik parametreler (numeric: min/max/mean/std, datetime: tarih aralığı, vb.)
4. **Genel Ayarlar (sidebar)** — satır sayısı, Faker locale, kalite modu, iş kuralları, korelasyon kuralları
5. **Üretim** — Engine kolonları üretir, korelasyonları uygular, iş kurallarını filtreler, gürültüyü enjekte eder
6. **Karşılaştırma & Export** — Orijinal vs üretilen istatistikler yan yana; CSV / Excel / JSON indirme

### Scratch Mode (sıfırdan tasarım)

1. **Veri Seti Ayarları** — satır sayısı, başlangıç kolon sayısı, Faker locale
2. **Sütun Tanımlama** — Her kolon için modüler kart:
   - Kullanıcı dostu tip seçimi (Tam Sayı, Ondalık, Kategorik, E-posta, Telefon, İsim, ID, Özel Desen, vb.)
   - Tip-spesifik parametreler
   - `nullable` ve `unique` flag'leri
3. **Üretim** — Aynı engine, aynı export seçenekleri (orijinal-üretilen karşılaştırma yok)

---

## 🧩 Architecture Overview

**Core Layers:**

- **Analyzer Layer (`analyzer/schema_analyzer.py`)**
  Yüklenen veri setinin şemasını çıkarır: kolon tipi tespiti, istatistik üretimi, Faker hint regex eşleşmesi. `format="mixed"` ile mixed-format datetime kolonlarını da güvenli şekilde tanır (`errors="coerce"` ile bozuk değerleri atar).

- **Generator Layer (`generator/`)**
  Tip başına bağımsız üretici modüller:
  - `numeric.py` — normal / uniform dağılım, sequential mod, IQR clip
  - `categorical.py` — değer + ağırlık tabanlı sampling
  - `datetime_gen.py` — tarih aralığı, business days, sequential
  - `boolean_gen.py` — true_ratio, format (True/False, Yes/No, Evet/Hayır, 1/0)
  - `text.py` — Faker provider veya rastgele metin
  - `id_gen.py` — prefix + zero-padded sequential / random unique ID
  - `pattern_gen.py` — regex-benzeri pattern (`#` rakam, `@` büyük harf, `&` küçük harf, vb.)
  - `correlations.py` — rank tabanlı pozitif/negatif korelasyon enjeksiyonu
  - `noise.py` — null/outlier/duplicate/typo/whitespace/format inconsistency
  - `engine.py` — orchestrator: tüm üreticileri sıraya koyup iş kurallarını uygular

- **UI Layer (`ui/`)**
  Streamlit sayfa mimarisi: home → mode → 3-step wizard. Yeniden kullanılabilir bileşenler (`components.py`).

- **Utils Layer (`utils/`)**
  I/O helper'ları (CSV/Excel okuma, çıktı bytes), sabitler (TYPE_OPTIONS, USER_TYPES, FAKER_PROVIDERS, LOCALE_OPTIONS), Streamlit version compat.

---

## 🤖 Model & Technology Stack

### Generation Approach
- Klasik istatistiksel üretim (NumPy random distributions)
- Faker tabanlı gerçekçi metin (name, email, phone, city, IBAN, vb.)
- Pattern tabanlı string üretimi (regex-benzeri sembol dili)
- Rank tabanlı korelasyon enjeksiyonu (Spearman benzeri)
- Pandas query ile iş kuralı filtresi

### Backend & UI
- Python (3.10+)
- Pandas / NumPy
- Faker (locale: en_US, tr_TR, de_DE, fr_FR, es_ES)
- Streamlit (UI)
- OpenPyXL (Excel export)

---

## 🧠 Generation Strategy

Mock veri üretimi **tip uyumluluğu, istatistiksel benzerlik ve kontrol edilebilirlik** üzerine kuruludur:

- **Şema sadakati** — Upload modunda orijinal kolon tipleri, dağılımları ve null oranları korunur
- **Kullanıcı kontrolü** — Otomatik tespitin üzerine her kolon için manuel override mümkün
- **Gürültü ayarlanabilir** — "Temiz" mod default; "Gerçek Dünya (Gürültülü)" modu null/outlier/duplicate/typo/whitespace/format inconsistency oranlarını ayrı ayrı kontrol eder
- **Korelasyon enjeksiyonu** — Sayısal kolonlar arası rank tabanlı pozitif/negatif korelasyon (0–1 strength)
- **İş kuralı filtreleri** — Pandas query syntax (`age >= 18 and salary > 0`); 3 retry ile yeterli satır toplanmaya çalışılır
- **Uniqueness garantisi** — `unique=True` flag'li kolonlarda 5 retry ile dup eliminate

LLM kullanılmaz — tüm üretim deterministik (random seed olmadan da tekrarlanabilir karakteristik) ve dış servis bağımlılığı yoktur.

---

## 📊 Example Output

Her üretim oturumunda sistem aşağıdaki çıktıları üretir:

### Ekran Üstü
- Üretilen satır / sütun / null sayımları
- İlk 100 satır önizlemesi
- Sütun bazlı tip + boş değer + benzersiz değer özeti
- (Upload modunda) Orijinal ve üretilen veri yan yana istatistik karşılaştırması: numeric için describe, categorical için bar chart, boolean için True/False sayıları

### Indirme Çıktıları
- `sentetik_veri.csv` — UTF-8 CSV
- `sentetik_veri.xlsx` — Excel (openpyxl), tek sheet
- `sentetik_veri.json` — pretty-printed records (`force_ascii=False` Türkçe karakter desteği için)

### Desteklenen Tip ve Formatlar

| Tip | Üretilen Değer Örneği |
|-----|----------------------|
| `numeric_int` | 25, 47, 33 (normal dist, min=18, max=70) |
| `numeric_float` | 12345.67 (decimals=2, allow_negative=True) |
| `categorical` | "Bireysel" / "Ticari" / "Kurumsal" (ağırlıklı sampling) |
| `datetime` | 2024-03-15 (start/end aralığında, business_days_only opsiyonel) |
| `boolean` | True / False, Yes / No, Evet / Hayır, 1 / 0 |
| `faker.email` | jdoe@example.com |
| `faker.phone_number` | (641)972 1729 |
| `id` | CUST-000001, CUST-000002 (prefix + zero-pad) |
| `pattern` | "AB-1234-XY" (`@@-####-@@` pattern) |
| `text` | Faker sentence/text/word avg_length'e göre |

---

## 🔐 Banking & Compliance Considerations

- **Production verisi gerekmez** — Kullanım amacının özünü oluşturur; tüm üretim deterministik kalıplardan ve istatistiklerden gelir
- Yüklenen örnek dosya **lokal olarak işlenir**, dış servise gönderilmez
- LLM kullanımı yoktur — gizli/hassas veri içeren prompt riski yoktur
- Faker provider'ları **gerçek kişilere ait olmayan** kalıplardan üretir (random isim/email/telefon)
- Excel/CSV/JSON çıktıları kurumsal denetim ve paylaşım için hazır formattadır
- 1.000.000 satıra kadar üretim destekli; bellek limiti uyarısı 500.000 satırda gösterilir
- ID kolonları zero-padded sequential olarak gerçek müşteri ID kalıplarına benzeyecek şekilde tasarlanır ama tamamen sentetiktir

---

## 🚀 Business Impact

- Geliştirme ve test süreçlerinde **production verisine bağımlılığı ortadan kaldırır**
- Demo ve eğitimlerde gerçekçi veri ile sunum kolaylığı sağlar
- ML model prototiplemede schema-uyumlu mock dataset üretir
- Veri ekipleri için onboarding sürecini hızlandırır
- 1M satıra kadar performans testleri için gerçekçi veri sağlar
- AI Hub içindeki diğer agent'lara (anomaly-detection, segment-intelligence, forecasting) input olarak kullanılabilir
- Korelasyon ve iş kuralları sayesinde üretilen veri downstream model davranışını gerçekçi şekilde test eder

---

## 🔮 Future Enhancements

- LLM tabanlı kolon adından akıllı tip önerme
- Multi-column constraint (örn. yas + dogum_tarihi tutarlılık)
- Time-series sentetik veri üretimi (trend + sezonsallık + gürültü)
- Reproducibility: random seed kontrolü ile tekrarlanabilir üretim
- Schema export/import: konfigürasyon JSON olarak kaydedilip paylaşılabilir
- Domain-spesifik şablonlar (banking, e-commerce, healthcare)
- Differential privacy garantileri (k-anonymity, ε-DP)
- Datetime için saat-dakika dağılımı (rush hour vb.) modellemesi
