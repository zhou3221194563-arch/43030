"""Build the organized AT1 Excel workbook for Pacific Smiles Group (PSQ)."""

import csv
from copy import copy
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = ROOT / "data"
PRICE_FILE = DATA_DIR / "pricehistory-dailyadj.csv"
DIVIDEND_FILE = DATA_DIR / "dividendhistory.csv"
WORKBOOK_FILE = DATA_DIR / "price_preprocess.xlsx"
EDA_WORKBOOK_FILE = DATA_DIR / "eda_analysis.xlsx"
CHART_DIR = ROOT / "report" / "charts_preview"
BACKTEST_DIR = ROOT / "report" / "backtests"

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
                "Time Series": trading_date,
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
        key=lambda row: row["Time Series"],
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


def add_table_sheet(
    workbook: Workbook,
    title: str,
    headers: list[str],
    rows: list[list[object]],
) -> None:
    sheet = workbook.create_sheet(title)
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    style_sheet(sheet)
    return sheet


def add_raw_data_sheet(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    headers = list(prices[0])
    rows = [[row[field] for field in headers] for row in prices]
    sheet = add_table_sheet(workbook, "Raw_Data", headers, rows)

    for row in sheet.iter_rows(min_row=2):
        row[0].number_format = "dd/mm/yyyy"
        for cell in row[3:7]:
            cell.number_format = "0.000"
        row[7].number_format = "#,##0"
        row[8].number_format = "#,##0"
        row[9].number_format = "0.00"
        row[10].number_format = "0.00"


def add_clean_data_sheet(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    headers = [
        "Time Series",
        "ASX Code",
        "Company Name",
        "Original Open",
        "Original High",
        "Original Low",
        "Close",
        "Daily Volume",
        "Stock Issued",
        "Dividend",
        "PE",
        "Open",
        "High",
        "Low",
        "Zero Volume Flag",
        "Price Adjusted Flag",
        "Price Adjustment Rule",
        "Previous Close",
        "Daily Return",
        "Price Change",
        "Market Capitalisation",
        "Dividend Yield",
        "5-Day Moving Average",
        "Cumulative Return",
    ]
    rows = []
    for index, row in enumerate(prices):
        zero_volume = row["Daily Volume"] == 0
        cleaned_ohlc = {
            column: row[column] if row[column] != 0 else row["Close"]
            for column in ["Open", "High", "Low"]
        }
        price_adjusted = any(row[column] == 0 for column in ["Open", "High", "Low"])
        previous_close = prices[index - 1]["Close"] if index > 0 else None
        daily_return = (
            row["Close"] / previous_close - 1
            if previous_close not in (None, 0)
            else None
        )
        first_close = prices[0]["Close"]
        moving_start = max(0, index - 4)
        moving_average = sum(
            price["Close"] for price in prices[moving_start : index + 1]
        ) / len(prices[moving_start : index + 1])
        rows.append(
            [
                row["Time Series"],
                row["ASX Code"],
                row["Company Name"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Daily Volume"],
                row["Stock Issued"],
                row["Dividend"],
                row["PE"],
                cleaned_ohlc["Open"],
                cleaned_ohlc["High"],
                cleaned_ohlc["Low"],
                "Yes" if zero_volume else "No",
                "Yes" if price_adjusted else "No",
                (
                    "For each of Open, High and Low: if the raw value equals 0, replace it with the same-day Close; otherwise retain the raw value."
                ),
                previous_close,
                daily_return,
                None if previous_close is None else row["Close"] - previous_close,
                row["Close"] * row["Stock Issued"],
                None if row["Dividend"] is None else row["Dividend"] / row["Close"],
                moving_average,
                row["Close"] / first_close - 1,
            ]
        )
    sheet = add_table_sheet(workbook, "Clean_Data", headers, rows)
    for row in sheet.iter_rows(min_row=2):
        row[0].number_format = "dd/mm/yyyy"
        for cell in list(row[3:7]) + list(row[11:14]):
            cell.number_format = "0.000"
        row[7].number_format = "0.000"
        row[8].number_format = "#,##0"
        row[9].number_format = "#,##0"
        row[10].number_format = "0.00"
        row[17].number_format = "0.000"
        row[18].number_format = "0.00%"
        row[19].number_format = "0.000"
        row[20].number_format = "$#,##0"
        row[21].number_format = "0.00%"
        row[22].number_format = "0.000"
        row[23].number_format = "0.00%"


def add_readme_sheet(
    workbook: Workbook, prices: list[dict[str, object]], dividend_count: int
) -> None:
    sheet = workbook.create_sheet("README")
    rows = [
        ["Company", "Pacific Smiles Group Ltd"],
        ["ASX Code", prices[0]["ASX Code"]],
        ["Assessment", "32146 Data Visualisation Foundations - AT1"],
        ["Requested period", f"{START_DATE} to {END_DATE}"],
        [
            "Available price period",
            f"{prices[0]['Time Series']} to {prices[-1]['Time Series']}",
        ],
        [
            "Data source",
            "DatAnalysis export: pricehistory-dailyadj.csv and dividendhistory.csv",
        ],
        [
            "Coverage note",
            "The supplied price file ends on 05/11/2025; FY2025-26 is incomplete.",
        ],
        ["Dividend records in requested period", dividend_count],
        ["Dividend treatment", "Blank where no FY2025-26 dividend record is supplied."],
        ["PE treatment", "Blank because no PE field is supplied in the source data."],
        [
            "Zero-volume treatment",
            "Zero-volume rows are retained and flagged; raw OHLC values are not overwritten.",
        ],
        [
            "Workbook structure",
            "Raw_Data is unchanged source data; Clean_Data adds analysis flags; later sheets contain EDA, calculations and charts.",
        ],
    ]
    sheet.append(["Item", "Description"])
    for row in rows:
        sheet.append(row)
    style_sheet(sheet)
    sheet.column_dimensions["A"].width = 32
    sheet.column_dimensions["B"].width = 100
    for row in sheet.iter_rows(min_row=2):
        row[0].font = Font(bold=True)
        row[1].alignment = Alignment(wrap_text=True, vertical="top")


def add_eda_sheet(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    closes = [row["Close"] for row in prices]
    volumes = [row["Daily Volume"] for row in prices]
    rows = [
        ["Metric", "Value", "Note"],
        ["Price records", len(prices), "Rows within the requested date range"],
        ["First available date", prices[0]["Time Series"], "From supplied price file"],
        ["Last available date", prices[-1]["Time Series"], "From supplied price file"],
        ["Minimum close", min(closes), "Currency per share"],
        ["Maximum close", max(closes), "Currency per share"],
        ["Average close", sum(closes) / len(closes), "Currency per share"],
        ["Total volume", sum(volumes), "Shares traded in supplied records"],
        [
            "Average daily volume",
            sum(volumes) / len(volumes),
            "Includes zero-volume records",
        ],
        [
            "Zero-volume records",
            sum(volume == 0 for volume in volumes),
            "Retained and flagged in Clean_Data",
        ],
        [
            "Dividend missing values",
            len(prices),
            "No dividend field supplied in price source",
        ],
        ["PE missing values", len(prices), "No PE field supplied in price source"],
    ]
    sheet = workbook.create_sheet("EDA")
    for row in rows:
        sheet.append(row)
    style_sheet(sheet)
    sheet.column_dimensions["A"].width = 28
    sheet.column_dimensions["B"].width = 20
    sheet.column_dimensions["C"].width = 65
    for row in sheet.iter_rows(min_row=2):
        row[2].alignment = Alignment(wrap_text=True, vertical="top")


def get_tradable_prices(prices: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in prices if row["Daily Volume"] > 0 and row["Close"] > 0]


def find_single_trade(prices: list[dict[str, object]]) -> dict[str, object]:
    tradable = get_tradable_prices(prices)
    best: dict[str, object] | None = None
    for buy_index, buy_row in enumerate(tradable[:-1]):
        shares = int(1000 // buy_row["Close"])
        if shares == 0:
            continue
        for sell_row in tradable[buy_index + 1 :]:
            profit = shares * (sell_row["Close"] - buy_row["Close"])
            candidate = {
                "Buy Date": buy_row["Time Series"],
                "Buy Price": buy_row["Close"],
                "Sell Date": sell_row["Time Series"],
                "Sell Price": sell_row["Close"],
                "Shares": shares,
                "Initial Cash": 1000 - shares * buy_row["Close"],
                "Profit": profit,
                "Return": profit / 1000,
            }
            if best is None or candidate["Profit"] > best["Profit"]:
                best = candidate
    if best is None:
        raise RuntimeError("At least two tradable price records are required.")
    return best


def find_multiple_trades(prices: list[dict[str, object]]) -> list[dict[str, object]]:
    tradable = get_tradable_prices(prices)
    trades = []
    index = 0
    cash = 1000.0
    while index < len(tradable) - 1:
        buy_index = index
        while (
            buy_index < len(tradable) - 1
            and tradable[buy_index + 1]["Close"] <= tradable[buy_index]["Close"]
        ):
            buy_index += 1
        sell_index = buy_index
        while (
            sell_index < len(tradable) - 1
            and tradable[sell_index + 1]["Close"] >= tradable[sell_index]["Close"]
        ):
            sell_index += 1
        if sell_index == buy_index:
            break

        buy_row = tradable[buy_index]
        sell_row = tradable[sell_index]
        shares = int(cash // buy_row["Close"])
        if shares == 0:
            break
        starting_cash = cash
        cash = cash + shares * (sell_row["Close"] - buy_row["Close"])
        trades.append(
            {
                "Trade": len(trades) + 1,
                "Buy Date": buy_row["Time Series"],
                "Buy Price": buy_row["Close"],
                "Sell Date": sell_row["Time Series"],
                "Sell Price": sell_row["Close"],
                "Shares": shares,
                "Starting Cash": starting_cash,
                "Ending Cash": cash,
                "Profit": cash - starting_cash,
                "Return": (cash - starting_cash) / starting_cash,
            }
        )
        index = sell_index + 1
    return trades


def add_calculations_sheet(workbook: Workbook, prices: list[dict[str, object]]) -> None:
    sheet = workbook.create_sheet("Calculations")
    sheet.append(
        [
            "Daily analysis uses Clean_Data. Return and market capitalisation are formula fields; trade rows exclude zero-volume records.",
        ]
    )
    sheet.merge_cells("A1:M1")
    sheet.append(
        [
            "Date",
            "Close",
            "Daily Volume",
            "Shares Issued",
            "Previous Close",
            "Daily Return",
            "Price Change",
            "Market Capitalisation",
            "Dividend Yield",
            "5-Day Moving Average",
            "Cumulative Return",
            "Tradable Record",
        ]
    )
    for row_index, row in enumerate(prices, start=3):
        previous_close = prices[row_index - 3]["Close"] if row_index > 3 else None
        sheet.append(
            [
                row["Time Series"],
                row["Close"],
                row["Daily Volume"],
                row["Stock Issued"],
                previous_close,
                None if row_index == 3 else f"=B{row_index}/B{row_index - 1}-1",
                None if row_index == 3 else f"=B{row_index}-B{row_index - 1}",
                f"=B{row_index}*D{row_index}",
                None,
                f"=AVERAGE(B{max(3, row_index - 4)}:B{row_index})",
                f"=B{row_index}/$B$3-1",
                "Yes" if row["Daily Volume"] > 0 and row["Close"] > 0 else "No",
            ]
        )
    style_sheet(sheet)
    sheet.auto_filter.ref = f"A2:M{len(prices) + 2}"
    sheet.freeze_panes = "A3"
    for row in sheet.iter_rows(min_row=3):
        row[0].number_format = "dd/mm/yyyy"
        row[1].number_format = "$0.000"
        row[2].number_format = "#,##0"
        row[3].number_format = "#,##0"
        row[4].number_format = "$0.000"
        row[5].number_format = "0.00%"
        row[6].number_format = "$0.000"
        row[7].number_format = "$#,##0"
        row[8].number_format = "0.00%"
        row[9].number_format = "$0.000"
        row[10].number_format = "0.00%"
        row[11].number_format = "0.00%"

    first_tradable = get_tradable_prices(prices)[0]
    last_tradable = get_tradable_prices(prices)[-1]
    buy_shares = int(1000 // first_tradable["Close"])
    buy_cash = 1000 - buy_shares * first_tradable["Close"]
    holding_value = buy_shares * last_tradable["Close"] + buy_cash
    single_trade = find_single_trade(prices)
    multiple_trades = find_multiple_trades(prices)

    start_row = sheet.max_row + 3
    sheet.cell(start_row, 1, "$1,000 Buy-and-Hold Portfolio")
    sheet.cell(start_row, 1).font = Font(bold=True, size=12)
    portfolio_rows = [
        ["Initial capital", 1000, "Assumption"],
        ["Buy date", first_tradable["Time Series"], "First tradable record"],
        ["Buy price", first_tradable["Close"], "Close price"],
        ["Shares purchased", buy_shares, "INT(Initial capital / Buy price)"],
        ["Remaining cash", buy_cash, "Initial capital - Shares x Buy price"],
        [
            "Valuation date",
            last_tradable["Time Series"],
            "Last tradable record available",
        ],
        ["Ending close", last_tradable["Close"], "Close price"],
        [
            "Ending portfolio value",
            holding_value,
            "Shares x Ending close + Remaining cash",
        ],
        ["Portfolio profit", holding_value - 1000, "Ending value - Initial capital"],
        [
            "Portfolio return",
            holding_value / 1000 - 1,
            "Ending value / Initial capital - 1",
        ],
        [
            "Dividend treatment",
            "No dividend added",
            "No FY2025-26 dividend record supplied",
        ],
    ]
    for row in portfolio_rows:
        sheet.append(row)
    for row in sheet.iter_rows(min_row=start_row + 1, max_row=sheet.max_row):
        row[0].font = Font(bold=True)
        row[2].alignment = Alignment(wrap_text=True)
    sheet.cell(start_row + 3, 2).number_format = "$0.000"
    sheet.cell(start_row + 4, 2).number_format = "#,##0"
    for row_number in [start_row + 5, start_row + 7, start_row + 8, start_row + 9]:
        sheet.cell(row_number, 2).number_format = "$#,##0.00"
    sheet.cell(start_row + 10, 2).number_format = "0.00%"

    single_row = sheet.max_row + 3
    sheet.cell(single_row, 1, "Single Trade Maximum Profit")
    sheet.cell(single_row, 1).font = Font(bold=True, size=12)
    for key, value in single_trade.items():
        sheet.append(
            [key, value, "Uses close prices, $1,000 limit, no fees or slippage"]
        )
    for row in sheet.iter_rows(min_row=single_row + 1, max_row=sheet.max_row):
        row[0].font = Font(bold=True)
        row[2].alignment = Alignment(wrap_text=True)
    for row in range(single_row + 1, sheet.max_row + 1):
        if row in [single_row + 2, single_row + 4, single_row + 6, single_row + 7]:
            sheet.cell(row, 2).number_format = "$0.000"
        if row == single_row + 8:
            sheet.cell(row, 2).number_format = "0.00%"

    multiple_row = sheet.max_row + 3
    sheet.cell(multiple_row, 1, "Multiple Trades")
    sheet.cell(multiple_row, 1).font = Font(bold=True, size=12)
    sheet.append(
        [
            "Trade",
            "Buy Date",
            "Buy Price",
            "Sell Date",
            "Sell Price",
            "Shares",
            "Starting Cash",
            "Ending Cash",
            "Profit",
            "Return",
        ]
    )
    for trade in multiple_trades:
        sheet.append([trade[key] for key in trade])
    for row in sheet.iter_rows(min_row=multiple_row + 1, max_row=sheet.max_row):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        for column in [2, 4]:
            row[column].number_format = "$0.000"
        for column in [6, 7, 8, 9]:
            row[column].number_format = "$#,##0.00"
        row[10 - 1].number_format = "0.00%"
    sheet.column_dimensions["A"].width = 28
    for column in range(2, 11):
        sheet.column_dimensions[get_column_letter(column)].width = 18


def add_placeholder_sheet(workbook: Workbook, title: str, purpose: str) -> None:
    sheet = workbook.create_sheet(title)
    sheet.append(["Purpose"])
    sheet.append([purpose])
    style_sheet(sheet)
    sheet.column_dimensions["A"].width = 110
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")


def copy_worksheet_content(source_sheet, target_sheet) -> None:
    """Copy an EDA worksheet into the consolidated submission workbook."""
    for row in source_sheet.iter_rows():
        for source_cell in row:
            if isinstance(source_cell, MergedCell):
                continue
            target_cell = target_sheet.cell(
                source_cell.row, source_cell.column, source_cell.value
            )
            if source_cell.has_style:
                target_cell.font = copy(source_cell.font)
                target_cell.fill = copy(source_cell.fill)
                target_cell.border = copy(source_cell.border)
            if source_cell.number_format:
                target_cell.number_format = source_cell.number_format
            if source_cell.alignment:
                target_cell.alignment = copy(source_cell.alignment)
            if source_cell.protection:
                target_cell.protection = copy(source_cell.protection)
            if source_cell.hyperlink:
                target_cell._hyperlink = copy(source_cell.hyperlink)
            if source_cell.comment:
                target_cell.comment = copy(source_cell.comment)

    for merged_range in source_sheet.merged_cells.ranges:
        target_sheet.merge_cells(str(merged_range))
    for column, dimension in source_sheet.column_dimensions.items():
        target_sheet.column_dimensions[column].width = dimension.width
        target_sheet.column_dimensions[column].hidden = dimension.hidden
    for row, dimension in source_sheet.row_dimensions.items():
        target_sheet.row_dimensions[row].height = dimension.height
        target_sheet.row_dimensions[row].hidden = dimension.hidden
    target_sheet.freeze_panes = source_sheet.freeze_panes
    target_sheet.auto_filter.ref = source_sheet.auto_filter.ref


def add_eda_workbook_sheets(workbook: Workbook) -> None:
    """Embed the completed standalone EDA workbook in the submission workbook."""
    if not EDA_WORKBOOK_FILE.exists():
        raise FileNotFoundError(f"EDA workbook not found: {EDA_WORKBOOK_FILE}")

    source_workbook = load_workbook(EDA_WORKBOOK_FILE, data_only=False)
    for source_sheet in source_workbook.worksheets:
        if source_sheet.title in workbook.sheetnames:
            workbook.remove(workbook[source_sheet.title])
        target_sheet = workbook.create_sheet(source_sheet.title)
        copy_worksheet_content(source_sheet, target_sheet)


def add_charts_sheet(workbook: Workbook) -> None:
    """Embed all eight required visualisations as images in one Excel sheet."""
    chart_files = [
        (
            "Figure 1 - Close price versus volume",
            CHART_DIR / "chart_01_close_vs_volume.png",
        ),
        ("Figure 2 - OHLC stock movement", CHART_DIR / "kline.png"),
        (
            "Figure 3 - Capitalisation versus issued shares",
            CHART_DIR / "chart_02_capital_vs_shares.png",
        ),
        (
            "Figure 4 - Close price and dividend alternative",
            CHART_DIR / "chart_03_close_dividend_alternative.png",
        ),
        (
            "Figure 5 - Daily return volatility",
            CHART_DIR / "chart_04_daily_return_volatility.png",
        ),
        (
            "Figure 6 - $1,000 buy-and-hold portfolio",
            BACKTEST_DIR / "buy_hold_portfolio.png",
        ),
        (
            "Figure 7 - Single-trade maximum profit",
            BACKTEST_DIR / "single_trade_max_profit.png",
        ),
        (
            "Figure 8 - Multiple-trade equity",
            BACKTEST_DIR / "multiple_trades_equity.png",
        ),
    ]
    sheet = workbook.create_sheet("Charts")
    sheet["A1"] = "PSQ AT1 Visualisations"
    sheet["A1"].font = Font(size=16, bold=True, color="FFFFFF")
    sheet["A1"].fill = PatternFill("solid", fgColor="1F4E78")
    sheet.merge_cells("A1:H1")
    sheet["A2"] = (
        "All eight required visualisations are embedded below. Source data and calculations are provided in the other worksheets."
    )
    sheet["A2"].alignment = Alignment(wrap_text=True)
    sheet.merge_cells("A2:H2")
    sheet.column_dimensions["A"].width = 24

    for index, (caption, chart_file) in enumerate(chart_files):
        if not chart_file.exists():
            raise FileNotFoundError(f"Required chart not found: {chart_file}")
        row = 4 + (index // 2) * 30
        column = 1 if index % 2 == 0 else 10
        caption_cell = sheet.cell(row, column, caption)
        caption_cell.font = Font(bold=True)
        caption_cell.alignment = Alignment(wrap_text=True)
        image = ExcelImage(chart_file)
        image.width = 640
        image.height = 320
        sheet.add_image(image, f"{get_column_letter(column)}{row + 1}")

    sheet.freeze_panes = "A4"


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
    workbook.remove(workbook.active)
    dividend_count = count_fy_dividends()
    add_readme_sheet(workbook, prices, dividend_count)
    add_raw_data_sheet(workbook, prices)
    add_clean_data_sheet(workbook, prices)
    add_eda_sheet(workbook, prices)
    add_calculations_sheet(workbook, prices)
    add_charts_sheet(workbook)
    add_eda_workbook_sheets(workbook)
    sources = workbook.create_sheet("Sources")
    sources.append(["Item", "Details"])
    sources.append(
        [
            "Primary source",
            "DatAnalysis export supplied for Pacific Smiles Group Ltd (ASX: PSQ)",
        ]
    )
    sources.append(["Price source file", "data/pricehistory-dailyadj.csv"])
    sources.append(["Dividend source file", "data/dividendhistory.csv"])
    sources.append(["Requested period", "01/07/2025 to 30/06/2026"])
    sources.append(
        ["Available period", "01/07/2025 to 05/11/2025; PSQ was acquired and delisted"]
    )
    sources.append(
        [
            "Raw-data treatment",
            "Raw_Data preserves source OHLC values, including zero values and zero-volume records.",
        ]
    )
    sources.append(
        [
            "Cleaning treatment",
            "Clean_Data replaces zero Open, High and Low values with same-day Close for display calculations and flags the adjustment.",
        ]
    )
    sources.append(
        [
            "Missing fields",
            "Dividend and PE are blank because no usable values are supplied in the source data.",
        ]
    )
    sources.append(
        [
            "Embedded analysis",
            "EDA_Summary, Data_Dictionary, Descriptive_Stats, EDA_Questions and Daily_Analysis were copied from eda_analysis.xlsx.",
        ]
    )
    style_sheet(sources)
    sources.column_dimensions["A"].width = 28
    sources.column_dimensions["B"].width = 110
    for row in sources.iter_rows(min_row=2):
        row[0].font = Font(bold=True)
        row[1].alignment = Alignment(wrap_text=True, vertical="top")
    add_summary_sheet(workbook, prices, dividend_count)
    workbook.save(WORKBOOK_FILE)
    print(f"Saved: {WORKBOOK_FILE}")


if __name__ == "__main__":
    main()
