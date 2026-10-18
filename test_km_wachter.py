# test_km_wachter.py
from km_wachter import needs_service, wear_percent


def test_almost_due_car_is_flagged():
    # A car at 14,900 of its 15,000 km window is about 99% worn and MUST be flagged.
    assert needs_service({"id": "VOS-4471", "odometer": 14900, "last_service_km": 0}) is True


def test_missing_reading_is_not_treated_as_zero():
    # A car with NO last-service reading must not be treated as fully worn.
    assert needs_service({"id": "VOS-7788", "odometer": 92000}) is False


# --- Boundary tests for the 80% wear threshold ---

def test_wear_just_below_threshold_not_flagged():
    # 11,850 km of a 15,000 km interval = exactly 79.0% — below threshold, must NOT be flagged.
    pct = wear_percent(11850, 15000)
    assert pct == 79.0                  # hard-coded: 11850 / 15000 * 100
    assert needs_service({"id": "VOS-TEST1", "odometer": 11850, "last_service_km": 0}) is False


def test_wear_exactly_at_threshold_flagged():
    # 12,000 km of a 15,000 km interval = exactly 80.0% — at threshold, MUST be flagged.
    pct = wear_percent(12000, 15000)
    assert pct == 80.0                  # hard-coded: 12000 / 15000 * 100
    assert needs_service({"id": "VOS-TEST2", "odometer": 12000, "last_service_km": 0}) is True


def test_wear_just_above_threshold_flagged():
    # 12,150 km of a 15,000 km interval = exactly 81.0% — above threshold, MUST be flagged.
    pct = wear_percent(12150, 15000)
    assert pct == 81.0                  # hard-coded: 12150 / 15000 * 100
    assert needs_service({"id": "VOS-TEST3", "odometer": 12150, "last_service_km": 0}) is True


def test_14900_km_wear_is_about_99_percent():
    # 14,900 km of a 15,000 km interval = 99.333...% — must NOT be rounded to 0.
    pct = wear_percent(14900, 15000)
    assert abs(pct - 99.333) < 0.01    # hard-coded: 14900 / 15000 * 100 ≈ 99.333
