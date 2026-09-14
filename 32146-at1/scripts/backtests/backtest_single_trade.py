"""Run the hindsight-best single trade through backtrader."""

import csv
from datetime import date, datetime
from pathlib import Path

import backtrader as bt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "pricehistory-dailyadj.csv"
OUTPUT_DIR = ROOT / "report" / "backtests"
OUTPUT_CSV = OUTPUT_DIR / "single_trade_summary.csv"
OUTPUT_PNG = OUTPUT_DIR / "single_trade_max_profit.png"
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


def find_best_dates(prices: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    best = None
    for buy_date, buy in prices.iloc[1:-1].iterrows():
        shares = int(INITIAL_CAPITAL // buy["Close"])
        for sell_date, sell in prices.loc[buy_date:].iloc[1:].iterrows():
            profit = shares * (sell["Close"] - buy["Close"])
            if shares and (best is None or profit > best[0]):
                best = (profit, buy_date, sell_date)
    if best is None:
        raise RuntimeError("No valid single trade found.")
    return best[1], best[2]


class SingleTrade(bt.Strategy):
    buy_date = None
    sell_date = None

    def __init__(self) -> None:
        self.trade_record = None
        self.entry_date = None
        self.entry_price = None
        self.entry_size = None

    def notify_order(self, order) -> None:
        if order.status != order.Completed:
            return
        if order.isbuy():
            self.entry_date = self.data.datetime.date(0)
            self.entry_price = order.executed.price
            self.entry_size = order.executed.size
        elif order.issell():
            self.exit_date = self.data.datetime.date(0)

    def notify_trade(self, trade) -> None:
        if trade.isclosed:
            self.trade_record = {
                "Buy Date": self.entry_date.isoformat(),
                "Buy Price": self.entry_price,
                "Sell Date": self.exit_date.isoformat(),
                "Sell Price": self.data.close[0],
                "Shares": int(self.entry_size),
                "Profit": trade.pnl,
                "Return": trade.pnl / INITIAL_CAPITAL,
                "Assumption": "Hindsight optimum executed by backtrader; no fees or slippage",
            }

    def next(self) -> None:
        current_date = self.data.datetime.date(0)
        if current_date == self.buy_date and not self.position:
            shares = int(self.broker.getcash() // self.data.close[0])
            if shares > 0:
                self.buy(size=shares)
        elif current_date == self.sell_date and self.position:
            self.close()


def main() -> None:
    prices = load_prices()
    if len(prices) < 2:
        raise RuntimeError("At least two tradable records are required.")

    buy_date, sell_date = find_best_dates(prices)
    SingleTrade.buy_date = buy_date.date()
    SingleTrade.sell_date = sell_date.date()
    feed = bt.feeds.PandasData(dataname=prices)
    cerebro = bt.Cerebro()
    cerebro.adddata(feed)
    cerebro.addstrategy(SingleTrade)
    cerebro.broker.setcash(INITIAL_CAPITAL)
    cerebro.broker.setcommission(commission=0)
    cerebro.broker.set_coc(True)
    strategies = cerebro.run()
    strategy = strategies[0]
    best = strategy.trade_record
    if best is None:
        raise RuntimeError("Backtrader did not execute the single trade.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=best.keys())
        writer.writeheader()
        writer.writerow(best)

    figure = cerebro.plot(style="line", volume=False, iplot=False)[0][0]
    figure.savefig(OUTPUT_PNG, dpi=180, bbox_inches="tight")

    print(f"Single-trade profit: ${best['Profit']:.2f}")
    print(f"Buy: {best['Buy Date']} at ${best['Buy Price']:.3f}")
    print(f"Sell: {best['Sell Date']} at ${best['Sell Price']:.3f}")
    print(f"Saved: {OUTPUT_CSV}")
    print(f"Saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
