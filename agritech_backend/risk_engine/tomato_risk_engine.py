"""
risk_engine.py

Rule-based (explainable, non-ML) risk scoring engine for tomato crop diseases.

Diseases covered:
    - Late blight        (Phytophthora infestans)   -> cool, wet, high humidity
    - Early blight        (Alternaria solani)         -> warm-humid, alternating wet/dry
    - Septoria leaf spot   (Septoria lycopersici)       -> moderate temp, PROLONGED continuous wetness
    - Bacterial leaf spot  (Xanthomonas spp.)           -> warm, wet, wind/rain-splash driven
    - Tomato leaf curl virus (whitefly-vectored)        -> warm, DRY (favors whitefly vector activity)
    - Septoria + Early blight combined co-occurrence risk (they commonly overlap)

DESIGN NOTES
------------
- This is intentionally a weighted-threshold model, not a trained ML model. There is no
  large labeled local outbreak dataset to train against, so an explainable rule-based
  approach is both more honest about its own confidence and easier to defend to judges
  or agronomists than an opaque model fit to too little data.
- Every threshold below reflects general, well-established plant-pathology consensus for
  these diseases. BEFORE real deployment, validate/tune these thresholds against ICAR or
  your state agricultural university's extension bulletins for your specific growing
  region -- this file is a credible starting point, not a substitute for that citation work
  (see item 7 in the team implementation plan).
- No leaf-wetness sensor is assumed (per the current hardware plan: temp/humidity + soil
  moisture + rain gauge only). Leaf wetness is therefore ESTIMATED from sustained high
  humidity and/or recent rainfall, not measured directly. This is a real approximation,
  and is flagged as such in each disease's docstring.
- Integration contract: `calculate_risk(disease, readings)` is the single entry point meant
  to be imported directly into the Django backend, matching the module signature discussed
  in the team implementation plan (item 48).

Usage:
    from risk_engine import calculate_risk, Disease, SensorReading

    result = calculate_risk(Disease.LATE_BLIGHT, readings)
    print(result.score, result.band, result.explanation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SensorReading:
    """One timestamped sensor reading from a field node."""
    timestamp: datetime
    temp_c: float            # Air temperature, Celsius
    humidity_pct: float      # Relative humidity, 0-100
    rainfall_mm: float = 0.0 # Rainfall accumulated since previous reading, mm
    soil_moisture_pct: float = 0.0  # 0-100, if available


class Disease(str, Enum):
    LATE_BLIGHT = "late_blight"
    EARLY_BLIGHT = "early_blight"
    SEPTORIA_LEAF_SPOT = "septoria_leaf_spot"
    BACTERIAL_LEAF_SPOT = "bacterial_leaf_spot"
    LEAF_CURL_VIRUS = "leaf_curl_virus"
    SEPTORIA_EARLY_BLIGHT_COMBO = "septoria_early_blight_combo"


class RiskBand(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskResult:
    disease: Disease
    score: float  # 0-100
    band: RiskBand
    explanation: str
    contributing_factors: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Small helper functions (shared scoring primitives)
# ---------------------------------------------------------------------------

def _trapezoid(value: float, low: float, opt_low: float, opt_high: float, high: float) -> float:
    """
    Trapezoidal membership function, returns 0.0-1.0.
    Score rises from 0 at `low`, is 1.0 across [opt_low, opt_high], falls back to 0 at `high`.
    Used to score "how favorable is this temperature/humidity for the pathogen".
    """
    if value <= low or value >= high:
        return 0.0
    if opt_low <= value <= opt_high:
        return 1.0
    if low < value < opt_low:
        return (value - low) / (opt_low - low)
    # opt_high < value < high
    return (high - value) / (high - opt_high)


def _above_threshold_score(value: float, threshold: float, saturate_at: float) -> float:
    """
    Returns 0.0 below `threshold`, ramps linearly to 1.0 by `saturate_at`.
    Used for "risk increases once humidity/rain crosses X and maxes out by Y".
    """
    if value <= threshold:
        return 0.0
    if value >= saturate_at:
        return 1.0
    return (value - threshold) / (saturate_at - threshold)


def _below_threshold_score(value: float, threshold: float, saturate_at: float) -> float:
    """Inverse of _above_threshold_score -- risk increases as value drops BELOW threshold."""
    if value >= threshold:
        return 0.0
    if value <= saturate_at:
        return 1.0
    return (threshold - value) / (threshold - saturate_at)


def _recent_readings(readings: List[SensorReading], hours: int) -> List[SensorReading]:
    if not readings:
        return []
    latest = max(r.timestamp for r in readings)
    cutoff = latest - timedelta(hours=hours)
    return [r for r in readings if r.timestamp >= cutoff]


def _consecutive_favorable_days(readings: List[SensorReading], is_favorable_day_fn) -> int:
    """
    Groups readings by calendar day, checks each day's average conditions against
    `is_favorable_day_fn(avg_temp, avg_humidity, total_rainfall) -> bool`, and returns
    the current streak of consecutive favorable days ending at the most recent day.
    """
    if not readings:
        return 0

    by_day: Dict[str, List[SensorReading]] = {}
    for r in readings:
        key = r.timestamp.strftime("%Y-%m-%d")
        by_day.setdefault(key, []).append(r)

    sorted_days = sorted(by_day.keys())
    streak = 0
    for day in reversed(sorted_days):
        day_readings = by_day[day]
        avg_temp = sum(r.temp_c for r in day_readings) / len(day_readings)
        avg_humidity = sum(r.humidity_pct for r in day_readings) / len(day_readings)
        total_rain = sum(r.rainfall_mm for r in day_readings)
        if is_favorable_day_fn(avg_temp, avg_humidity, total_rain):
            streak += 1
        else:
            break
    return streak


def _band_from_score(score: float) -> RiskBand:
    # NOTE: these breakpoints are a reasonable starting default, not empirically
    # validated. Tune against real outbreak data if/when you have it.
    if score < 30:
        return RiskBand.LOW
    if score < 55:
        return RiskBand.MODERATE
    if score < 75:
        return RiskBand.HIGH
    return RiskBand.CRITICAL


def _duration_bonus(consecutive_days: int, max_days_for_full_bonus: int = 5) -> float:
    """0.0-1.0 bonus that grows with sustained favorable conditions."""
    return min(consecutive_days / max_days_for_full_bonus, 1.0)


# ---------------------------------------------------------------------------
# Per-disease scoring functions
# ---------------------------------------------------------------------------

def score_late_blight(readings: List[SensorReading]) -> RiskResult:
    """
    Phytophthora infestans favors COOL, WET conditions with high humidity and
    extended leaf wetness. Classic trigger: temp 10-24C (optimal ~18-21C),
    relative humidity persistently above ~90%, prolonged moisture.
    Leaf wetness is estimated here from sustained high humidity + recent rainfall,
    since no direct leaf-wetness sensor is assumed.
    """
    recent = _recent_readings(readings, hours=72)
    if not recent:
        return RiskResult(Disease.LATE_BLIGHT, 0.0, RiskBand.LOW, "No recent sensor data available.")

    avg_temp = sum(r.temp_c for r in recent) / len(recent)
    avg_humidity = sum(r.humidity_pct for r in recent) / len(recent)
    total_rain = sum(r.rainfall_mm for r in recent)

    temp_factor = _trapezoid(avg_temp, low=6, opt_low=15, opt_high=22, high=27)
    humidity_factor = _above_threshold_score(avg_humidity, threshold=85, saturate_at=97)
    wetness_proxy = _above_threshold_score(total_rain, threshold=5, saturate_at=40)

    def favorable_day(t, h, rain):
        return 10 <= t <= 24 and h >= 88

    streak = _consecutive_favorable_days(recent, favorable_day)
    duration_factor = _duration_bonus(streak)

    weights = {"temp": 0.30, "humidity": 0.30, "wetness": 0.20, "duration": 0.20}
    raw = (
        weights["temp"] * temp_factor
        + weights["humidity"] * humidity_factor
        + weights["wetness"] * wetness_proxy
        + weights["duration"] * duration_factor
    )
    score = round(raw * 100, 1)
    band = _band_from_score(score)

    explanation = (
        f"Late blight risk driven by cool-wet conditions: avg temp {avg_temp:.1f}C "
        f"(favors 15-22C), avg humidity {avg_humidity:.0f}% (risk rises above 85%), "
        f"{total_rain:.1f}mm rain in last 72h, {streak} consecutive favorable day(s)."
    )
    return RiskResult(
        Disease.LATE_BLIGHT, score, band, explanation,
        contributing_factors={
            "temp_factor": round(temp_factor, 2),
            "humidity_factor": round(humidity_factor, 2),
            "wetness_proxy": round(wetness_proxy, 2),
            "duration_factor": round(duration_factor, 2),
        },
    )


def score_early_blight(readings: List[SensorReading]) -> RiskResult:
    """
    Alternaria solani favors WARM, HUMID conditions that ALTERNATE with drier stress
    periods (unlike late blight, which wants continuous wetness). Optimal temp
    ~24-29C, humidity high but the alternating wet/dry pattern itself is a risk
    signal -- plants stressed by moisture fluctuation are more susceptible.
    """
    recent = _recent_readings(readings, hours=96)
    if not recent:
        return RiskResult(Disease.EARLY_BLIGHT, 0.0, RiskBand.LOW, "No recent sensor data available.")

    avg_temp = sum(r.temp_c for r in recent) / len(recent)
    avg_humidity = sum(r.humidity_pct for r in recent) / len(recent)
    humidity_values = [r.humidity_pct for r in recent]
    # Simple variability proxy: range of humidity values as a stand-in for wet/dry alternation
    humidity_swing = max(humidity_values) - min(humidity_values) if humidity_values else 0

    temp_factor = _trapezoid(avg_temp, low=15, opt_low=24, opt_high=29, high=34)
    humidity_factor = _above_threshold_score(avg_humidity, threshold=80, saturate_at=95)
    swing_factor = _above_threshold_score(humidity_swing, threshold=15, saturate_at=45)

    def favorable_day(t, h, rain):
        return 22 <= t <= 30 and h >= 78

    streak = _consecutive_favorable_days(recent, favorable_day)
    duration_factor = _duration_bonus(streak)

    weights = {"temp": 0.30, "humidity": 0.25, "swing": 0.25, "duration": 0.20}
    raw = (
        weights["temp"] * temp_factor
        + weights["humidity"] * humidity_factor
        + weights["swing"] * swing_factor
        + weights["duration"] * duration_factor
    )
    score = round(raw * 100, 1)
    band = _band_from_score(score)

    explanation = (
        f"Early blight risk driven by warm-humid alternating conditions: avg temp "
        f"{avg_temp:.1f}C (favors 24-29C), avg humidity {avg_humidity:.0f}%, "
        f"humidity swing {humidity_swing:.0f}pp (wet/dry alternation proxy), "
        f"{streak} consecutive favorable day(s)."
    )
    return RiskResult(
        Disease.EARLY_BLIGHT, score, band, explanation,
        contributing_factors={
            "temp_factor": round(temp_factor, 2),
            "humidity_factor": round(humidity_factor, 2),
            "swing_factor": round(swing_factor, 2),
            "duration_factor": round(duration_factor, 2),
        },
    )


def score_septoria_leaf_spot(readings: List[SensorReading]) -> RiskResult:
    """
    Septoria lycopersici is rain-splash dispersed and needs PROLONGED CONTINUOUS
    leaf wetness (commonly cited as 48-72+ hours) to establish infection. Optimal
    temp is more moderate than early blight, roughly 20-25C. Continuous wetness is
    estimated from consecutive days of high humidity + rainfall together, since a
    single wet day is a much weaker signal than several in a row.
    """
    recent = _recent_readings(readings, hours=120)
    if not recent:
        return RiskResult(Disease.SEPTORIA_LEAF_SPOT, 0.0, RiskBand.LOW, "No recent sensor data available.")

    avg_temp = sum(r.temp_c for r in recent) / len(recent)
    avg_humidity = sum(r.humidity_pct for r in recent) / len(recent)
    total_rain = sum(r.rainfall_mm for r in recent)

    temp_factor = _trapezoid(avg_temp, low=12, opt_low=20, opt_high=25, high=30)

    def favorable_day(t, h, rain):
        # Septoria's defining feature: needs BOTH high humidity AND rain on the same day,
        # not just one or the other -- this is what "continuous wetness" is standing in for.
        return h >= 85 and rain >= 2

    streak = _consecutive_favorable_days(recent, favorable_day)
    # Septoria's risk curve is much steeper with duration than the other diseases --
    # a single wet day means little, several in a row is what actually matters.
    wetness_duration_factor = _above_threshold_score(streak, threshold=1, saturate_at=4)

    rain_volume_factor = _above_threshold_score(total_rain, threshold=8, saturate_at=50)

    weights = {"temp": 0.20, "wetness_duration": 0.50, "rain_volume": 0.30}
    raw = (
        weights["temp"] * temp_factor
        + weights["wetness_duration"] * wetness_duration_factor
        + weights["rain_volume"] * rain_volume_factor
    )
    score = round(raw * 100, 1)
    band = _band_from_score(score)

    explanation = (
        f"Septoria leaf spot risk driven by prolonged wetness: {streak} consecutive "
        f"day(s) of high humidity + rain together (needs 2-4+ to be a strong signal), "
        f"avg temp {avg_temp:.1f}C (favors 20-25C), {total_rain:.1f}mm total rain in last 120h."
    )
    return RiskResult(
        Disease.SEPTORIA_LEAF_SPOT, score, band, explanation,
        contributing_factors={
            "temp_factor": round(temp_factor, 2),
            "wetness_duration_factor": round(wetness_duration_factor, 2),
            "rain_volume_factor": round(rain_volume_factor, 2),
            "consecutive_wet_days": streak,
        },
    )


def score_bacterial_leaf_spot(readings: List[SensorReading]) -> RiskResult:
    """
    Xanthomonas spp. favors WARM, WET conditions, but specifically needs an actual
    rain/wind-driven splash EVENT (for spread and wounding-based entry) rather than
    just ambient humidity -- unlike the fungal diseases above, sustained humidity
    alone without rain events is a weaker signal here.
    """
    recent = _recent_readings(readings, hours=72)
    if not recent:
        return RiskResult(Disease.BACTERIAL_LEAF_SPOT, 0.0, RiskBand.LOW, "No recent sensor data available.")

    avg_temp = sum(r.temp_c for r in recent) / len(recent)
    avg_humidity = sum(r.humidity_pct for r in recent) / len(recent)
    rain_events = sum(1 for r in recent if r.rainfall_mm >= 1.0)
    total_rain = sum(r.rainfall_mm for r in recent)

    temp_factor = _trapezoid(avg_temp, low=18, opt_low=24, opt_high=30, high=35)
    humidity_factor = _above_threshold_score(avg_humidity, threshold=80, saturate_at=95)
    rain_event_factor = _above_threshold_score(rain_events, threshold=1, saturate_at=6)

    weights = {"temp": 0.30, "humidity": 0.25, "rain_events": 0.45}
    raw = (
        weights["temp"] * temp_factor
        + weights["humidity"] * humidity_factor
        + weights["rain_events"] * rain_event_factor
    )
    score = round(raw * 100, 1)
    band = _band_from_score(score)

    explanation = (
        f"Bacterial leaf spot risk driven by warm-wet conditions WITH rain/splash "
        f"events: avg temp {avg_temp:.1f}C (favors 24-30C), avg humidity {avg_humidity:.0f}%, "
        f"{rain_events} distinct rain event(s) in last 72h ({total_rain:.1f}mm total)."
    )
    return RiskResult(
        Disease.BACTERIAL_LEAF_SPOT, score, band, explanation,
        contributing_factors={
            "temp_factor": round(temp_factor, 2),
            "humidity_factor": round(humidity_factor, 2),
            "rain_event_factor": round(rain_event_factor, 2),
            "rain_events_count": rain_events,
        },
    )


def score_leaf_curl_virus(readings: List[SensorReading]) -> RiskResult:
    """
    Tomato leaf curl virus is whitefly-VECTORED -- it is not a moisture-driven
    pathogen like the other four. Whitefly populations and activity are favored by
    WARM, DRY conditions; rain and high humidity actually SUPPRESS whitefly activity.
    This formula is therefore intentionally inverted relative to the fungal/bacterial
    diseases above -- do not average this in with the others using the same weights.
    """
    recent = _recent_readings(readings, hours=168)  # 1 week -- vector buildup is slower
    if not recent:
        return RiskResult(Disease.LEAF_CURL_VIRUS, 0.0, RiskBand.LOW, "No recent sensor data available.")

    avg_temp = sum(r.temp_c for r in recent) / len(recent)
    avg_humidity = sum(r.humidity_pct for r in recent) / len(recent)
    total_rain = sum(r.rainfall_mm for r in recent)

    temp_factor = _trapezoid(avg_temp, low=18, opt_low=26, opt_high=32, high=38)
    dryness_factor = _below_threshold_score(avg_humidity, threshold=65, saturate_at=35)
    low_rain_factor = _below_threshold_score(total_rain, threshold=10, saturate_at=0)

    def favorable_day(t, h, rain):
        return 24 <= t <= 34 and h <= 60 and rain < 1

    streak = _consecutive_favorable_days(recent, favorable_day)
    duration_factor = _duration_bonus(streak, max_days_for_full_bonus=7)

    weights = {"temp": 0.30, "dryness": 0.30, "low_rain": 0.15, "duration": 0.25}
    raw = (
        weights["temp"] * temp_factor
        + weights["dryness"] * dryness_factor
        + weights["low_rain"] * low_rain_factor
        + weights["duration"] * duration_factor
    )
    score = round(raw * 100, 1)
    band = _band_from_score(score)

    explanation = (
        f"Leaf curl virus risk driven by whitefly-favorable warm-DRY conditions "
        f"(inverse of the fungal diseases): avg temp {avg_temp:.1f}C (favors 26-32C), "
        f"avg humidity {avg_humidity:.0f}% (risk rises as humidity drops below 65%), "
        f"only {total_rain:.1f}mm rain in last week, {streak} consecutive dry-warm day(s)."
    )
    return RiskResult(
        Disease.LEAF_CURL_VIRUS, score, band, explanation,
        contributing_factors={
            "temp_factor": round(temp_factor, 2),
            "dryness_factor": round(dryness_factor, 2),
            "low_rain_factor": round(low_rain_factor, 2),
            "duration_factor": round(duration_factor, 2),
        },
    )


def score_septoria_early_blight_combo(readings: List[SensorReading]) -> RiskResult:
    """
    Septoria leaf spot and early blight are commonly reported to co-occur in the
    field, since their favorable condition windows overlap substantially (both like
    warm-to-moderate temperatures with high humidity, differing mainly in exactly
    how continuous the wetness needs to be). This function does not invent a new
    formula -- it combines the two individual scores and adds an explicit
    "co-occurrence bonus" for the specific zone where both are simultaneously
    elevated, since real-world co-occurrence risk is higher than either disease's
    individual score alone would suggest in that overlap zone.
    """
    septoria = score_septoria_leaf_spot(readings)
    early_blight = score_early_blight(readings)

    base_combo = (septoria.score + early_blight.score) / 2

    # Co-occurrence bonus: if BOTH individual scores are already elevated, the
    # combined real-world risk is higher than a simple average suggests.
    both_elevated = septoria.score >= 50 and early_blight.score >= 50
    bonus = 10 if both_elevated else 0

    score = round(min(base_combo + bonus, 100), 1)
    band = _band_from_score(score)

    explanation = (
        f"Combined septoria + early blight risk (these diseases commonly co-occur "
        f"due to overlapping favorable conditions). Septoria score: {septoria.score}, "
        f"early blight score: {early_blight.score}."
        + (" Both individually elevated -- co-occurrence bonus applied." if both_elevated else "")
    )

    return RiskResult(
        Disease.SEPTORIA_EARLY_BLIGHT_COMBO, score, band, explanation,
        contributing_factors={
            "septoria_score": septoria.score,
            "early_blight_score": early_blight.score,
            "co_occurrence_bonus_applied": both_elevated,
        },
    )


# ---------------------------------------------------------------------------
# Single entry point -- import THIS into the Django backend
# ---------------------------------------------------------------------------

_SCORERS = {
    Disease.LATE_BLIGHT: score_late_blight,
    Disease.EARLY_BLIGHT: score_early_blight,
    Disease.SEPTORIA_LEAF_SPOT: score_septoria_leaf_spot,
    Disease.BACTERIAL_LEAF_SPOT: score_bacterial_leaf_spot,
    Disease.LEAF_CURL_VIRUS: score_leaf_curl_virus,
    Disease.SEPTORIA_EARLY_BLIGHT_COMBO: score_septoria_early_blight_combo,
}


def calculate_risk(disease: Disease, readings: List[SensorReading]) -> RiskResult:
    """
    Main entry point. Pass a Disease enum member and a list of recent SensorReading
    objects (order doesn't matter, timestamps do). Returns a RiskResult with a
    0-100 score, a qualitative band, and a human-readable explanation.
    """
    scorer = _SCORERS.get(disease)
    if scorer is None:
        raise ValueError(f"No scorer implemented for disease: {disease}")
    return scorer(readings)


def calculate_all_risks(readings: List[SensorReading]) -> Dict[Disease, RiskResult]:
    """Convenience wrapper: runs every disease scorer against the same reading set."""
    return {disease: calculate_risk(disease, readings) for disease in Disease}


# ---------------------------------------------------------------------------
# Demo / manual test (run this file directly: `python risk_engine.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    now = datetime.now()

    # Synthetic example: a warm, humid, rainy stretch -- should push several
    # fungal/bacterial disease scores up, and push leaf curl virus DOWN.
    demo_readings = []
    for day_offset in range(5, -1, -1):
        day = now - timedelta(days=day_offset)
        for hour in (6, 12, 18):
            demo_readings.append(
                SensorReading(
                    timestamp=day.replace(hour=hour, minute=0, second=0, microsecond=0),
                    temp_c=23.5 + (2 if hour == 12 else 0),
                    humidity_pct=90 if hour != 12 else 80,
                    rainfall_mm=3.0 if hour == 18 else 0.0,
                    soil_moisture_pct=55,
                )
            )

    print("=" * 70)
    print("DEMO: Warm, humid, rainy 6-day stretch")
    print("=" * 70)
    results = calculate_all_risks(demo_readings)
    for disease, result in results.items():
        print(f"\n[{disease.value.upper()}]")
        print(f"  Score: {result.score}  |  Band: {result.band.value}")
        print(f"  {result.explanation}")
        print(f"  Factors: {result.contributing_factors}")
