You are a senior Data Engineer with extensive experience building robust ETL processes for enterprise systems.

**Context & Requirements**:
1. We already have a Python script that flattens multi-level column headers (see the code below). 
2. Now, we need to **extend** this code to handle multi-level row indexes AND insert (or upsert) the resulting data into a database (e.g., PostgreSQL, MySQL, or other SQL DB).
3. The code must be **production-grade**:
   - Configurable to handle multi-level row indexes in addition to multi-level columns.
   - Flexible in specifying:
       - file paths
       - sheet names
       - header rows, skip rows, prefix separator for columns
       - row index levels to flatten
       - database connection parameters (host, port, database, user, password)
       - the table name to insert into
       - whether to create or truncate the table
       - logging level, etc.
   - Must gracefully handle missing row index labels, partial data, or duplicates.
   - Must include error handling and transaction management for database inserts.
4. We want a **scalable design**: easy to integrate into a larger pipeline.

---

**Base Code (Flattening Multi-Level Columns)**:
```python
#!/usr/bin/env python3
"""
flatten_excel_columns.py

A production-ready Python script that reads an Excel file with potentially multi-level column headers,
flattens the headers into a single level, and returns or saves the resulting DataFrame.

Features:
    - Configurable: sheet name, header rows, skip rows, prefix separator, etc.
    - Production-grade: error handling, logging, flexible usage.
    - Scalable design: can integrate into larger ETL pipelines.

Example:
    python flatten_excel_columns.py --file_path data.xlsx --sheet_name "Sheet1" \
        --header_rows 0,1 --prefix_sep "_" --skiprows 2
"""

import argparse
import logging
import sys
import pandas as pd
from typing import List, Union

__author__ = "Senior Data Engineer"
__version__ = "1.0.0"


def setup_logging():
    """
    Configure the logger for the script.
    Adjust the logging level as needed.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def flatten_excel_columns(
    file_path: str,
    sheet_name: Union[str, int] = 0,
    header_rows: Union[List[int], int] = 0,
    skiprows: Union[List[int], int, None] = None,
    prefix_sep: str = "_",
) -> pd.DataFrame:
    """
    Reads an Excel file (potentially with multi-level column headers),
    flattens the column headers, and returns a single-level column DataFrame.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (Union[str, int], optional): The sheet name or index to parse.
            Defaults to the first sheet (index=0).
        header_rows (Union[List[int], int], optional): Row indices to use as the column headers.
            For multi-level headers, pass a list (e.g. [0, 1]).
            For a single-level header, pass an integer (e.g. 0).
            Defaults to 0.
        skiprows (Union[List[int], int, None], optional): Rows to skip at the beginning
            of the sheet before reading the data. Defaults to None.
        prefix_sep (str, optional): Separator for joining multi-level header tuples.
            Defaults to '_'.

    Returns:
        pd.DataFrame: DataFrame with flattened column headers.

    Raises:
        FileNotFoundError: If the provided file does not exist.
        ValueError: If the sheet is invalid or the header rows configuration fails.
    """
    logger = logging.getLogger("flatten_excel_columns")
    logger.info("Reading Excel file: %s", file_path)
    logger.info("Sheet: %s | Header Rows: %s | Skip Rows: %s | Prefix Sep: %s",
                sheet_name, header_rows, skiprows, prefix_sep)
    try:
        # Read the Excel file with the given parameters
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_rows,
            skiprows=skiprows
        )
    except FileNotFoundError as fnf_err:
        logger.error("File not found: %s", file_path)
        raise FileNotFoundError(f"Cannot find the file: {file_path}") from fnf_err
    except Exception as e:
        logger.error("Failed to read Excel file: %s", e)
        raise ValueError(f"Error reading file {file_path}: {e}") from e

    # If columns are multi-level, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        logger.info("Flattening multi-level columns.")
        # Convert tuples like ('Volatility', 'TOTAL') into "Volatility_TOTAL"
        new_columns = []
        for col_tuple in df.columns:
            # For each tuple, filter out None or blank, then join
            col_parts = [str(x) for x in col_tuple if x is not None]
            new_col_name = prefix_sep.join(col_parts).strip()
            new_columns.append(new_col_name)
        df.columns = new_columns
    else:
        logger.info("Columns are already single-level. No flattening needed.")

    # Optional: Trim whitespace from column names
    df.columns = [col.strip() for col in df.columns]

    logger.info("Successfully flattened columns. DataFrame shape: %s", df.shape)
    return df


def main():
    """
    Main entry point for command-line usage:
    python flatten_excel_columns.py --file_path data.xlsx [options...]
    """
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Flatten multi-level column headers in an Excel file."
    )
    parser.add_argument(
        "--file_path",
        required=True,
        help="Path to the Excel file."
    )
    parser.add_argument(
        "--sheet_name",
        default="0",
        help="Sheet name or index. Defaults to first sheet."
    )
    parser.add_argument(
        "--header_rows",
        default="0",
        help="Comma-separated list of rows to use as headers. E.g. '0,1' for multi-level."
    )
    parser.add_argument(
        "--skiprows",
        default=None,
        help="Number of rows (or comma-separated list of rows) to skip. E.g. '2' or '2,3'."
    )
    parser.add_argument(
        "--prefix_sep",
        default="_",
        help="Separator for flattening multi-level headers. Default is '_'."
    )

    args = parser.parse_args()
    logger = logging.getLogger("flatten_excel_columns")

    # Parse header_rows
    if "," in args.header_rows:
        header_rows = [int(h) for h in args.header_rows.split(",")]
    else:
        header_rows = int(args.header_rows)

    # Parse skiprows
    parsed_skiprows = None
    if args.skiprows is not None:
        if "," in args.skiprows:
            parsed_skiprows = [int(r) for r in args.skiprows.split(",")]
        else:
            parsed_skiprows = int(args.skiprows)

    sheet_name = args.sheet_name
    # Try converting to int if it's purely numeric
    if sheet_name.isdigit():
        sheet_name = int(sheet_name)

    try:
        df = flatten_excel_columns(
            file_path=args.file_path,
            sheet_name=sheet_name,
            header_rows=header_rows,
            skiprows=parsed_skiprows,
            prefix_sep=args.prefix_sep
        )
        logger.info("DataFrame ready. Columns: %s", list(df.columns))
        # For demonstration, print shape. Real-world usage: store or pass DataFrame forward.
        print(f"Flattened DataFrame shape: {df.shape}")
        print(df.head())
    except Exception as e:
        logger.error("Failed to flatten Excel columns: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
