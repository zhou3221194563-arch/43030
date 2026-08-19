"""Build the organized PSQ AT1 workbook with calculation sections."""

from data_preprocess import (
    WORKBOOK_FILE,
    add_calculations_sheet,
    add_clean_data_sheet,
    add_eda_sheet,
    add_placeholder_sheet,
    add_raw_data_sheet,
    add_readme_sheet,
    add_summary_sheet,
    count_fy_dividends,
    load_prices,
)
from openpyxl import Workbook


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
    add_placeholder_sheet(
        workbook,
        "Charts",
        "Reserved for the eight required visualisations. Charts should be created from Clean_Data and Calculations.",
    )
    add_placeholder_sheet(
        workbook,
        "Sources",
        "Record the DatAnalysis export name, access date, source screenshots and data verification notes here.",
    )
    add_summary_sheet(workbook, prices, dividend_count)

    workbook.save(WORKBOOK_FILE)
    print(f"Saved: {WORKBOOK_FILE}")


if __name__ == "__main__":
    main()
