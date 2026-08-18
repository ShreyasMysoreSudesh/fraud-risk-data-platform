from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


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

    