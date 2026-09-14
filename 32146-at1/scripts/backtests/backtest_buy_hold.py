"""Backtest a $1,000 buy-and-hold PSQ portfolio with backtrader."""

import csv
from datetime import date, datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "pricehistory-dailyadj.csv"
OUTPUT_DIR = ROOT / "report" / "backtests"
OUTPUT_CSV = OUTPUT_DIR / "buy_hold_daily.csv"
OUTPUT_PNG = OUTPUT_DIR / "buy_hold_portfolio.png"
START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)
INITIAL_CAPITAL = 1000.0


def load_prices() -> pd.DataFrame:
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as source:
        rows = []
        for row in csv.DictReader(source):
            trading_date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
            if START_DATE <= trading_date <= END_DATE:
                rows.append(
                    {
                        "date": trading_date,
                        "close": float(row["Close"]),
                        "volume": int(float(row["Volume"])),
                    }
                )
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.set_index("date").sort_index()
    frame.columns = ["Close", "Volume"]
    frame["Open"] = frame["Close"]
    frame["High"] = frame["Close"]
    frame["Low"] = frame["Close"]
    return frame[["Open", "High", "Low", "Close", "Volume"]]


class BuyAndHold(bt.Strategy):
    def __init__(self) -> None:
        self.equity_curve = []

    def next(self) -> None:
        if not self.position:
            shares = int(self.broker.getcash() // self.data.close[0])
            if shares > 0:
                self.buy(size=shares)
        self.equity_curve.append(
            {
                "Date": self.data.datetime.date(0),
                "Equity": self.broker.getvalue(),
            }
        )


def main() -> None:
    prices = load_prices()
    prices = prices[(prices["Volume"] > 0) & (prices["Close"] > 0)]
    if prices.empty:
        raise RuntimeError("No tradable price records found.")

    feed = bt.feeds.PandasData(dataname=prices)
    cerebro = bt.Cerebro()
    cerebro.adddata(feed)
    cerebro.addstrategy(BuyAndHold)
    cerebro.broker.setcash(INITIAL_CAPITAL)
    cerebro.broker.setcommission(commission=0)
    cerebro.broker.set_coc(True)
    strategies = cerebro.run()
    strategy = strategies[0]
    equity = pd.DataFrame(strategy.equity_curve).set_index("Date")
    equity.index = pd.to_datetime(equity.index)
    equity["Return"] = equity["Equity"] / INITIAL_CAPITAL - 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    equity.to_csv(OUTPUT_CSV)
    figure = cerebro.plot(style="line", volume=False, iplot=False)[0][0]
    figure.savefig(OUTPUT_PNG, dpi=180, bbox_inches="tight")

    final_value = cerebro.broker.getvalue()
    print(f"Buy-and-hold final value: ${final_value:.2f}")
    print(f"Buy-and-hold return: {final_value / INITIAL_CAPITAL - 1:.2%}")
    print(f"Saved: {OUTPUT_CSV}")
    print(f"Saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
