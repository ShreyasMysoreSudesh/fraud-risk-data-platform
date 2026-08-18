import argparse
from pathlib import Path
from time import perf_counter

from fraud_platform.data_generator.generator import (
    generate_customers,
    generate_devices,
    generate_merchants,
    generate_transaction_batches,
    set_seed,
)
from fraud_platform.data_generator.writer import (
    write_jsonl,
    write_transaction_parquet,
)

OUTPUT_DIR = Path("data/raw")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Generate synthetic fraud-risk datasets."
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=1_000,
        help="Number of customers to generate.",
    )

    parser.add_argument(
        "--merchants",
        type=int,
        default=100,
        help="Number of merchants to generate.",
    )

    parser.add_argument(
        "--devices",
        type=int,
        default=2_000,
        help="Number of devices to generate.",
    )

    parser.add_argument(
        "--transactions",
        type=int,
        default=10_000,
        help="Number of transactions to generate.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1_000,
        help="Number of transactions per batch.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )

    return parser.parse_args()


def main() -> None:
    """Generate synthetic financial datasets."""

    args = parse_args()

    set_seed(args.seed)

    print()
    print("=" * 60)
    print("SYNTHETIC FRAUD DATA GENERATOR")
    print("=" * 60)

    print(f"Customers:     {args.customers:,}")
    print(f"Merchants:     {args.merchants:,}")
    print(f"Devices:       {args.devices:,}")
    print(f"Transactions:  {args.transactions:,}")
    print(f"Batch size:    {args.batch_size:,}")
    print(f"Seed:          {args.seed}")
    print("=" * 60)
    print()

    # ------------------------------------------------------------------
    # GENERATE CUSTOMERS
    # ------------------------------------------------------------------

    print(f"Generating {args.customers:,} customers...")

    customers = generate_customers(
        args.customers
    )

    print(
        f"Generated {len(customers):,} customers."
    )

    # ------------------------------------------------------------------
    # GENERATE MERCHANTS
    # ------------------------------------------------------------------

    print(f"Generating {args.merchants:,} merchants...")

    merchants = generate_merchants(
        args.merchants
    )

    print(
        f"Generated {len(merchants):,} merchants."
    )

    # ------------------------------------------------------------------
    # GENERATE DEVICES
    # ------------------------------------------------------------------

    print(f"Generating {args.devices:,} devices...")

    devices = generate_devices(
        count=args.devices,
        customers=customers,
    )

    print(
        f"Generated {len(devices):,} devices."
    )

    # ------------------------------------------------------------------
    # WRITE DIMENSION DATA
    # ------------------------------------------------------------------

    print()
    print("Writing dimension files...")

    write_jsonl(
        records=customers,
        output_path=OUTPUT_DIR / "customers.jsonl",
    )

    write_jsonl(
        records=merchants,
        output_path=OUTPUT_DIR / "merchants.jsonl",
    )

    write_jsonl(
        records=devices,
        output_path=OUTPUT_DIR / "devices.jsonl",
    )

    print("Dimension files written.")

    # ------------------------------------------------------------------
    # PREPARE PARQUET OUTPUT DIRECTORY
    # ------------------------------------------------------------------

    parquet_output_dir = (
        OUTPUT_DIR / "transactions_parquet"
    )

    parquet_output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove Parquet files from previous runs.
    for old_file in parquet_output_dir.glob(
        "part-*.parquet"
    ):
        old_file.unlink()

    # ------------------------------------------------------------------
    # GENERATE TRANSACTIONS
    # ------------------------------------------------------------------

    print()
    print(
        f"Generating {args.transactions:,} transactions..."
    )

    start_time = perf_counter()

    total_written = 0
    fraud_count = 0

    for batch_number, batch in enumerate(
        generate_transaction_batches(
            total_records=args.transactions,
            customers=customers,
            merchants=merchants,
            devices=devices,
            batch_size=args.batch_size,
        ),
        start=1,
    ):
        # Count fraud records.
        fraud_count += sum(
            transaction.is_fraud
            for transaction in batch
        )

        # Each batch becomes one Parquet file.
        parquet_file = (
            parquet_output_dir
            / f"part-{batch_number:05d}.parquet"
        )

        write_transaction_parquet(
            records=batch,
            output_path=parquet_file,
        )

        total_written += len(batch)

        print(
            f"Transactions written: "
            f"{total_written:,}/{args.transactions:,}"
        )

    # ------------------------------------------------------------------
    # CALCULATE METRICS
    # ------------------------------------------------------------------

    elapsed_seconds = (
        perf_counter() - start_time
    )

    records_per_second = (
        total_written / elapsed_seconds
        if elapsed_seconds > 0
        else 0
    )

    fraud_rate = (
        fraud_count / total_written
        if total_written > 0
        else 0
    )

    parquet_files = list(
        parquet_output_dir.glob("*.parquet")
    )

    parquet_size_bytes = sum(
        file.stat().st_size
        for file in parquet_files
    )

    parquet_size_mb = (
        parquet_size_bytes / (1024 * 1024)
    )

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------

    print()
    print("=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    print(
        f"Customers:       {len(customers):,}"
    )

    print(
        f"Merchants:       {len(merchants):,}"
    )

    print(
        f"Devices:         {len(devices):,}"
    )

    print(
        f"Transactions:    {total_written:,}"
    )

    print()
    print(
        f"Fraud count:     {fraud_count:,}"
    )

    print(
        f"Fraud rate:      {fraud_rate:.2%}"
    )

    print()
    print(
        f"Generation time: "
        f"{elapsed_seconds:.2f} seconds"
    )

    print(
        f"Throughput:      "
        f"{records_per_second:,.0f} records/sec"
    )

    print()
    print(
        f"Parquet files:   {len(parquet_files):,}"
    )

    print(
        f"Parquet size:    "
        f"{parquet_size_mb:,.2f} MB"
    )

    print()
    print(
        f"Output directory: "
        f"{parquet_output_dir.resolve()}"
    )

    print("=" * 60)
    print("Generation complete.")


if __name__ == "__main__":
    main()