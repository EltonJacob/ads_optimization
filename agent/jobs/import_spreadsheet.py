"""Import keyword performance data from CSV or Excel spreadsheets."""

from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from agent.data import dao
from agent.data.schemas import KeywordPerformance

logger = logging.getLogger(__name__)


def _parse_date(value: object) -> date:
    """Parse date from various formats."""
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()

    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date from {value!r}")


def _parse_float(value: object) -> float:
    """Parse float, handling empty/null values."""
    if value in (None, "", "null", "NULL", "--"):
        return 0.0
    # Handle currency formatting like "$12.50" or "12.50 USD"
    if isinstance(value, str):
        value = value.strip().replace("$", "").replace("USD", "").replace(",", "").strip()
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _parse_int(value: object) -> int:
    """Parse integer, handling empty/null values."""
    if value in (None, "", "null", "NULL", "--"):
        return 0
    # Remove commas from numbers like "1,234"
    if isinstance(value, str):
        value = value.strip().replace(",", "")
    try:
        return int(float(value))  # Handle "5.0" -> 5
    except (ValueError, TypeError):
        return 0


def _generate_keyword_id(keyword: str, match_type: str) -> str:
    """Generate a unique keyword ID from keyword text and match type.

    Returns an integer (as string) that can be safely converted by dao.upsert_performance.
    """
    text = f"{keyword.lower().strip()}_{match_type.lower().strip()}"
    # Convert hex hash to integer to match database schema requirement
    hex_hash = hashlib.md5(text.encode()).hexdigest()[:12]
    return str(int(hex_hash, 16))


def import_csv(file_path: Path) -> List[KeywordPerformance]:
    """Import keyword performance data from CSV file.

    Supports two formats:
    1. Standard format with keyword_id and date columns
    2. Amazon Ads export format with Keyword and Match type columns (generates keyword_id)
    """
    import csv

    records: List[KeywordPerformance] = []

    with open(file_path, "r", encoding="utf-8-sig") as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)

        # Normalize column names to lowercase
        reader.fieldnames = [name.lower().strip() if name else "" for name in (reader.fieldnames or [])]

        # Detect format type
        has_keyword_id = any(field in reader.fieldnames for field in ["keyword_id", "keywordid"])
        has_date = "date" in reader.fieldnames
        has_keyword_text = "keyword" in reader.fieldnames
        has_match_type = "match type" in reader.fieldnames

        # Amazon export format detection
        is_amazon_format = has_keyword_text and has_match_type and not has_keyword_id

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
            try:
                # Handle Amazon export format
                if is_amazon_format:
                    keyword = row.get("keyword", "").strip()
                    match_type = row.get("match type", "").strip()

                    if not keyword or not match_type:
                        logger.warning(f"Skipping row {row_num}: missing keyword or match type")
                        continue

                    # Skip rows with "State" = "archived" or "paused"
                    state = str(row.get("state", "")).lower()
                    if state in ("archived", "paused"):
                        continue

                    # Generate keyword_id from keyword + match type
                    keyword_id = _generate_keyword_id(keyword, match_type)

                    # Use today's date if no date column
                    record_date = date.today()

                # Standard format
                else:
                    keyword_id = row.get("keyword_id") or row.get("keywordid")
                    date_str = row.get("date")

                    if not keyword_id or not date_str:
                        logger.warning(f"Skipping row {row_num}: missing keyword_id or date")
                        continue

                    keyword_id = str(keyword_id)
                    record_date = _parse_date(date_str)

                # Parse metrics (works for both formats)
                impressions = _parse_int(row.get("impressions", 0))
                clicks = _parse_int(row.get("clicks", 0))
                spend = _parse_float(row.get("spend") or row.get("cost") or row.get("spend(usd)", 0))
                sales = _parse_float(row.get("sales") or row.get("sales(usd)", 0))
                orders = _parse_int(row.get("orders") or row.get("conversions", 0))

                # Skip rows with zero activity
                if impressions == 0 and clicks == 0 and spend == 0 and sales == 0:
                    continue

                # Create record
                record = KeywordPerformance(
                    keyword_id=keyword_id,
                    date=record_date,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    sales=sales,
                    orders=orders,
                )

                records.append(record)

            except Exception as exc:
                logger.error(f"Error parsing row {row_num}: {exc}")
                continue

    return records


def import_excel(file_path: Path) -> List[KeywordPerformance]:
    """Import keyword performance data from Excel file.

    Supports two formats:
    1. Standard format with keyword_id and date columns
    2. Amazon Ads export format with Keyword and Match type columns (generates keyword_id)
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError(
            "openpyxl is required for Excel import. Install with: pip install openpyxl"
        )

    records: List[KeywordPerformance] = []
    workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet = workbook.active

    # Get header row and normalize to lowercase
    headers = [str(cell.value).lower().strip() if cell.value else "" for cell in sheet[1]]

    # Detect format type
    has_keyword_id = any(field in headers for field in ["keyword_id", "keywordid"])
    has_date = "date" in headers
    has_keyword_text = "keyword" in headers
    has_match_type = "match type" in headers

    # Amazon export format detection
    is_amazon_format = has_keyword_text and has_match_type and not has_keyword_id

    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            # Create dict from headers and row values
            row_dict = dict(zip(headers, row))

            # Handle Amazon export format
            if is_amazon_format:
                keyword = str(row_dict.get("keyword", "")).strip()
                match_type = str(row_dict.get("match type", "")).strip()

                if not keyword or not match_type:
                    logger.warning(f"Skipping row {row_num}: missing keyword or match type")
                    continue

                # Skip rows with "State" = "archived" or "paused"
                state = str(row_dict.get("state", "")).lower()
                if state in ("archived", "paused"):
                    continue

                # Generate keyword_id from keyword + match type
                keyword_id = _generate_keyword_id(keyword, match_type)

                # Use today's date if no date column
                record_date = date.today()

            # Standard format
            else:
                keyword_id = row_dict.get("keyword_id") or row_dict.get("keywordid")
                date_val = row_dict.get("date")

                if not keyword_id or not date_val:
                    logger.warning(f"Skipping row {row_num}: missing keyword_id or date")
                    continue

                keyword_id = str(keyword_id)
                record_date = _parse_date(date_val)

            # Parse metrics (works for both formats)
            impressions = _parse_int(row_dict.get("impressions", 0))
            clicks = _parse_int(row_dict.get("clicks", 0))
            spend = _parse_float(row_dict.get("spend") or row_dict.get("cost") or row_dict.get("spend(usd)", 0))
            sales = _parse_float(row_dict.get("sales") or row_dict.get("sales(usd)", 0))
            orders = _parse_int(row_dict.get("orders") or row_dict.get("conversions", 0))

            # Skip rows with zero activity
            if impressions == 0 and clicks == 0 and spend == 0 and sales == 0:
                continue

            # Create record
            record = KeywordPerformance(
                keyword_id=keyword_id,
                date=record_date,
                impressions=impressions,
                clicks=clicks,
                spend=spend,
                sales=sales,
                orders=orders,
            )

            records.append(record)

        except Exception as exc:
            logger.error(f"Error parsing row {row_num}: {exc}")
            continue

    workbook.close()
    return records


def run(file_path: str, *, job_id: Optional[str] = None) -> None:
    """Import keyword performance data from a spreadsheet file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(
        "import_start",
        extra={"file_path": str(path), "file_size": path.stat().st_size, "job_id": job_id},
    )

    # Determine file type and import
    suffix = path.suffix.lower()
    if suffix == ".csv":
        records = import_csv(path)
    elif suffix in (".xlsx", ".xls"):
        records = import_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .csv, .xlsx, or .xls")

    if not records:
        logger.warning("import_no_records", extra={"file_path": str(path)})
        print(f"⚠️  No valid records found in {path.name}")
        return

    # Persist to database
    persisted = dao.upsert_performance(records)

    logger.info(
        "import_complete",
        extra={
            "file_path": str(path),
            "parsed_rows": len(records),
            "persisted_rows": persisted,
            "job_id": job_id,
        },
    )

    print(f"✓ Imported {len(records)} records from {path.name}")
    print(f"✓ Persisted {persisted} rows to database")
