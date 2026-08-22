import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from valuation_engine import PropertyInput, calculate_valuation, get_reviewable_config

app = FastAPI(
    title="SaudiAqarAI API",
    description="Backend API for Saudi Arabia Real Estate Price Prediction",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_properties_store: list[dict] = []


class PredictRequest(BaseModel):
    city: str = Field(..., example="الرياض")
    neighborhood: str = Field(default="", example="النخيل")
    property_type: str = Field(default="شقة سكنية", example="فيلا")
    area: float = Field(..., gt=0, example=350.0)
    rooms: int = Field(default=4, ge=0)
    age: int = Field(default=0, ge=0)
    facade: str = Field(default="جنوبية", example="شرقية")
    street_width: float = Field(default=15.0, ge=0)
    location_grade: str = Field(default="حي متوسط", example="حي راقي")
    has_elevator: bool = False
    has_pool: bool = False
    has_driver_room: bool = False
    is_furnished: bool = False


class AddPropertyRequest(BaseModel):
    city: str
    neighborhood: str
    price: float = Field(..., gt=0)
    area: float = Field(..., gt=0)
    property_type: str = "شقة سكنية"


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "SaudiAqarAI Valuation Engine",
        "version": "3.0.0",
    }


@app.get("/api/health")
def health():
    return {"status": "online", "system": "SaudiAqarAI Engine 3.0"}


@app.get("/config/rates")
def config_rates():
    """Return all reviewable pricing/search values."""
    return get_reviewable_config()


@app.post("/predict")
def predict_price(data: PredictRequest):
    result = calculate_valuation(
        PropertyInput(
            city=data.city,
            neighborhood=data.neighborhood,
            property_type=data.property_type,
            area=data.area,
            rooms=data.rooms,
            age=data.age,
            facade=data.facade,
            street_width=data.street_width,
            location_grade=data.location_grade,
            has_elevator=data.has_elevator,
            has_pool=data.has_pool,
            has_driver_room=data.has_driver_room,
            is_furnished=data.is_furnished,
        )
    )

    return {
        "success": True,
        "predicted_price": result.predicted_price,
        "min_price": result.min_price,
        "max_price": result.max_price,
        "meter_price": result.meter_price,
        "investment_score": result.investment_score,
        "investment_grade": result.investment_grade,
        "investment_grade_key": result.investment_grade_key,
        "city_key": result.city_key,
        "adjustments": result.adjustments,
        "model_info": {
            "method": "rule-based market model",
            "last_reviewed": get_reviewable_config()["review_meta"]["last_reviewed"],
            "note": "Estimates only — not an official appraisal",
        },
    }


@app.get("/properties")
def list_properties():
    return {"success": True, "count": len(_properties_store), "properties": _properties_store}


@app.post("/properties")
def add_property(data: AddPropertyRequest):
    valuation = calculate_valuation(
        PropertyInput(
            city=data.city,
            neighborhood=data.neighborhood,
            property_type=data.property_type,
            area=data.area,
        )
    )

    entry = {
        "id": str(uuid.uuid4())[:8],
        "city": data.city,
        "neighborhood": data.neighborhood,
        "price": round(data.price),
        "area": data.area,
        "property_type": data.property_type,
        "meter_price": round(data.price / data.area),
        "ai_estimate": valuation.predicted_price,
        "variance_pct": round(abs(data.price - valuation.predicted_price) / valuation.predicted_price * 100, 1)
        if valuation.predicted_price
        else 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _properties_store.append(entry)
    return {"success": True, "property": entry}


@app.get("/export/csv")
def export_csv():
    if not _properties_store:
        raise HTTPException(status_code=404, detail="No properties to export")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "city", "neighborhood", "property_type", "area", "price", "meter_price", "ai_estimate", "variance_pct", "created_at"],
    )
    writer.writeheader()
    writer.writerows(_properties_store)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=saudiaqarai_properties.csv"},
    )


@app.get("/analytics/chart")
def analytics_chart():
    config = get_reviewable_config()
    cities = ["riyadh", "jeddah", "dammam", "makkah", "madinah"]
    labels = {"riyadh": "الرياض", "jeddah": "جدة", "dammam": "الدمام", "makkah": "مكة", "madinah": "المدينة"}
    return {
        "labels": [labels[c] for c in cities],
        "data": [config["city_base_rates"][c] for c in cities],
        "unit": "SAR/m²",
    }
