"""Run repeated buy-low/sell-high trades through backtrader."""

import csv
from datetime import date, datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "pricehistory-dailyadj.csv"
OUTPUT_DIR = ROOT / "report" / "backtests"
OUTPUT_CSV = OUTPUT_DIR / "multiple_trades_ledger.csv"
OUTPUT_PNG = OUTPUT_DIR / "multiple_trades_equity.png"
START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)
INITIAL_CAPITAL = 1000.0


def load_prices() -> pd.DataFrame:
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as source:
        rows = []
        for row in csv.DictReader(source):
            trading_date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
            if START_DATE <= trading_date <= END_DATE and int(float(row["Volume"])) > 0:
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


def find_signal_dates(prices: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    signals = []
    index = 1
    while index < len(prices) - 1:
        buy_index = index
        while (
            buy_index < len(prices) - 1
            and prices.iloc[buy_index + 1]["Close"] <= prices.iloc[buy_index]["Close"]
        ):
            buy_index += 1
        sell_index = buy_index
        while (
            sell_index < len(prices) - 1
            and prices.iloc[sell_index + 1]["Close"] >= prices.iloc[sell_index]["Close"]
        ):
            sell_index += 1
        if sell_index == buy_index:
            break
        signals.append((prices.index[buy_index], prices.index[sell_index]))
        index = sell_index + 1
    return signals


class MultipleTrades(bt.Strategy):
    signal_dates = []

    def __init__(self) -> None:
        self.equity_curve = []
        self.trade_records = []
        self.entry_date = None
        self.entry_price = None
        self.entry_size = None

    def notify_order(self, order) -> None:
        if order.status != order.Completed:
            return
        execution_date = self.data.datetime.datetime(0)
        if order.isbuy():
            self.entry_date = execution_date
            self.entry_price = order.executed.price
            self.entry_size = order.executed.size
        elif order.issell():
            self.exit_date = execution_date

    def notify_trade(self, trade) -> None:
        if trade.isclosed:
            self.trade_records.append(
                {
                    "EntryTime": self.entry_date,
                    "ExitTime": self.exit_date,
                    "Size": self.entry_size,
                    "PnL": trade.pnl,
                    "Equity After Trade": self.broker.getvalue(),
                }
            )

    def next(self) -> None:
        current_date = self.data.datetime.date(0)
        for buy_date, sell_date in self.signal_dates:
            if current_date == buy_date and not self.position:
                shares = int(self.broker.getcash() // self.data.close[0])
                if shares > 0:
                    self.buy(size=shares)
            elif current_date == sell_date and self.position:
                self.close()
        self.equity_curve.append(
            {"Date": self.data.datetime.date(0), "Equity": self.broker.getvalue()}
        )


def main() -> None:
    prices = load_prices()
    signals = find_signal_dates(prices)
    if not signals:
        raise RuntimeError("No profitable multiple-trade sequence found.")

    MultipleTrades.signal_dates = [(buy.date(), sell.date()) for buy, sell in signals]
    feed = bt.feeds.PandasData(dataname=prices)
    cerebro = bt.Cerebro()
    cerebro.adddata(feed)
    cerebro.addstrategy(MultipleTrades)
    cerebro.broker.setcash(INITIAL_CAPITAL)
    cerebro.broker.setcommission(commission=0)
    cerebro.broker.set_coc(True)
    strategies = cerebro.run()
    strategy = strategies[0]
    ledger = pd.DataFrame(strategy.trade_records)
    if ledger.empty:
        raise RuntimeError("Backtrader did not execute multiple trades.")
    ledger.to_csv(OUTPUT_CSV, index=False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure = cerebro.plot(style="line", volume=False, iplot=False)[0][0]
    figure.savefig(OUTPUT_PNG, dpi=180, bbox_inches="tight")

    print(f"Multiple trades: {len(ledger)}")
    final_equity = cerebro.broker.getvalue()
    print(f"Final equity: ${final_equity:.2f}")
    print(f"Total return: {(final_equity / INITIAL_CAPITAL - 1) * 100:.2f}%")
    print(f"Saved: {OUTPUT_CSV}")
    print(f"Saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
