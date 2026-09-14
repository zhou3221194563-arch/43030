"""Export a standalone EDA workbook for the PSQ AT1 dataset."""

import csv
import math
from datetime import date, datetime
from pathlib import Path
from statistics import mean, median

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[2]
DATA_DIR = ROOT / "data"
PRICE_FILE = DATA_DIR / "pricehistory-dailyadj.csv"
OUTPUT_FILE = DATA_DIR / "eda_analysis.xlsx"
START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)


def load_prices() -> list[dict[str, object]]:
    prices = []
    with PRICE_FILE.open(newline="", encoding="utf-8-sig") as source:
        for source_row in csv.DictReader(source):
            trading_date = datetime.strptime(source_row["Date"], "%d/%m/%Y").date()
            if not START_DATE <= trading_date <= END_DATE:
                continue
            prices.append(
                {
                    "Date": trading_date,
                    "ASX Code": source_row["ASX Code"],
                    "Company Name": source_row["Company Name"],
                    "Open": float(source_row["Open"]),
                    "High": float(source_row["High"]),
                    "Low": float(source_row["Low"]),
                    "Close": float(source_row["Close"]),
                    "Daily Volume": int(float(source_row["Volume"])),
                    "Shares Issued": int(float(source_row["Shares on Issue"])),
                }
            )
    return sorted(prices, key=lambda row: row["Date"])


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def add_title(sheet, title: str, columns: int) -> None:
    sheet.append([title] + [None] * (columns - 1))
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=columns)
    sheet["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    sheet["A1"].fill = PatternFill("solid", fgColor="1F4E78")


def style_table(sheet, header_row: int = 2) -> None:
    header_fill = PatternFill("solid", fgColor="5B9BD5")
    for cell in sheet[header_row]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.row_dimensions[header_row].height = 30
    for column_cells in sheet.columns:
        width = min(max(len(str(cell.value or "")) for cell in column_cells) + 2, 32)
        sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = width


def write_rows(sheet, rows: list[list[object]]) -> None:
    for row in rows:
        sheet.append(row)


def add_eda_summary(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    closes = [row["Close"] for row in prices]
    volumes = [row["Daily Volume"] for row in prices]
    tradable = [row for row in prices if row["Daily Volume"] > 0 and row["Close"] > 0]
    zero_volume = [row for row in prices if row["Daily Volume"] == 0]
    sheet = workbook.create_sheet("EDA_Summary")
    add_title(sheet, "PSQ Exploratory Data Analysis Summary", 3)
    rows = [
        ["Metric", "Value", "Interpretation"],
        ["Company", prices[0]["Company Name"], "Company assigned for AT1"],
        ["ASX Code", prices[0]["ASX Code"], "Security identifier"],
        ["Requested period", f"{START_DATE} to {END_DATE}", "Assessment period"],
        [
            "Available period",
            f"{prices[0]['Date']} to {prices[-1]['Date']}",
            "Available source-data period",
        ],
        ["Coverage status", "Incomplete", "Source file ends before 30 June 2026"],
        ["Total records", len(prices), "Rows within the requested period"],
        ["Tradable records", len(tradable), "Daily Volume > 0 and Close > 0"],
        ["Zero-volume records", len(zero_volume), "Retained for data-quality review"],
        ["Close minimum", min(closes), "Price per share"],
        ["Close maximum", max(closes), "Price per share"],
        ["Close mean", mean(closes), "Price per share"],
        ["Close median", median(closes), "Price per share"],
        ["Total volume", sum(volumes), "Shares recorded in the source data"],
        ["Average daily volume", mean(volumes), "Includes zero-volume records"],
        [
            "Shares issued minimum",
            min(row["Shares Issued"] for row in prices),
            "Issued shares",
        ],
        [
            "Shares issued maximum",
            max(row["Shares Issued"] for row in prices),
            "Issued shares",
        ],
        [
            "Dividend available",
            "No",
            "Dividend field is not supplied in the price source",
        ],
        ["PE available", "No", "PE field is not supplied in the price source"],
    ]
    write_rows(sheet, rows)
    style_table(sheet)
    for row in sheet.iter_rows(min_row=3):
        row[2].alignment = Alignment(wrap_text=True, vertical="top")
    for row_number in [11, 12, 13, 15]:
        sheet.cell(row_number, 2).number_format = "$0.000"


def add_data_dictionary(workbook: Workbook) -> None:
    sheet = workbook.create_sheet("Data_Dictionary")
    add_title(sheet, "Dataset Fields and Measurement Types", 4)
    rows = [
        ["Field", "Data type", "Measurement", "EDA use"],
        ["Date", "Date", "Trading date", "Time ordering and coverage"],
        ["ASX Code", "Text", "Security identifier", "Company identification"],
        ["Company Name", "Text", "Company name", "Company identification"],
        ["Open", "Numeric", "Currency per share", "Opening price distribution"],
        ["High", "Numeric", "Currency per share", "Intraday high and range"],
        ["Low", "Numeric", "Currency per share", "Intraday low and range"],
        ["Close", "Numeric", "Currency per share", "Price trend and returns"],
        ["Daily Volume", "Integer", "Shares traded", "Liquidity and activity"],
        ["Shares Issued", "Integer", "Shares on issue", "Capitalisation analysis"],
        ["Daily Return", "Numeric", "Percentage", "Price movement and outliers"],
        ["Market Capitalisation", "Numeric", "Currency", "Close x Shares Issued"],
        ["Cumulative Return", "Numeric", "Percentage", "Performance from first close"],
    ]
    write_rows(sheet, rows)
    style_table(sheet)


def add_descriptive_stats(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    sheet = workbook.create_sheet("Descriptive_Stats")
    add_title(sheet, "Descriptive Statistics", 9)
    fields = ["Open", "High", "Low", "Close", "Daily Volume", "Shares Issued"]
    rows = [
        [
            "Field",
            "Count",
            "Missing",
            "Minimum",
            "Q1",
            "Mean",
            "Median",
            "Q3",
            "Maximum",
        ]
    ]
    for field in fields:
        values = [float(row[field]) for row in prices]
        rows.append(
            [
                field,
                len(values),
                0,
                min(values),
                percentile(values, 0.25),
                mean(values),
                median(values),
                percentile(values, 0.75),
                max(values),
            ]
        )
    write_rows(sheet, rows)
    style_table(sheet)
    for row in sheet.iter_rows(min_row=3):
        for cell in row[3:]:
            cell.number_format = "#,##0.000"


def add_eda_questions(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    returns = []
    for index, row in enumerate(prices):
        if index and prices[index - 1]["Close"] != 0:
            returns.append(
                {
                    "Date": row["Date"],
                    "Return": row["Close"] / prices[index - 1]["Close"] - 1,
                }
            )
    return_values = [row["Return"] for row in returns]
    top_return_days = sorted(returns, key=lambda row: abs(row["Return"]), reverse=True)[
        :5
    ]
    top_volume_days = sorted(prices, key=lambda row: row["Daily Volume"], reverse=True)[
        :5
    ]
    zero_volume_count = sum(row["Daily Volume"] == 0 for row in prices)
    zero_ohlc_count = sum(
        any(row[field] == 0 for field in ["Open", "High", "Low"]) for row in prices
    )
    shares_values = [row["Shares Issued"] for row in prices]
    shares_stable = min(shares_values) == max(shares_values)
    return_summary = "; ".join(
        f"{row['Date'].isoformat()}: {row['Return']:.2%}" for row in top_return_days
    )
    volume_summary = "; ".join(
        f"{row['Date'].isoformat()}: {row['Daily Volume']:,}" for row in top_volume_days
    )

    sheet = workbook.create_sheet("EDA_Questions")
    add_title(sheet, "Answers to EDA Questions", 3)
    rows = [
        ["Question", "Answer", "Evidence / analysis basis"],
        [
            "1. How many calendar days and valid trading records are covered?",
            f"The price data covers {prices[0]['Date']} to {prices[-1]['Date']}, with {len(prices)} records in total. {len(prices) - zero_volume_count} records are classified as tradable. The dataset does not cover the complete financial year because the last available date is before 30 June 2026.",
            "A tradable record is defined as Daily Volume > 0 and Close > 0.",
        ],
        [
            "2. Are there suspended, delisted, zero-volume or zero-price records?",
            f"There are {zero_volume_count} zero-volume records. Among them, {zero_ohlc_count} records have at least one zero value in Open, High or Low. These records are retained in the raw data and flagged in Clean_Data. For OHLC charting, zero OHLC values may be replaced with the same-day Close according to the documented rule.",
            "Zero-volume records are treated as data states requiring interpretation, not automatically as normal trades.",
        ],
        [
            "3. What are the ranges and volatility of Open, High, Low and Close prices?",
            f"The Close price ranges from ${min(row['Close'] for row in prices):.3f} to ${max(row['Close'] for row in prices):.3f}. The mean is ${mean(row['Close'] for row in prices):.3f} and the median is ${median(row['Close'] for row in prices):.3f}. The mean daily return is {mean(return_values):.2%}. The dates with the largest absolute movements are: {return_summary}.",
            "Price ranges are calculated from all records; returns are calculated from changes between consecutive Close prices.",
        ],
        [
            "4. Which dates show unusual volume or price movements?",
            f"The dates with the highest trading volumes are: {volume_summary}. The dates with the largest absolute price movements are: {return_summary}. These dates should be highlighted in the Close-versus-Volume chart and the price trend chart.",
            "Candidate anomalies are ranked by highest volume and largest absolute daily return; they are not automatically treated as data errors.",
        ],
        [
            "5. Are Shares Issued stable, and are capitalisation changes mainly caused by price or share count?",
            f"Shares Issued range from {min(shares_values):,} to {max(shares_values):,} and {('remain constant during the available period' if shares_stable else 'change during the available period')}. Market Capitalisation = Close x Shares Issued. Therefore, if the share count remains constant, changes in market capitalisation are mainly caused by changes in the Close price.",
            "Market capitalisation is calculated as closing price multiplied by shares issued.",
        ],
        [
            "6. Are Dividend and PE data available for the financial year? If not, which analyses require alternatives?",
            "Dividend and PE are not provided in the current price dataset. Direct empirical analysis of Dividend Yield and PE cannot be performed, and the report should explain this limitation. Dividend analysis can use Close price trends or buy-and-hold portfolio value as an alternative. PE analysis should be labelled Not available; blank values must not be changed to zero.",
            "Dividend and PE are treated as unavailable fields in the standalone EDA workbook.",
        ],
    ]
    write_rows(sheet, rows)
    style_table(sheet)
    for row in sheet.iter_rows(min_row=3):
        row[1].alignment = Alignment(wrap_text=True, vertical="top")
        row[2].alignment = Alignment(wrap_text=True, vertical="top")
    sheet.column_dimensions["A"].width = 48
    sheet.column_dimensions["B"].width = 110
    sheet.column_dimensions["C"].width = 55


def add_daily_analysis(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    sheet = workbook.create_sheet("Daily_Analysis")
    add_title(sheet, "Daily EDA Analysis Data", 12)
    headers = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Daily Volume",
        "Shares Issued",
        "Previous Close",
        "Daily Return",
        "Price Change",
        "Market Capitalisation",
        "Cumulative Return",
    ]
    sheet.append(headers)
    first_close = prices[0]["Close"]
    for index, row in enumerate(prices):
        previous_close = prices[index - 1]["Close"] if index else None
        daily_return = (
            row["Close"] / previous_close - 1
            if previous_close not in (None, 0)
            else None
        )
        sheet.append(
            [
                row["Date"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Daily Volume"],
                row["Shares Issued"],
                previous_close,
                daily_return,
                None if previous_close is None else row["Close"] - previous_close,
                row["Close"] * row["Shares Issued"],
                row["Close"] / first_close - 1,
            ]
        )
    style_table(sheet, header_row=2)
    for row in sheet.iter_rows(min_row=3):
        row[0].number_format = "dd/mm/yyyy"
        for index in [1, 2, 3, 4, 7, 9]:
            row[index].number_format = "$0.000"
        row[5].number_format = "#,##0"
        row[6].number_format = "#,##0"
        row[8].number_format = "0.00%"
        row[10].number_format = "$#,##0"
        row[11].number_format = "0.00%"


def main() -> None:
    prices = load_prices()
    if not prices:
        raise RuntimeError("No price records found in the requested period.")

    workbook = Workbook()
    workbook.remove(workbook.active)
    add_eda_summary(workbook, prices)
    add_data_dictionary(workbook)
    add_descriptive_stats(workbook, prices)
    add_eda_questions(workbook, prices)
    add_daily_analysis(workbook, prices)
    workbook.save(OUTPUT_FILE)
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Records: {len(prices)}")
    print(f"Available period: {prices[0]['Date']} to {prices[-1]['Date']}")


if __name__ == "__main__":
    main()
