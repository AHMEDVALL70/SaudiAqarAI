from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
import os
import json

app = FastAPI(title="عقارAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTACT_MESSAGES_PATH = os.path.join(BASE_DIR, "contact_messages.json")

# ============================================
# قائمة المدن السعودية
# ============================================

CITIES = [
    {"id": 1, "name": "الرياض", "region": "الوسطى"},
    {"id": 2, "name": "جدة", "region": "الغربية"},
    {"id": 3, "name": "مكة المكرمة", "region": "الغربية"},
    {"id": 4, "name": "المدينة المنورة", "region": "الغربية"},
    {"id": 5, "name": "الدمام", "region": "الشرقية"},
    {"id": 6, "name": "الخبر", "region": "الشرقية"},
    {"id": 7, "name": "الظهران", "region": "الشرقية"},
    {"id": 8, "name": "تبوك", "region": "الشمالية"},
    {"id": 9, "name": "أبها", "region": "الجنوبية"},
    {"id": 10, "name": "نجران", "region": "الجنوبية"},
    {"id": 11, "name": "حائل", "region": "الشمالية"},
    {"id": 12, "name": "بريدة", "region": "الوسطى"},
    {"id": 13, "name": "عنيزة", "region": "الوسطى"},
    {"id": 14, "name": "الطائف", "region": "الغربية"},
    {"id": 15, "name": "الجوف", "region": "الشمالية"},
]

# ============================================
# نموذج بيانات التواصل
# ============================================

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)


def _read_contact_messages() -> list:
    if not os.path.exists(CONTACT_MESSAGES_PATH):
        return []
    try:
        with open(CONTACT_MESSAGES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_contact_message(entry: dict) -> None:
    messages = _read_contact_messages()
    messages.append(entry)
    with open(CONTACT_MESSAGES_PATH, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# ============================================
# المسارات (Routes)
# ============================================

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>مرحباً بك في عقارAI</h1>")

@app.get("/license", response_class=HTMLResponse)
def get_license():
    license_path = os.path.join(BASE_DIR, "license.html")
    if os.path.exists(license_path):
        with open(license_path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="صفحة الترخيص غير موجودة")

@app.get("/cities")
def get_cities():
    """إرجاع قائمة المدن السعودية"""
    return {"cities": CITIES}

@app.get("/cities/{city_id}")
def get_city(city_id: int):
    """إرجاع مدينة محددة حسب ID"""
    city = next((c for c in CITIES if c["id"] == city_id), None)
    if city:
        return city
    raise HTTPException(status_code=404, detail="المدينة غير موجودة")

@app.get("/predict")
def predict(area: float = 100, bedrooms: int = 3, bathrooms: int = 2):
    if area <= 0:
        raise HTTPException(status_code=400, detail="المساحة يجب أن تكون أكبر من صفر")
    if bedrooms < 0 or bathrooms < 0:
        raise HTTPException(status_code=400, detail="عدد الغرف/الحمامات لا يمكن أن يكون سالباً")

    price = (area * 5000) + (bedrooms * 50000) + (bathrooms * 30000)
    return {
        "estimated_price": price,
        "currency": "SAR",
        "area_sqm": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms
    }

@app.post("/contact")
def submit_contact_message(payload: ContactMessage):
    """استقبال رسالة من نموذج (تواصل معنا) وحفظها"""
    entry = {
        **payload.model_dump(),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_contact_message(entry)
    return {"status": "ok", "message": "تم استلام رسالتك، بنرد عليك قريباً بإذن الله ✅"}

# ============================================
# تشغيل السيرفر (اختياري)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5500)
