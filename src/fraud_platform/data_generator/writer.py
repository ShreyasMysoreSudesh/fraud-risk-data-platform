import json
from enum import Enum
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel

TRANSACTION_SCHEMA = pa.schema(
    [
        pa.field("transaction_id", pa.string()),
        pa.field("customer_id", pa.string()),
        pa.field("merchant_id", pa.string()),
        pa.field("device_id", pa.string()),
        pa.field(
            "transaction_timestamp",
            pa.timestamp("us", tz="UTC"),
        ),
        pa.field(
            "amount",
            pa.decimal128(12, 2),
        ),
        pa.field("currency", pa.string()),
        pa.field("channel", pa.string()),
        pa.field("ip_country", pa.string()),
        pa.field("card_present", pa.bool_()),
        pa.field("transaction_status", pa.string()),
        pa.field("is_fraud", pa.bool_()),
    ]
)


def write_jsonl(
    records: list[BaseModel],
    output_path: Path,
    append: bool = False,
) -> None:
    """Write Pydantic models to a JSONL file."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    mode = "a" if append else "w"

    with output_path.open(
        mode,
        encoding="utf-8",
    ) as file:
        for record in records:
            serialized = record.model_dump(mode="json")
            file.write(json.dumps(serialized) + "\n")


def model_to_python_dict(
    record: BaseModel,
) -> dict:
    """
    Convert a Pydantic model to Python-native values.

    Enum values are converted to strings while datetimes and Decimals
    remain typed Python objects for Arrow.
    """

    data = record.model_dump(mode="python")

    for key, value in data.items():
        if isinstance(value, Enum):
            data[key] = value.value

    return data


def write_transaction_parquet(
    records: list[BaseModel],
    output_path: Path,
) -> None:
    """Write one transaction batch to a Parquet file."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = [
        model_to_python_dict(record)
        for record in records
    ]

    table = pa.Table.from_pylist(
        rows,
        schema=TRANSACTION_SCHEMA,
    )

    pq.write_table(
        table,
        output_path,
        compression="snappy",
    )