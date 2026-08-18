import random
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from faker import Faker

from fraud_platform.data_generator.models import (
    AccountStatus,
    Currency,
    Customer,
    Device,
    DeviceType,
    Merchant,
    MerchantRiskLevel,
    RiskSegment,
    Transaction,
    TransactionChannel,
    TransactionStatus,
)

fake = Faker()


# ---------------------------------------------------------------------------
# RANDOM SEED
# ---------------------------------------------------------------------------


def set_seed(seed: int) -> None:
    """Set deterministic seeds for Python random and Faker."""
    random.seed(seed)
    Faker.seed(seed)


# ---------------------------------------------------------------------------
# CUSTOMER GENERATION
# ---------------------------------------------------------------------------


def generate_customer(customer_number: int) -> Customer:
    """Generate one synthetic customer."""

    customer_id = f"C{customer_number:06d}"

    first_name = fake.first_name()
    last_name = fake.last_name()

    signup_date = fake.date_between(
        start_date="-5y",
        end_date="today",
    )

    updated_at = fake.date_time_between(
        start_date=datetime.combine(
            signup_date,
            datetime.min.time(),
            tzinfo=UTC,
        ),
        end_date="now",
        tzinfo=UTC,
    )

    return Customer(
        customer_id=customer_id,
        first_name=first_name,
        last_name=last_name,
        email=fake.email(),
        country="US",
        state=fake.state_abbr(),
        signup_date=signup_date,
        risk_segment=random.choice(list(RiskSegment)),
        account_status=random.choice(list(AccountStatus)),
        updated_at=updated_at,
    )


def generate_customers(count: int) -> list[Customer]:
    """Generate multiple synthetic customers."""

    if count <= 0:
        raise ValueError("Customer count must be greater than zero")

    return [
        generate_customer(customer_number)
        for customer_number in range(1, count + 1)
    ]


# ---------------------------------------------------------------------------
# MERCHANT GENERATION
# ---------------------------------------------------------------------------


MERCHANT_CATEGORIES = [
    "GROCERY",
    "RESTAURANT",
    "E_COMMERCE",
    "TRAVEL",
    "ENTERTAINMENT",
    "ELECTRONICS",
    "FUEL",
    "PHARMACY",
    "RETAIL",
    "UTILITIES",
]


def generate_merchant(merchant_number: int) -> Merchant:
    """Generate one synthetic merchant."""

    merchant_id = f"M{merchant_number:06d}"

    risk_level = random.choices(
        population=[
            MerchantRiskLevel.LOW,
            MerchantRiskLevel.MEDIUM,
            MerchantRiskLevel.HIGH,
        ],
        weights=[70, 25, 5],
        k=1,
    )[0]

    return Merchant(
        merchant_id=merchant_id,
        name=fake.company(),
        category=random.choice(MERCHANT_CATEGORIES),
        country="US",
        merchant_risk_level=risk_level,
        updated_at=fake.date_time_between(
            start_date="-3y",
            end_date="now",
            tzinfo=UTC,
        ),
    )


def generate_merchants(count: int) -> list[Merchant]:
    """Generate multiple synthetic merchants."""

    if count <= 0:
        raise ValueError("Merchant count must be greater than zero")

    return [
        generate_merchant(merchant_number)
        for merchant_number in range(1, count + 1)
    ]


# ---------------------------------------------------------------------------
# DEVICE GENERATION
# ---------------------------------------------------------------------------


def operating_system_for_device(device_type: DeviceType) -> str:
    """Return a reasonable operating system for a device type."""

    if device_type == DeviceType.MOBILE:
        return random.choice(
            [
                "iOS",
                "Android",
            ]
        )

    if device_type == DeviceType.TABLET:
        return random.choice(
            [
                "iPadOS",
                "Android",
            ]
        )

    return random.choice(
        [
            "Windows",
            "macOS",
            "Linux",
        ]
    )


def create_device(
    device_number: int,
    customer: Customer,
) -> Device:
    """Generate one synthetic device belonging to a customer."""

    device_type = random.choice(list(DeviceType))

    first_seen = fake.date_time_between(
        start_date="-3y",
        end_date="-1d",
        tzinfo=UTC,
    )

    last_seen = fake.date_time_between(
        start_date=first_seen,
        end_date="now",
        tzinfo=UTC,
    )

    return Device(
        device_id=f"D{device_number:07d}",
        customer_id=customer.customer_id,
        device_type=device_type,
        operating_system=operating_system_for_device(device_type),
        first_seen=first_seen,
        last_seen=last_seen,
        trusted_device=random.random() < 0.85,
    )


def generate_devices(
    count: int,
    customers: list[Customer],
) -> list[Device]:
    """
    Generate devices.

    Every customer receives at least one device before additional devices
    are assigned randomly.
    """

    if count <= 0:
        raise ValueError("Device count must be greater than zero")

    if not customers:
        raise ValueError("Customers are required to generate devices")

    if count < len(customers):
        raise ValueError(
            "Device count must be at least equal to customer count "
            "so every customer has one device"
        )

    devices: list[Device] = []

    device_number = 1

    # Give every customer at least one device.
    for customer in customers:
        devices.append(
            create_device(
                device_number=device_number,
                customer=customer,
            )
        )
        device_number += 1

    # Generate remaining devices randomly.
    while len(devices) < count:
        customer = random.choice(customers)

        devices.append(
            create_device(
                device_number=device_number,
                customer=customer,
            )
        )

        device_number += 1

    return devices


# ---------------------------------------------------------------------------
# DEVICE LOOKUP
# ---------------------------------------------------------------------------


def build_customer_device_index(
    devices: list[Device],
) -> dict[str, list[Device]]:
    """
    Build a customer_id -> devices lookup.

    This prevents scanning every device for every generated transaction.
    """

    customer_devices: defaultdict[str, list[Device]] = defaultdict(list)

    for device in devices:
        customer_devices[device.customer_id].append(device)

    return dict(customer_devices)


# ---------------------------------------------------------------------------
# TRANSACTION GENERATION
# ---------------------------------------------------------------------------


INTERNATIONAL_COUNTRIES = [
    "CA",
    "GB",
    "DE",
    "IN",
    "MX",
    "FR",
    "AU",
]


def generate_transaction_amount() -> Decimal:
    """Generate a positively skewed synthetic transaction amount."""

    raw_amount = random.lognormvariate(
        mu=4.0,
        sigma=1.0,
    )

    amount = Decimal(str(round(raw_amount, 2)))

    return min(
        amount,
        Decimal("10000.00"),
    )


def generate_transaction(
    transaction_number: int,
    customers: list[Customer],
    merchants: list[Merchant],
    customer_device_index: dict[str, list[Device]],
) -> Transaction:
    """Generate one synthetic financial transaction."""

    customer = random.choice(customers)
    merchant = random.choice(merchants)

    customer_devices = customer_device_index.get(
        customer.customer_id
    )

    if not customer_devices:
        raise ValueError(
            f"No devices found for customer {customer.customer_id}"
        )

    device = random.choice(customer_devices)

    amount = generate_transaction_amount()

    now = datetime.now(UTC)

    transaction_timestamp = now - timedelta(
        seconds=random.randint(
            0,
            365 * 24 * 60 * 60,
        )
    )

    channel = random.choice(list(TransactionChannel))

    card_present = channel in {
        TransactionChannel.POS,
        TransactionChannel.ATM,
    }

    # 90% of transactions originate from the customer's home country.
    if random.random() < 0.90:
        ip_country = customer.country
    else:
        ip_country = random.choice(INTERNATIONAL_COUNTRIES)

    transaction_status = random.choices(
        population=[
            TransactionStatus.APPROVED,
            TransactionStatus.DECLINED,
            TransactionStatus.PENDING,
        ],
        weights=[
            92,
            7,
            1,
        ],
        k=1,
    )[0]

    # -----------------------------------------------------------------------
    # FRAUD PROBABILITY
    # -----------------------------------------------------------------------

    fraud_probability = 0.003

    # Large transaction.
    if amount > Decimal("1500.00"):
        fraud_probability += 0.05

    # International transaction.
    if ip_country != customer.country:
        fraud_probability += 0.04

    # Untrusted device.
    if not device.trusted_device:
        fraud_probability += 0.03

    # High-risk merchant.
    if merchant.merchant_risk_level == MerchantRiskLevel.HIGH:
        fraud_probability += 0.05

    # Medium-risk merchant.
    elif merchant.merchant_risk_level == MerchantRiskLevel.MEDIUM:
        fraud_probability += 0.01

    # Very early morning transaction.
    if 0 <= transaction_timestamp.hour <= 4:
        fraud_probability += 0.015

    # High-risk customer.
    if customer.risk_segment == RiskSegment.HIGH:
        fraud_probability += 0.025

    elif customer.risk_segment == RiskSegment.MEDIUM:
        fraud_probability += 0.005

    fraud_probability = min(
        fraud_probability,
        0.80,
    )

    is_fraud = random.random() < fraud_probability

    return Transaction(
        transaction_id=f"TX{transaction_number:010d}",
        customer_id=customer.customer_id,
        merchant_id=merchant.merchant_id,
        device_id=device.device_id,
        transaction_timestamp=transaction_timestamp,
        amount=amount,
        currency=Currency.USD,
        channel=channel,
        ip_country=ip_country,
        card_present=card_present,
        transaction_status=transaction_status,
        is_fraud=is_fraud,
    )


def generate_transactions(
    count: int,
    customers: list[Customer],
    merchants: list[Merchant],
    devices: list[Device],
) -> list[Transaction]:
    """
    Generate transactions in memory.

    Use this function only for development and relatively small datasets.
    The 10M-record dataset will use chunked generation instead.
    """

    if count <= 0:
        raise ValueError("Transaction count must be greater than zero")

    if not customers:
        raise ValueError("Customers are required")

    if not merchants:
        raise ValueError("Merchants are required")

    if not devices:
        raise ValueError("Devices are required")

    customer_device_index = build_customer_device_index(devices)

    return [
        generate_transaction(
            transaction_number=transaction_number,
            customers=customers,
            merchants=merchants,
            customer_device_index=customer_device_index,
        )
        for transaction_number in range(1, count + 1)
    ]


# ---------------------------------------------------------------------------
# CHUNKED TRANSACTION GENERATION
# ---------------------------------------------------------------------------


def generate_transaction_batches(
    total_records: int,
    customers: list[Customer],
    merchants: list[Merchant],
    devices: list[Device],
    batch_size: int = 100_000,
):
    """
    Generate transactions in batches.

    This will be used for the 10M-record dataset so the entire fact table
    does not need to exist in memory simultaneously.
    """

    if total_records <= 0:
        raise ValueError("Total record count must be greater than zero")

    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero")

    customer_device_index = build_customer_device_index(devices)

    for start in range(
        0,
        total_records,
        batch_size,
    ):
        current_batch_size = min(
            batch_size,
            total_records - start,
        )

        batch: list[Transaction] = []

        for offset in range(current_batch_size):
            transaction_number = start + offset + 1

            transaction = generate_transaction(
                transaction_number=transaction_number,
                customers=customers,
                merchants=merchants,
                customer_device_index=customer_device_index,
            )

            batch.append(transaction)

        yield batch
        