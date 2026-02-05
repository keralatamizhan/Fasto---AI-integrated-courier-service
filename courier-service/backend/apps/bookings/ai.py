from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.utils import timezone


def _stable_seed(*parts: Any) -> int:
    h = hashlib.sha256(("|".join(map(str, parts))).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _approx_km(sender_city: str, receiver_city: str) -> float:
    """
    Deterministic pseudo-distance when we don't have real geocoding.
    Produces a value roughly in [5, 1500] km based on city strings.
    """
    seed = _stable_seed(sender_city.lower().strip(), receiver_city.lower().strip())
    rng = random.Random(seed)
    base = rng.uniform(15.0, 900.0)
    # Add a little structure: similar names => shorter
    similarity = 1.0 - (min(_levenshtein(sender_city, receiver_city), 20) / 20.0)
    return max(5.0, base * (0.6 + 0.8 * (1.0 - similarity)))


def _levenshtein(a: str, b: str) -> int:
    a, b = a.lower(), b.lower()
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


@dataclass(frozen=True)
class BookingRecommendation:
    recommended_delivery_type: str
    confidence: float
    reasons: list[str]


def recommend_service(distance_km: float, weight_kg: float, urgency: str | None = None) -> BookingRecommendation:
    """
    Simulated "AI" recommendation using transparent rules + calibrated confidence.
    urgency: "low" | "medium" | "high"
    """
    urgency = (urgency or "medium").lower()
    score_express = 0.0
    score_normal = 0.0
    score_eco = 0.0

    # Distance signal
    if distance_km > 450:
        score_express += 1.5
        score_normal += 0.8
        score_eco += 0.3
    elif distance_km > 120:
        score_express += 1.0
        score_normal += 1.0
        score_eco += 0.6
    else:
        score_express += 0.6
        score_normal += 1.0
        score_eco += 1.1

    # Weight signal
    if weight_kg >= 10:
        score_express += 0.4
        score_normal += 1.0
        score_eco += 0.8
    elif weight_kg >= 3:
        score_express += 0.8
        score_normal += 1.0
        score_eco += 0.9
    else:
        score_express += 1.1
        score_normal += 1.0
        score_eco += 0.8

    # Urgency signal
    if urgency == "high":
        score_express += 1.7
    elif urgency == "low":
        score_eco += 0.8

    scores = {"express": score_express, "normal": score_normal, "eco": score_eco}
    recommended = max(scores, key=scores.get)
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    gap = sorted_scores[0][1] - sorted_scores[1][1]
    confidence = max(0.55, min(0.95, 0.65 + 0.12 * gap))

    reasons: list[str] = []
    reasons.append(f"Distance: {distance_km:.1f} km")
    reasons.append(f"Weight: {weight_kg:.2f} kg")
    reasons.append(f"Urgency: {urgency}")
    if recommended == "express":
        reasons.append("Optimized for faster delivery windows.")
    elif recommended == "eco":
        reasons.append("Optimized for cost efficiency and lower emissions.")
    else:
        reasons.append("Balanced speed and cost for typical deliveries.")

    return BookingRecommendation(recommended_delivery_type=recommended, confidence=confidence, reasons=reasons)


def optimize_route(sender_city: str, receiver_city: str, waypoints: list[str] | None = None) -> dict[str, Any]:
    """
    Simulated route optimization. Returns an ordered list of stops and an ETA model.
    """
    waypoints = [w.strip() for w in (waypoints or []) if w.strip()]
    base_distance = _approx_km(sender_city, receiver_city)

    # Deterministic "optimized" ordering: sort waypoints by hash distance from sender
    def wp_key(w: str) -> int:
        return _stable_seed(sender_city.lower(), w.lower())

    ordered = sorted(waypoints, key=wp_key)
    stops = [sender_city] + ordered + [receiver_city]

    # Add distance inflation for extra stops
    total_distance = base_distance * (1.0 + 0.07 * max(0, len(ordered)))
    avg_speed_kmh = 42.0
    travel_hours = total_distance / avg_speed_kmh
    eta_minutes = int(math.ceil(travel_hours * 60))

    return {
        "stops": stops,
        "distance_km": round(total_distance, 2),
        "eta_minutes": eta_minutes,
    }


def detect_issues(tracking_status: str, distance_km: float, delivery_type: str, created_at) -> dict[str, Any]:
    """
    Simulated issue detection: produces a risk score and optional alert.
    """
    age_minutes = max(0, int((timezone.now() - created_at).total_seconds() // 60))
    risk = 0.05
    if delivery_type == "express":
        risk += 0.05
    if distance_km > 600:
        risk += 0.15
    if tracking_status in ("in_transit", "out_for_delivery") and age_minutes > 240:
        risk += 0.20
    if tracking_status == "picked_up" and age_minutes > 180:
        risk += 0.20
    if tracking_status == "pending" and age_minutes > 60:
        risk += 0.25

    risk = max(0.0, min(0.95, risk))
    alert = None
    if risk >= 0.55:
        alert = "Potential delay detected based on current progress and route conditions (simulated)."

    return {"risk_score": round(risk, 2), "alert": alert}


def estimate_distance_km(sender_city: str, receiver_city: str) -> float:
    return round(_approx_km(sender_city, receiver_city), 2)


def estimate_delivery_datetime(distance_km: float, delivery_type: str) -> object:
    """
    Naive ETA: normal ~ 1-3 days, express ~ 0-2 days, eco ~ 2-5 days.
    """
    now = timezone.now()
    if delivery_type == "express":
        hours = 8 + (distance_km / 80.0) * 6
        return now + timedelta(hours=min(48, hours))
    if delivery_type == "eco":
        hours = 36 + (distance_km / 60.0) * 10
        return now + timedelta(hours=min(120, hours))
    hours = 20 + (distance_km / 70.0) * 8
    return now + timedelta(hours=min(72, hours))

