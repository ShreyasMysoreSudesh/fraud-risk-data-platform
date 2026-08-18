import pytest
from pydantic import ValidationError

from fraud_platform.data_generator.models import Customer, Merchant


def test_valid_customer():
    customer = Customer(
        customer_id="C1001",
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        country="US",
        state="NY",
        signup_date="2025-06-10",
        risk_segment="LOW",
        account_status="ACTIVE",
        updated_at="2026-08-17T20:00:00",
    )

    assert customer.customer_id == "C1001"
    assert customer.risk_segment.value == "LOW"


def test_invalid_email():
    with pytest.raises(ValidationError):
        Customer(
            customer_id="C1002",
            first_name="John",
            last_name="Smith",
            email="not-an-email",
            country="US",
            state="NY",
            signup_date="2025-06-10",
            risk_segment="LOW",
            account_status="ACTIVE",
            updated_at="2026-08-17T20:00:00",
        )


def test_invalid_risk_segment():
    with pytest.raises(ValidationError):
        Customer(
            customer_id="C1003",
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            country="US",
            state="NY",
            signup_date="2025-06-10",
            risk_segment="VERY_HIGH",
            account_status="ACTIVE",
            updated_at="2026-08-17T20:00:00",
        )


def test_valid_merchant():
    merchant = Merchant(
        merchant_id="M1001",
        name="Amazon",
        category="E_COMMERCE",
        country="US",
        merchant_risk_level="LOW",
        updated_at="2026-08-17T20:00:00",
    )

    assert merchant.merchant_id == "M1001"
    assert merchant.name == "Amazon"
    assert merchant.merchant_risk_level.value == "LOW"


def test_invalid_merchant_risk_level():
    with pytest.raises(ValidationError):
        Merchant(
            merchant_id="M1002",
            name="Test Merchant",
            category="RETAIL",
            country="US",
            merchant_risk_level="VERY_HIGH",
            updated_at="2026-08-17T20:00:00",
        )