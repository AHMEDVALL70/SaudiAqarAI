# 🏢 SaudiAqarAI - Real Estate Valuation Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript)

**SaudiAqarAI** — محرك تقييم عقاري ذكي للمملكة العربية السعودية مع واجهة ثلاثية اللغات وBackend API موحّد.

---

## 🌟 المميزات

* **محرك تقييم موحّد** — نفس المنطق في Frontend و Backend (`valuation_engine.py`)
* **قيم بحث قابلة للمراجعة** — جدول مراجعة دورية لأسعار المتر والمعاملات
* **دعم ثلاث لغات** — العربية / English / Français مع RTL/LTR
* **API + وضع محلي** — يعمل مع FastAPI أو بدونه (localStorage fallback)
* **إضافة عقارات وتصدير CSV** — تخزين فعلي مع مقارنة السعر vs تقدير AI

---

## 🏗️ الهيكلية

```text
├── index.html              # الواجهة (HTML + CSS + JS)
├── valuation_engine.py     # محرك التقييم الموحّد + قيم البحث
├── main.py                 # FastAPI Backend
├── worker.js               # Cloudflare Worker (static assets)
├── requirements.txt
└── wrangler.toml
```

---

## 🚀 التشغيل المحلي

### Backend
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
API: `http://127.0.0.1:8000` — Docs: `http://127.0.0.1:8000/docs`

### Frontend
افتح `index.html` في المتصفح — يتصل تلقائياً بـ API على localhost.

---

## 📊 API Endpoints

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/config/rates` | قيم البحث القابلة للمراجعة |
| POST | `/predict` | تقييم عقار |
| GET/POST | `/properties` | قائمة / إضافة عقارات |
| GET | `/export/csv` | تصدير CSV |
| GET | `/analytics/chart` | بيانات الرسم البياني |

---

## ⚠️ Disclaimer
التقييمات استرشادية فقط — ليست وثيقة تثمين رسمية.

---

## 👤 Developer
**أحمد فال جمال الدين سيدنا** — [Innovision](https://ahmedvall70.github.io/Innovision/)
