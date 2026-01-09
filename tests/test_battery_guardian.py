import pytest
from volltyield_platinum.battery_guardian import BatteryPassport, BatteryHealthEvent

def test_grade_a_platinum():
    # SOH > 94%, No Abuse
    event = BatteryHealthEvent(soh_percent=95.0, cycle_count=100, fast_charge_count=10, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "PREMIUM", "value_adj": 0.15}

def test_grade_b_gold():
    # SOH > 85%, No Abuse
    # SOH 90%
    event = BatteryHealthEvent(soh_percent=90.0, cycle_count=100, fast_charge_count=10, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "STANDARD", "value_adj": 0.0}

def test_grade_b_gold_with_abuse():
    # SOH > 85% (e.g. 96%), BUT Abuse present
    # Should fall to Grade B because Grade A requires No Abuse
    event = BatteryHealthEvent(soh_percent=96.0, cycle_count=100, fast_charge_count=31, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "STANDARD", "value_adj": 0.0}

def test_grade_c_distressed_low_soh():
    # SOH < 80%
    event = BatteryHealthEvent(soh_percent=79.9, cycle_count=100, fast_charge_count=10, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "PENALTY", "value_adj": -0.25}

def test_grade_c_distressed_thermal():
    # SOH High, but Thermal Event > 45.0
    event = BatteryHealthEvent(soh_percent=99.0, cycle_count=100, fast_charge_count=10, max_temp_c=45.1)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "PENALTY", "value_adj": -0.25}

def test_gap_uncertified():
    # SOH between 80 and 85 inclusive
    event = BatteryHealthEvent(soh_percent=82.0, cycle_count=100, fast_charge_count=10, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "UNCERTIFIED", "value_adj": 0.0}

    # Boundary 85.0
    event = BatteryHealthEvent(soh_percent=85.0, cycle_count=100, fast_charge_count=10, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    assert result == {"impact": "UNCERTIFIED", "value_adj": 0.0}

def test_zero_cycles():
    # Should not crash on division by zero
    event = BatteryHealthEvent(soh_percent=95.0, cycle_count=0, fast_charge_count=0, max_temp_c=25.0)
    passport = BatteryPassport()
    result = passport.calculate_resale_grade(event)
    # No abuse possible if 0 cycles (0 > 0 is False)
    assert result == {"impact": "PREMIUM", "value_adj": 0.15}
