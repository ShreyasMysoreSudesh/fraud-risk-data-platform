import pytest
from pydantic import ValidationError

from fraud_platform.data_generator.models import Customer, Device, Merchant, Transaction


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
def test_valid_device():
    device = Device(
        device_id="D1001",
        customer_id="C1001",
        device_type="MOBILE",
        operating_system="iOS",
        first_seen="2026-08-17T20:00:00",
        last_seen="2026-08-18T20:00:00",
        trusted_device=True,
    )

    assert device.device_id == "D1001"
    assert device.device_type.value == "MOBILE"
    assert device.trusted_device is True
def test_invalid_device_type():
    with pytest.raises(ValidationError):
        Device(
            device_id="D1002",
            customer_id="C1002",
            device_type="SMARTWATCH",
            operating_system="Android",
            first_seen="2026-08-17T20:00:00",
            last_seen="2026-08-18T20:00:00",
            trusted_device=False,
        )
def test_device_last_seen_before_first_seen():
    with pytest.raises(ValidationError):
        Device(
            device_id="D1002",
            customer_id="C1001",
            device_type="MOBILE",
            operating_system="Android",
            first_seen="2026-08-17T20:00:00",
            last_seen="2026-08-16T20:00:00",
            trusted_device=False,
        )
def test_valid_transaction():
    transaction = Transaction(
        transaction_id="TX1001",
        customer_id="C1001",
        merchant_id="M1001",
        device_id="D1001",
        transaction_timestamp="2026-08-17T20:30:00-04:00",
        amount="125.75",
        currency="USD",
        channel="ONLINE",
        ip_country="US",
        card_present=False,
        transaction_status="APPROVED",
        is_fraud=False,
    )

    assert transaction.transaction_id == "TX1001"
    assert transaction.currency.value == "USD"
    assert transaction.transaction_status.value == "APPROVED"
def test_invalid_transaction_currency():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TX1002",
            customer_id="C1001",
            merchant_id="M1001",
            device_id="D1001",
            transaction_timestamp="2026-08-17T20:30:00",
            amount="100.00",
            currency="DOGE",
            channel="ONLINE",
            ip_country="US",
            card_present=False,
            transaction_status="APPROVED",
            is_fraud=False,
        )
def test_invalid_transaction_status():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TX1003",
            customer_id="C1001",
            merchant_id="M1001",
            device_id="D1001",
            transaction_timestamp="2026-08-17T20:30:00",
            amount="100.00",
            currency="USD",
            channel="ONLINE",
            ip_country="US",
            card_present=False,
            transaction_status="CANCELLED_FOREVER",
            is_fraud=False,
        )

def test_transaction_negative_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TX1004",
            customer_id="C1001",
            merchant_id="M1001",
            device_id="D1001",
            transaction_timestamp="2026-08-17T20:30:00-04:00",
            amount="-50.00",
            currency="USD",
            channel="ONLINE",
            ip_country="US",
            card_present=False,
            transaction_status="APPROVED",
            is_fraud=False,
        )
def test_transaction_zero_amount():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TX1005",
            customer_id="C1001",
            merchant_id="M1001",
            device_id="D1001",
            transaction_timestamp="2026-08-17T20:30:00-04:00",
            amount="0",
            currency="USD",
            channel="ONLINE",
            ip_country="US",
            card_present=False,
            transaction_status="APPROVED",
            is_fraud=False,
        )
def test_transaction_timestamp_requires_timezone():
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="TX1006",
            customer_id="C1001",
            merchant_id="M1001",
            device_id="D1001",
            transaction_timestamp="2026-08-17T20:30:00",
            amount="100.00",
            currency="USD",
            channel="ONLINE",
            ip_country="US",
            card_present=False,
            transaction_status="APPROVED",
            is_fraud=False,
        )