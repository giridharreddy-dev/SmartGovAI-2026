# SmartGov Health – आंध्र प्रदेश स्वास्थ्य योजनाएं

**अंग्रेजी में नीचे है | English below**

---

## 📱 تطبيق ذكي لمساعدة المناطق الريفية في الوصول إلى مخططات الصحة الحكومية

SmartGov Health ایک **آفلائن-فرسٹ PWA** ہے جو **کم سواد والے دیہاتی لوگوں** کے لیے ڈیزائن کیا گیا ہے جو سست انٹرنیٹ یا آفلائن ہو سکتے ہیں۔

## 🎯 تمام خصوصیات

- ✅ **آفلائن-فرسٹ PWA** – ایک بار ڈاؤن لوڈ کریں، ہمیشہ کام کریں
- ✅ **تیلوگو میں مکمل آواز ریڈنگ** – Web Speech API + براؤزر TTS فال بیک
- ✅ **بڑے ٹیپ ہدف** – 48px+ تمام بٹن (موٹے انگلیوں کے لیے)
- ✅ **آفلائن آڈیو** – تمام MP3s محفوظ رہتے ہیں (رن ٹائم gTTS نہیں)
- ✅ **سادہ UI** – موبائل پر ایک کالم، لیپ ٹاپ پر دو کالم
- ✅ **moreAndhra Pradesh** – ایکسپنڈر کے پیچھے اختیاری خصوصیات
- ✅ **SMS + WhatsApp شیئر** – `sms:` پروٹوکول کے ساتھ
- ✅ **مقامی ڈیٹا ہسٹری** – localStorage میں سوالوں/چیک لسٹ
- ✅ **ایک کلک رپورٹ** – غلط معلومات کی رپورٹنگ

---

## 🚀 سیٹ اپ کی ہدایات (5 منٹ)

### مرحلہ 1: ضروری چیزیں انسٹال کریں

```bash
# Python 3.9+ کے ساتھ کلون/ڈاؤن لوڈ کریں
cd SmartGovAI2

# ورچوئل ماحول بنائیں
python -m venv myenv

# فعال کریں
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# منحصر انسٹال کریں
pip install -r requirements.txt
```

### مرحلہ 2: ایک بار MP3 آڈیو بنائیں

```bash
python generate_audio.py
```

یہ تمام `schemes_complex.json` میں ہر یوجنا کے لیے تیلوگو MP3 فائلیں بناتا ہے۔ **صرف ایک بار (یا جب نئی یوجنائیں شامل کریں)**

### مرحلہ 3: ایپ چلائیں

```bash
python app.py
```

برقرار `http://localhost:5000`

### مرحلہ 4: PWA بند کریں (آفلائن استعمال)

**موبائل**:
1. `http://localhost:5000` کھولیں
2. شیئر → **ہوم اسکرین میں شامل کریں** نل کریں
3. آفلائن جائیں → ایپ کام کرتی ہے! ✅

**لیپ ٹاپ/ڈیسک ٹاپ**:
- یوں `/install` بٹن کو دیکھیں → کلک کریں

---

## 🔧 اختیاری: Gemini API (PDF تبدیلی کے لیے)

PDF دستاویزات کو سادہ کرنے کے لیے اگر آپ کو Gemini کی ضرورت ہے:

```bash
# .env بنائیں
echo "GEMINI_API_KEY=your_key_here" > .env
```

[Google AI Studio سے اپنی کلید حاصل کریں](https://aistudio.google.com)

**بغیر API**: **مقررہ یوجنائیں** (جو `schemes_complex.json` میں ہیں) کام کرتی رہتی ہیں!

---

## 📋 صارف کی بنیادی سہولیات

### 🔍 **یوجنا تلاش**
- تیلوگو میں ٹائپ کریں یا **🎙️ مائک** دبائیں
- تاریخ خود بخود محفوظ ہوتی ہے

### 📖 **اس صفحے کو پڑھیں**
- **🔊 ہندی پیڑھ صفحہ** بٹن دبائیں
- Web Speech یا براؤزر TTS استعمال کرتا ہے

### 📱 **شیئر کریں**
- **WhatsApp**: `📱 WhatsApp` بٹن
- **SMS**: `📲 SMS` بٹن (پہلے سے متن بھرا ہوا)

### ⚠️ **غلط معلومات کی رپورٹ کریں**
- **📋 غلط معلومات رپورٹ کریں** (فٹ ر)
- یا **سسائ** بٹن (نتائج میں)

### ✓ **فارم بھریں**
- **🎯 اہلیت جانچ** – ہاں/نہیں کے سوالات
- **📋 دستاویز چیک لسٹ** – نقل کے لیے بکس
- **🖨️ پرنٹ** کریں یا **💾 محفوظ کریں**

---

## 🛠️ ڈویلپر معلومات

### فائل ڈھانچہ

```
SmartGovAI2/
├── app.py                    # Flask سرور
├── generate_audio.py         # آڈیو بنانے والا (1 بار چلائیں)
├── requirements.txt          # منحصر
├── schemes_complex.json      # تمام یوجنائیں
├── database.py               # DB سیٹ اپ
├── static/
│   ├── service-worker.js     # آفلائن کیشنگ (Stale-While-Revalidate)
│   ├── enhanced-features.js  # JS افعال
│   ├── audio/                # MP3 فائلیں (generate_audio.py سے)
│   └── manifest.webmanifest  # PWA میٹا ڈیٹا
└── templates/
    ├── index.html            # مرکزی UI
    ├── offline.html          # آفلائن فال بیک
    └── analytics.html        # اختیاری اعدادوشمار
```

### اہم رائوٹ

```
POST /simplify              # یوجنا معلومات حاصل کریں
POST /eligibility-check     # اہلیت سکور کریں
POST /whatsapp-share        # WhatsApp متن
POST /staff-report          # مسائل رپورٹ کریں
GET  /offline-cache         # آفلائن ڈیٹا
GET  /healthz               # ہیلتھ چیک
```

### Service Worker

- **Stale-While-Revalidate**: کیش سے فوری ڈیٹا، پس منظر میں نیا
- **تمام `.mp3` محفوظ رہتے ہیں**
- **آفلائن صفحہ**: `/offline.html`

---

## 📦 منحصر

```
flask                  # سرور
google-genai           # اختیاری: Gemini PDF API
pdfplumber             # PDF ٹیکسٹ نکالنا
gtts                   # تیلوگو آڈیو بنانا
python-dotenv          # .env لوڈ کریں
pytesseract (opt)      # OCR
pdf2image (opt)        # PDF سے تصویریں
```

---

## 🎨 UI خصوصیات

| خصوصیت | تفصیلات |
|-----------|----------|
| **رنگ پیلٹ** | سبز (ہندی), سنہری, نیلی, سرخ |
| **فونٹ** | Noto Sans تیلوگو (ڈیفالٹ) |
| **تمام بٹن** | 48px+ تاکہ موٹے انگلیاں کام کریں |
| **ریسپانسیو** | 560px تک موبائل, 860px تک ٹیبلٹ, 1120px تک ڈیسک ٹاپ |

---

## 🚨 خرابی سے نمٹنا

### Gemini API ناکام ہو گئی?
✅ مقررہ یوجنائیں **کام جاری رکھتی ہیں** (کوئی API نہیں)

### انٹرنیٹ نہیں ہے؟
✅ **آفلائن مسٹ** – کیش شدہ ڈیٹا دیکھیں

### آڈیو ناکام؟
✅ **براؤزر TTS** فال بیک – **🔊 یہ صفحہ پڑھیں** کے ذریعے

### PWA انسٹال نہیں ہو رہا؟
- اہم: **HTTPS کے ذریعے سرو کریں** (یا localhost) 
- Service Worker کو آپ کے براؤزر کے ٹول میں دیکھیں

---

## 📊 ڈیٹا بیس

- **feedback.db**: صارف کی رائے و تجاویز اور رپورٹیں
- **localStorage**: ہر صارف کے اہلیت سوالات + چیک لسٹ (براؤزر میں)

---

## 🌐 تنشر (Production)

```bash
# ہموار سرور کے ساتھ:
gunicorn app:app -w 4 -b 0.0.0.0:5000

# یا Docker:
docker build -t smartgov . && docker run -p 5000:5000 smartgov
```

---

## 📝 لائسنس

عوامی ڈومین – **مفت استعمال کریں!**

---

## 💬 معاونت

مسائل:
- GitHub Issues
- ای میل: support@smartgov.example
- WhatsApp: `reportIssue()` استعمال کریں

---

---

# 🇮🇳 SmartGov Health - English Version

A **modern, offline-first Progressive Web App (PWA)** designed specifically for **low-literacy rural villagers in Andhra Pradesh** to access government health schemes easily.

## ✨ Key Features

✅ **Offline-First PWA** – Download once, works forever (even without internet)  
✅ **Full Telugu Voice Navigation** – Web Speech API with browser TTS fallback  
✅ **Large Tap Targets** – All buttons 48px+ (designed for fat fingers)  
✅ **Pre-Generated Audio** – All MP3 files created offline (no runtime gTTS)  
✅ **Dead Simple UI** – Single column on mobile, two-column on laptop  
✅ **Advanced Features Hidden** – Behind "More" expanders (clean interface)  
✅ **SMS + WhatsApp Sharing** – Share schemes instantly  
✅ **Local Data Persistence** – Eligibility answers & checklists saved locally  
✅ **One-Click Issue Report** – Report incorrect info with device details  
✅ **Robust Error Handling** – Works offline, shows cached data if Gemini fails  

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd SmartGovAI2

# Create virtual environment (Python 3.9+)
python -m venv myenv

# Activate
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Generate MP3 Audio Files (One-Time)

```bash
python generate_audio.py
```

This creates all Telugu MP3 files from `schemes_complex.json`. **Run only once** or when adding new schemes.

### Step 3: Start the App

```bash
python app.py
```

Open `http://localhost:5000`

### Step 4: Install as PWA (Offline Use)

**On Mobile:**
1. Open `http://localhost:5000`
2. Tap Share → **Add to Home Screen**
3. Go offline → App still works! ✅

**On Desktop:**
- Click the install button in the address bar

---

## 🔐 Optional: Gemini API (PDF Simplification)

To simplify PDF documents with AI:

```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key" > .env
```

Get your key from [Google AI Studio](https://aistudio.google.com)

**Without API:** Built-in health schemes (in `schemes_complex.json`) still work perfectly!

---

## 📱 User Guide

### 🔍 Search for a Scheme
- Type in Telugu or English
- Click 🎙️ microphone to speak
- Your search history is auto-saved

### 📖 Listen to Page Content
- Click **🔊 Read this page aloud** button
- Uses Web Speech API or browser TTS
- Automatically saves reading state

### 📱 Share with Friends
- **WhatsApp** → 📱 WhatsApp button
- **SMS** → 📲 SMS button (pre-filled message with `sms:` protocol)

### ⚠️ Report Wrong Information
- Click **📋 Report wrong info** (footer)
- Or use **⚠️ Issue** button in result panel
- Sends via WhatsApp with device/scheme info

### ✅ Fill Out Forms
- **🎯 Eligibility Checker** – Yes/No questions
- **📋 Document Checklist** – Track documents needed
- **🖨️ Print** or **💾 Save** locally

---

## 🛠️ Developer Guide

### File Structure

```
SmartGovAI2/
├── app.py                      # Flask backend
├── generate_audio.py           # MP3 generator (run once)
├── requirements.txt            # Dependencies
├── schemes_complex.json        # All schemes data
├── database.py                 # Database setup
├── static/
│   ├── service-worker.js       # Offline caching (Stale-While-Revalidate)
│   ├── enhanced-features.js    # Client-side features
│   ├── audio/                  # MP3 files (generated by generate_audio.py)
│   └── manifest.webmanifest    # PWA metadata
└── templates/
    ├── index.html              # Main UI
    ├── offline.html            # Offline fallback page
    └── analytics.html          # Optional usage stats
```

### API Routes

```
POST /simplify              # Get scheme details
POST /eligibility-check     # Score eligibility
POST /whatsapp-share        # Get WhatsApp message
POST /staff-report          # Report issues
GET  /offline-cache         # Offline data
GET  /healthz               # Health check
```

### Service Worker Strategy

- **Stale-While-Revalidate**: Return cached data immediately, fetch fresh in background
- **Audio files cached** – All `.mp3` files stored for offline
- **Offline page** – `/offline.html` shown when navigation fails

---

## 📦 Dependencies

```
flask                  # Web framework
google-genai           # Optional: PDF simplification
pdfplumber             # PDF text extraction
gtts                   # Telugu text-to-speech
python-dotenv          # Environment variables
pytesseract (optional) # OCR support
pdf2image (optional)   # PDF to image conversion
```

---

## 🎨 UI Design

| Aspect | Details |
|--------|---------|
| **Colors** | Green (primary), Orange, Blue, Red |
| **Font** | Noto Sans Telugu (default system fonts) |
| **Min Tap Targets** | 48px for all buttons |
| **Breakpoints** | Mobile <560px, Tablet <860px, Desktop 1120px max |
| **Accessibility** | High contrast, large text, no hover-dependent UI |

---

## ❌ Error Handling

### Gemini API fails?
✅ Built-in schemes **still work** (no API needed)

### No internet?
✅ **Offline mode** – Shows cached schemes

### Audio file missing?
✅ **Browser TTS fallback** – "🔊 Read page aloud" button works

### PWA won't install?
- Make sure you're on **HTTPS** (or localhost)
- Check browser DevTools → Application → Service Workers

---

## 💾 Data Storage

- **feedback.db**: User feedback and issue reports
- **localStorage**: User's eligibility answers + document checklist per scheme

---

## 🌍 Production Deployment

```bash
# With gunicorn:
pip install gunicorn
gunicorn app:app -w 4 -b 0.0.0.0:5000

# With Docker:
docker build -t smartgov . && docker run -p 5000:5000 smartgov

# With Nginx (reverse proxy):
# See NGINX config in deployment/ folder
```

---

## 📝 License

**Public Domain** – Free to use and modify for any purpose.

---

## 🤝 Support

**Issues?**
- GitHub Issues
- Email: support@smartgov.health
- Use the in-app **Report Issue** button

**Contributing?**
- Fork → Make changes → Submit PR

---

## 📚 Documentation Files

- [FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md) – Complete feature list
- [BUG_FIXES.md](BUG_FIXES.md) – Recent fixes and improvements
- [USER_GUIDE.md](USER_GUIDE.md) – Detailed user instructions

---

**Last Updated**: June 2026  
**Made with ❤️ for Rural India**
