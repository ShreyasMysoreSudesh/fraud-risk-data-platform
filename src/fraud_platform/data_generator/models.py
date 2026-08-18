from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class RiskSegment(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class Customer(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: EmailStr
    country: str
    state: str
    signup_date: date
    risk_segment: RiskSegment
    account_status: AccountStatus
    updated_at: datetime

class MerchantRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Merchant(BaseModel):
    merchant_id: str
    name: str
    category: str
    country: str
    merchant_risk_level: MerchantRiskLevel
    updated_at: datetime

class DeviceType(str, Enum):
    MOBILE = "MOBILE"
    TABLET = "TABLET"
    DESKTOP = "DESKTOP"

class Device(BaseModel):
    device_id: str
    customer_id: str
    device_type: DeviceType
    operating_system: str
    first_seen: datetime
    last_seen: datetime
    trusted_device: bool

    @model_validator(mode="after")
    def validate_device(self):
        if self.first_seen > self.last_seen:
            raise ValueError("first_seen must be before last_seen")
        return self

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class TransactionChannel(str, Enum):
    ONLINE = "ONLINE"
    POS = "POS"
    ATM = "ATM"
    MOBILE = "MOBILE"


class TransactionStatus(str, Enum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"

class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    merchant_id: str
    device_id: str
    transaction_timestamp: datetime
    amount: Decimal
    currency: Currency
    channel: TransactionChannel
    ip_country: str
    card_present: bool
    transaction_status: TransactionStatus
    is_fraud: bool

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Transaction amount must be non-negative")
        return value
    @field_validator("transaction_timestamp")
    @classmethod
    def validate_transaction_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Transaction timestamp must be timezone-aware")
        if value> datetime.now(UTC):
            raise ValueError("Transaction timestamp cannot be in the future")
        return value
