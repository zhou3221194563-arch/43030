"""Export standalone preview charts for PSQ AT1 visual analysis."""

import csv
from datetime import date, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
DATA_FILE = ROOT / "data" / "pricehistory-dailyadj.csv"
OUTPUT_DIR = ROOT / "report" / "charts_preview"
START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)


def load_data() -> pd.DataFrame:
    rows = []
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as source:
        for source_row in csv.DictReader(source):
            trading_date = datetime.strptime(source_row["Date"], "%d/%m/%Y").date()
            if not START_DATE <= trading_date <= END_DATE:
                continue
            rows.append(
                {
                    "Date": trading_date,
                    "Open": float(source_row["Open"]),
                    "High": float(source_row["High"]),
                    "Low": float(source_row["Low"]),
                    "Close": float(source_row["Close"]),
                    "Daily Volume": int(float(source_row["Volume"])),
                    "Shares Issued": int(float(source_row["Shares on Issue"])),
                }
            )
    data = pd.DataFrame(rows).sort_values("Date").set_index("Date")
    for column in ["Open", "High", "Low"]:
        data.loc[data[column] == 0, column] = data["Close"]
    data["Market Capitalisation"] = data["Close"] * data["Shares Issued"]
    data["Daily Return"] = data["Close"].pct_change()
    data["Cumulative Return"] = data["Close"] / data["Close"].iloc[0] - 1
    data["5-Day Moving Average"] = data["Close"].rolling(5, min_periods=1).mean()
    return data


def save_figure(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / name, dpi=180, bbox_inches="tight")
    plt.close()


def chart_price_volume(data: pd.DataFrame) -> None:
    figure, price_axis = plt.subplots(figsize=(12, 6))
    volume_axis = price_axis.twinx()
    price_axis.plot(
        data.index, data["Close"], color="#1f77b4", linewidth=2, label="Close price"
    )
    volume_axis.bar(
        data.index,
        data["Daily Volume"],
        color="#b0b7c3",
        alpha=0.35,
        width=1.0,
        label="Daily volume",
    )
    highest_volume_date = data["Daily Volume"].idxmax()
    price_axis.scatter(
        highest_volume_date,
        data.loc[highest_volume_date, "Close"],
        color="#d62728",
        zorder=4,
    )
    price_axis.annotate(
        f"Highest volume\n{highest_volume_date}",
        (highest_volume_date, data.loc[highest_volume_date, "Close"]),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#d62728"},
    )
    price_axis.set_title("PSQ Close Price versus Daily Volume")
    price_axis.set_xlabel("Trading date")
    price_axis.set_ylabel("Close price ($)")
    volume_axis.set_ylabel("Daily volume (shares)")
    price_axis.grid(alpha=0.25)
    price_axis.legend(loc="upper left")
    volume_axis.legend(loc="upper right")
    save_figure("chart_01_close_vs_volume.png")


def chart_ohlc(data: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(12, 6))
    axis.vlines(
        data.index, data["Low"], data["High"], color="#555555", linewidth=0.8, alpha=0.7
    )
    up = data["Close"] >= data["Open"]
    down = ~up
    width = 0.7
    axis.bar(
        data.index[up],
        data.loc[up, "Close"] - data.loc[up, "Open"],
        bottom=data.loc[up, "Open"],
        width=width,
        color="#2ca02c",
        alpha=0.8,
    )
    axis.bar(
        data.index[down],
        data.loc[down, "Close"] - data.loc[down, "Open"],
        bottom=data.loc[down, "Open"],
        width=width,
        color="#d62728",
        alpha=0.8,
    )
    zero_volume_dates = data.index[data["Daily Volume"] == 0]
    if len(zero_volume_dates):
        axis.scatter(
            zero_volume_dates,
            data.loc[zero_volume_dates, "Close"],
            color="#9467bd",
            marker="x",
            s=25,
            label="Zero-volume record",
        )
    axis.set_title("PSQ OHLC Price Movement")
    axis.set_xlabel("Trading date")
    axis.set_ylabel("Price ($)")
    axis.grid(alpha=0.25)
    axis.legend(loc="upper left")
    save_figure("chart_02_ohlc.png")


def chart_capital_shares(data: pd.DataFrame) -> None:
    figure, (capital_axis, shares_axis) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True
    )
    capital_axis.plot(
        data.index,
        data["Market Capitalisation"] / 1_000_000,
        color="#1f77b4",
        linewidth=2,
        label="Market capitalisation",
    )
    shares_axis.plot(
        data.index,
        data["Shares Issued"] / 1_000_000,
        color="#ff7f0e",
        linestyle="--",
        linewidth=1.8,
        label="Shares issued",
    )
    capital_axis.set_title("PSQ Market Capitalisation and Shares Issued")
    capital_axis.set_ylabel("Market capitalisation ($ millions)")
    shares_axis.set_xlabel("Trading date")
    shares_axis.set_ylabel("Shares issued (millions)")
    shares_min = data["Shares Issued"].min() / 1_000_000
    shares_max = data["Shares Issued"].max() / 1_000_000
    shares_axis.set_ylim(161, 162)
    share_change = data["Shares Issued"].max() - data["Shares Issued"].min()
    share_change_pct = share_change / data["Shares Issued"].min() * 100
    shares_axis.text(
        0.01,
        0.88,
        f"Range: {shares_min:.6f}m to {shares_max:.6f}m\nChange: {share_change:,} shares ({share_change_pct:.4f}%)",
        transform=shares_axis.transAxes,
        fontsize=9,
        va="top",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.8},
    )
    capital_axis.grid(alpha=0.25)
    shares_axis.grid(alpha=0.25)
    capital_axis.legend(loc="upper left")
    shares_axis.legend(loc="upper left")
    save_figure("chart_03_capital_vs_shares.png")


def chart_dividend_alternative(data: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(
        data.index, data["Close"], color="#1f77b4", linewidth=2, label="Close price"
    )
    axis.plot(
        data.index,
        data["5-Day Moving Average"],
        color="#ff7f0e",
        linestyle="--",
        linewidth=1.8,
        label="5-day moving average",
    )
    axis.set_title("PSQ Close Price Trend (Dividend Data Unavailable)")
    axis.set_xlabel("Trading date")
    axis.set_ylabel("Close price ($)")
    axis.grid(alpha=0.25)
    axis.legend()
    save_figure("chart_04_close_dividend_alternative.png")


def chart_return_volatility(data: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(12, 6))
    colors = [
        "#2ca02c" if value >= 0 else "#d62728"
        for value in data["Daily Return"].fillna(0)
    ]
    axis.bar(
        data.index,
        data["Daily Return"].fillna(0) * 100,
        color=colors,
        alpha=0.75,
        width=1.0,
    )
    largest_move = data["Daily Return"].abs().idxmax()
    axis.scatter(
        largest_move,
        data.loc[largest_move, "Daily Return"] * 100,
        color="#111111",
        zorder=4,
    )
    axis.annotate(
        f"Largest move\n{largest_move}",
        (largest_move, data.loc[largest_move, "Daily Return"] * 100),
        xytext=(10, 12),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#111111"},
    )
    axis.axhline(0, color="#444444", linewidth=0.8)
    axis.set_title("PSQ Daily Return and Price Volatility")
    axis.set_xlabel("Trading date")
    axis.set_ylabel("Daily return (%)")
    axis.grid(alpha=0.25, axis="y")
    save_figure("chart_05_daily_return_volatility.png")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    if data.empty:
        raise RuntimeError("No price records found in the requested period.")
    chart_price_volume(data)
    chart_ohlc(data)
    chart_capital_shares(data)
    chart_dividend_alternative(data)
    chart_return_volatility(data)
    print(f"Saved five chart previews to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
