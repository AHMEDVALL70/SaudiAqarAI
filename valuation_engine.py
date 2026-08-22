"""
SaudiAqarAI — Unified Valuation Engine
All pricing/search values are centralized here for review and maintenance.
Last reviewed: March 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ─────────────────────────────────────────────
# REVIEWABLE MARKET VALUES (update quarterly)
# ─────────────────────────────────────────────

REVIEW_META = {
    "last_reviewed": "2026-03-01",
    "next_review": "2026-06-01",
    "data_source": "Saudi Real Estate Market Indicators 2025-2026",
    "note": "Base rates are SAR per m² — review against official market reports",
}

CITY_BASE_RATES: dict[str, float] = {
    "riyadh": 4800,
    "jeddah": 4500,
    "dammam": 3900,
    "makkah": 5200,
    "madinah": 4100,
}

CITY_ALIASES: dict[str, str] = {
    "الرياض": "riyadh",
    "riyadh": "riyadh",
    "جدة": "jeddah",
    "jeddah": "jeddah",
    "الدمام": "dammam",
    "dammam": "dammam",
    "مكة المكرمة": "makkah",
    "makkah": "makkah",
    "meca": "makkah",
    "المدينة المنورة": "madinah",
    "madinah": "madinah",
}

PROPERTY_TYPE_MULTIPLIERS: dict[str, float] = {
    "villa": 1.30,
    "فيلا": 1.30,
    "apartment": 1.00,
    "شقة سكنية": 1.00,
    "land": 0.85,
    "أرض": 0.85,
    "duplex": 1.15,
    "دوبلكس": 1.15,
}

FACADE_ADJUSTMENTS: dict[str, float] = {
    "east": 1.05,
    "شرقية": 1.05,
    "north": 1.04,
    "شمالية": 1.04,
    "south": 1.00,
    "جنوبية": 1.00,
    "west": 0.98,
    "غربية": 0.98,
}

DISTRICT_GRADE_ADJUSTMENTS: dict[str, float] = {
    "prime": 1.25,
    "حي راقي": 1.25,
    "investment": 1.15,
    "حي استثماري": 1.15,
    "medium": 1.00,
    "حي متوسط": 1.00,
}

AMENITY_ADJUSTMENTS: dict[str, float] = {
    "elevator": 1.04,
    "pool": 1.08,
    "driver_room": 1.03,
    "furnished": 1.10,
}

STREET_WIDTH_TIERS: list[tuple[float, float]] = [
    (30, 1.08),
    (20, 1.05),
    (15, 1.02),
    (10, 1.00),
    (0, 0.97),
]

DEPRECIATION_RATE = 0.008
MIN_DEPRECIATION_FACTOR = 0.55
ROOMS_BASELINE = 3
ROOMS_ADJUSTMENT = 0.025
PRICE_RANGE_MARGIN = 0.05

PREMIUM_NEIGHBORHOOD_KEYWORDS: dict[str, float] = {
    "النخيل": 1.06,
    "الملقا": 1.08,
    "العليا": 1.07,
    "الروضة": 1.05,
    "الشاطئ": 1.06,
    "الفيصلية": 1.05,
    "اليرموك": 1.04,
    "الحمراء": 1.05,
    "الخليج": 1.04,
}


@dataclass
class PropertyInput:
    city: str
    neighborhood: str = ""
    property_type: str = "apartment"
    area: float = 100.0
    rooms: int = 3
    age: int = 0
    facade: str = "south"
    street_width: float = 15.0
    location_grade: str = "medium"
    has_elevator: bool = False
    has_pool: bool = False
    has_driver_room: bool = False
    is_furnished: bool = False


@dataclass
class ValuationResult:
    predicted_price: int
    min_price: int
    max_price: int
    meter_price: int
    investment_score: int
    investment_grade: str
    investment_grade_key: str
    city_key: str
    base_rate: float
    adjustments: dict[str, Any] = field(default_factory=dict)


def normalize_city(city: str) -> str:
    key = CITY_ALIASES.get(city.strip(), city.strip().lower())
    return key if key in CITY_BASE_RATES else "riyadh"


def neighborhood_multiplier(neighborhood: str) -> float:
    if not neighborhood:
        return 1.0
    normalized = neighborhood.strip().lower()
    for keyword, mult in PREMIUM_NEIGHBORHOOD_KEYWORDS.items():
        if keyword in normalized or keyword.lower() in normalized:
            return mult
    return 1.0


def street_width_multiplier(width: float) -> float:
    for threshold, mult in STREET_WIDTH_TIERS:
        if width >= threshold:
            return mult
    return 0.97


def investment_grade(score: int) -> tuple[str, str]:
    if score >= 85:
        return "A+", "excellent"
    if score >= 70:
        return "A", "very_good"
    if score >= 55:
        return "B", "average"
    return "C", "needs_study"


def calculate_valuation(data: PropertyInput) -> ValuationResult:
    city_key = normalize_city(data.city)
    base_rate = CITY_BASE_RATES[city_key]

    total = data.area * base_rate

    type_mult = PROPERTY_TYPE_MULTIPLIERS.get(data.property_type, 1.0)
    total *= type_mult

    depreciation = max(MIN_DEPRECIATION_FACTOR, 1 - (data.age * DEPRECIATION_RATE))
    total *= depreciation

    total *= 1 + (data.rooms - ROOMS_BASELINE) * ROOMS_ADJUSTMENT
    total *= street_width_multiplier(data.street_width)
    total *= FACADE_ADJUSTMENTS.get(data.facade, 1.0)
    total *= DISTRICT_GRADE_ADJUSTMENTS.get(data.location_grade, 1.0)
    total *= neighborhood_multiplier(data.neighborhood)

    if data.has_elevator:
        total *= AMENITY_ADJUSTMENTS["elevator"]
    if data.has_pool:
        total *= AMENITY_ADJUSTMENTS["pool"]
    if data.has_driver_room:
        total *= AMENITY_ADJUSTMENTS["driver_room"]
    if data.is_furnished:
        total *= AMENITY_ADJUSTMENTS["furnished"]

    avg_price = round(total)
    min_price = round(total * (1 - PRICE_RANGE_MARGIN))
    max_price = round(total * (1 + PRICE_RANGE_MARGIN))
    meter_price = round(total / data.area) if data.area else 0

    facade_adj = FACADE_ADJUSTMENTS.get(data.facade, 1.0)
    district_adj = DISTRICT_GRADE_ADJUSTMENTS.get(data.location_grade, 1.0)
    neigh_adj = neighborhood_multiplier(data.neighborhood)

    score = min(
        100,
        round(
            (base_rate / 50)
            + (15 if data.area > 200 else data.area / 15)
            + (10 if data.street_width >= 20 else 0)
            + (10 if facade_adj >= 1.04 else 0)
            + (15 if district_adj >= 1.15 else 0)
            + (10 if data.age <= 5 else 5 if data.age <= 10 else 0)
            + (10 if data.has_pool else 0)
            + (8 if data.has_elevator else 0)
            + (5 if neigh_adj > 1.0 else 0)
        ),
    )

    grade, grade_key = investment_grade(score)

    return ValuationResult(
        predicted_price=avg_price,
        min_price=min_price,
        max_price=max_price,
        meter_price=meter_price,
        investment_score=score,
        investment_grade=grade,
        city_key=city_key,
        base_rate=base_rate,
        investment_grade_key=grade_key,
        adjustments={
            "type_multiplier": type_mult,
            "depreciation_factor": round(depreciation, 4),
            "facade_adjustment": facade_adj,
            "district_adjustment": district_adj,
            "neighborhood_adjustment": neigh_adj,
            "street_width_adjustment": street_width_multiplier(data.street_width),
        },
    )


def get_reviewable_config() -> dict[str, Any]:
    return {
        "review_meta": REVIEW_META,
        "city_base_rates": CITY_BASE_RATES,
        "property_type_multipliers": PROPERTY_TYPE_MULTIPLIERS,
        "facade_adjustments": FACADE_ADJUSTMENTS,
        "district_grade_adjustments": DISTRICT_GRADE_ADJUSTMENTS,
        "amenity_adjustments": AMENITY_ADJUSTMENTS,
        "street_width_tiers": [{"min_width": t[0], "multiplier": t[1]} for t in STREET_WIDTH_TIERS],
        "depreciation": {"rate": DEPRECIATION_RATE, "min_factor": MIN_DEPRECIATION_FACTOR},
        "rooms": {"baseline": ROOMS_BASELINE, "adjustment_per_room": ROOMS_ADJUSTMENT},
        "price_range_margin": PRICE_RANGE_MARGIN,
        "premium_neighborhood_keywords": PREMIUM_NEIGHBORHOOD_KEYWORDS,
    }
