"""Build the first AT1 Excel workbook for Pacific Smiles Group (PSQ)."""

import csv
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = ROOT / "data"
PRICE_FILE = DATA_DIR / "pricehistory-dailyadj.csv"
DIVIDEND_FILE = DATA_DIR / "dividendhistory.csv"
WORKBOOK_FILE = DATA_DIR / "price_preprocess.xlsx"

START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)


def load_prices() -> list[dict[str, object]]:
    with PRICE_FILE.open(newline="", encoding="utf-8-sig") as source:
        source_rows = list(csv.DictReader(source))

    prices = []
    for row in source_rows:
        trading_date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
        if not START_DATE <= trading_date <= END_DATE:
            continue

        close = float(row["Close"])
        volume = int(float(row["Volume"]))
        ohlc = {name: float(row[name]) for name in ["Open", "High", "Low"]}
        prices.append(
            {
                "Time Series": row["Date"],
                "ASX Code": row["ASX Code"],
                "Company Name": row["Company Name"],
                "Open": ohlc["Open"],
                "High": ohlc["High"],
                "Low": ohlc["Low"],
                "Close": close,
                "Daily Volume": volume,
                "Stock Issued": int(float(row["Shares on Issue"])),
                "Dividend": None,
                "PE": None,
            }
        )
    return sorted(
        prices,
        key=lambda row: datetime.strptime(row["Time Series"], "%d/%m/%Y"),
    )


def count_fy_dividends() -> int:
    with DIVIDEND_FILE.open(newline="", encoding="utf-8-sig") as source:
        rows = csv.DictReader(source)
        return sum(
            START_DATE
            <= datetime.strptime(row["Balance Date"], "%d/%m/%Y").date()
            <= END_DATE
            for row in rows
        )


def style_sheet(sheet) -> None:
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.row_dimensions[1].height = 32

    for column_cells in sheet.columns:
        width = min(max(len(str(cell.value or "")) for cell in column_cells) + 2, 28)
        sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = width


def add_data_sheet(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    sheet = workbook.active
    sheet.title = "Price Data"
    fields = list(prices[0])
    sheet.append(fields)
    for row in prices:
        sheet.append([row[field] for field in fields])

    for row in sheet.iter_rows(min_row=2):
        for cell in row[3:7]:
            cell.number_format = "0.000"
        row[7].number_format = "#,##0"
        row[8].number_format = "#,##0"
        row[9].number_format = "0.00"
        row[10].number_format = "0.00"
    style_sheet(sheet)


def add_summary_sheet(
    workbook: Workbook, prices: list[dict[str, object]], dividend_count: int
) -> None:
    sheet = workbook.create_sheet("Summary")
    sheet.append(["PSQ Pacific Smiles Group - 32146 AT1 first draft", None])
    sheet.append(
        [
            "Data source",
            "DatAnalysis export: pricehistory-dailyadj.csv and dividendhistory.csv",
        ]
    )
    sheet.append(["Requested period", f"{START_DATE} to {END_DATE}"])
    sheet.append(
        [
            "Available period",
            f"{prices[0]['Time Series']} to {prices[-1]['Time Series']}",
        ]
    )
    sheet.append(
        [
            "Coverage note",
            "The supplied price file ends on 05/11/2025; FY2025-26 is incomplete.",
        ]
    )
    sheet.append(["Rows", len(prices)])
    sheet.append(["Starting close", prices[0]["Close"]])
    sheet.append(["Ending close", prices[-1]["Close"]])
    sheet.append(["Price return", prices[-1]["Close"] / prices[0]["Close"] - 1])
    sheet.append(
        [
            "Zero-volume / suspension rows",
            sum(row["Daily Volume"] == 0 for row in prices),
        ]
    )
    sheet.append(["FY dividend records", dividend_count])
    sheet.append(
        ["Dividend treatment", "Blank: no FY2025-26 dividend record was supplied."]
    )
    sheet.append(
        ["PE treatment", "Blank: no PE field was supplied in the source data."]
    )
    sheet.append(
        [
            "OHLC treatment",
            "Raw Open/High/Low values are preserved. Zero-volume rows are marked separately and must not be interpreted as trades.",
        ]
    )

    sheet["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    sheet["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    sheet.merge_cells("A1:B1")
    for row in range(2, sheet.max_row + 1):
        sheet.cell(row, 1).font = Font(bold=True)
        sheet.cell(row, 1).alignment = Alignment(vertical="top", wrap_text=True)
        sheet.cell(row, 2).alignment = Alignment(vertical="top", wrap_text=True)
    sheet.column_dimensions["A"].width = 28
    sheet.column_dimensions["B"].width = 95
    for row in [7, 8]:
        sheet.cell(row, 2).number_format = "0.000"
    sheet["B9"].number_format = "0.00%"
    sheet.freeze_panes = "A2"


def main() -> None:
    prices = load_prices()
    if not prices:
        raise RuntimeError("No price rows found in the requested period.")

    workbook = Workbook()
    add_data_sheet(workbook, prices)
    add_summary_sheet(workbook, prices, count_fy_dividends())
    workbook.save(WORKBOOK_FILE)
    print(f"Saved: {WORKBOOK_FILE}")


if __name__ == "__main__":
    main()
