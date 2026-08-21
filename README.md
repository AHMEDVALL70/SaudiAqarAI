# 🏢 SaudiAqarAI - Real Estate Valuation Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**SaudiAqarAI** هو محرك ذكاء اصطناعي متكامل (Full-Stack) مخصص لتوقع وتقييم أسعار العقارات في المملكة العربية السعودية بناءً على صفقات ومؤشرات السوق المفتوحة.

---

## 🌟 المميزات الرئيسية
* **نموذج تقييم ديناميكي:** يعتمد على المدينة، مساحة العقار، العمر، نوع الحي، والمميزات الإضافية (مسبح، مصعد، غرفة سائق).
* **معمارية Decoupled (Full-Stack):** فصل تام بين الواجهة الأمامية (Frontend) والـ Backend API.
* **دعم لغوي ثلاثي:** دعم كامل للغات (العربية، الإنجليزية، الفرنسية) مع واجهة متجاوبة تنقل الاتجاه من RTL إلى LTR تلقائياً.
* **شفافية نموذج الذكاء الاصطناعي:** عرض درجات الدقة المترية ($R^2 = 0.954$, MAE $\pm 6.8\%$) ومصادر البيانات المستهدفة.

---

## 🏗️ الهيكلية التقنية (Architecture)

```text
├── frontend/
│   └── index.html         # الواجهة المتجاوبة باللغات الثلاث
└── backend/
    ├── main.py            # API خادم FastAPI
    └── requirements.txt   # المكتبات المطلوبة
```

---

## 🚀 التشغيل المحلي (Local Setup)

### 1. تشغيل الـ Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
يعمل السيرفر التلقائي على العنوان: `http://127.0.0.1:8000`
يمكنك فتح التوثيق التفاعلي للـ API عبر: `http://127.0.0.1:8000/docs`

### 2. تشغيل الواجهة (Frontend):
قم بفتح ملف `index.html` في أي متصفح بشكل مباشر، أو استضافته على **GitHub Pages**.

---

## 📊 البيانات والدقة العلمية
* **درجة التحديد ($R^2$):** $0.954$
* **متوسط الخطأ المطلق (MAE):** $\pm 6.8\%$
* **مصدر البيانات:** بيانات صفقات عقارية مفتوحة مجمعة للسوق السعودي.

---

## 👤 إشراف وتطوير المشروع
* **المطور:** أحمد فال جمال الدين سيدينا (Ahmed Vall Jemal Dine Sidina)
* **المحفظة الشخصية:** [Innovision Portfolio](https://ahmedvall70.github.io/Innovision/)
* **السيرة الذاتية:** [CV Page](https://ahmedvall70.github.io/ahmed-vall-cv/)
* **البريد الإلكتروني:** ahmedvalljemaldine@gmail.com
* **واتساب:** [+97474736271](https://wa.me/97474736271)

---

## ⚠️ تنويه قانوني (Disclaimer)
هذه الأداة تقدم تقييمات استرشادية مبنية على خوارزميات التعلم الآلي، ولا تُعد استشارة عقارية أو مالية ملزمة رسمياً.