# -*- coding: utf-8 -*-
"""PSQ Pacific Smiles Group - FY2025-26 K线图和成交量 (finplot)
- 保留 DatAnalysis 原始 OHLC 数据
- K线下方显示 Daily Volume
- 保存 PNG
用法:
    python kline_finplot.py   # 保存 PNG
"""

import sys
from pathlib import Path

import finplot as fplt
import pandas as pd

ROOT = Path(r"D:\code\43030\43030")
CSV = ROOT / "data" / "pricehistory-dailyadj.csv"
PNG = ROOT / "report" / "kline.png"


def load():
    df = pd.read_csv(CSV, parse_dates=["Date"], dayfirst=True)
    df = df.sort_values("Date").reset_index(drop=True)
    # 所有 0 值用当日 Close 填充 (Open/High/Low = Close)
    for c in ["Open", "High", "Low"]:
        df.loc[df[c] == 0, c] = df["Close"]
    df = df.set_index("Date")
    return df


def main():
    df = load()
    print(f"rows={len(df)}  range={df.index[0].date()} ~ {df.index[-1].date()}")

    price_ax, volume_ax = fplt.create_plot("PSQ price and volume", rows=2)
    fplt.candlestick_ochl(df[["Open", "Close", "High", "Low"]], ax=price_ax)
    fplt.volume_ocv(df[["Open", "Close", "Volume"]], ax=volume_ax)
    price_ax.setTitle("PSQ OHLC price")
    volume_ax.setTitle("Daily Volume")
    try:
        fplt.win.setWindowTitle(
            "PSQ Pacific Smiles Group - FY2025-26 OHLC and Daily Volume"
        )
    except Exception:
        pass

    if "--show" in sys.argv:
        # 交互窗口: 关闭窗口后退出
        fplt.show(qt_exec=True)
        return

    # --save 模式: 事件循环启动后单次截图并退出
    def grab_and_quit():
        try:
            ok = fplt.screenshot(open(PNG, "wb"))
            print("saved PNG:", PNG) if ok else print("screenshot returned False")
        except Exception as e:
            print("screenshot failed:", type(e).__name__, e)
        fplt.app.quit()

    fplt.timer_callback(grab_and_quit, 0.5, single_shot=True)
    fplt.show(qt_exec=True)


if __name__ == "__main__":
    main()
