"""The product side of the crack: US distillate and gasoline stocks against the five-year range,
and US product exports. All EIA weekly data (Weekly Petroleum Status Report series).
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", "eia_spot", *f)
R = lambda *f: os.path.join(HERE, "..", "results", *f)
L = lambda s: pd.read_csv(D(s + ".csv"), index_col=0, parse_dates=True).v

rows = []
for code, name in [("WDISTUS1", "distillate stocks"), ("WGTSTUS1", "gasoline stocks")]:
    d = L(code); last = d.index[-1]; wk = last.isocalendar().week
    hist = pd.Series({y: d[(d.index.year == y) & (d.index.isocalendar().week == wk)].iloc[0] for y in range(2021, 2026)})
    rows.append(dict(series=name, week=last.date(), mbbl=d.iloc[-1] / 1000, five_yr_avg=hist.mean() / 1000,
                     five_yr_min=hist.min() / 1000, five_yr_max=hist.max() / 1000, vs_avg_pct=(d.iloc[-1] / hist.mean() - 1) * 100))
t = pd.DataFrame(rows).round(1)
print(t.to_string(index=False)); t.to_csv(R("product_stocks.csv"), index=False)

ex = pd.DataFrame({"distillate_exports_kbd": L("WDIEXUS2"), "gasoline_exports_kbd": L("W_EPM0F_EEX_NUS-Z00_MBBLD")})
last = ex.index[-1]
ytd = ex[(ex.index.month < last.month) | ((ex.index.month == last.month) & (ex.index.day <= last.day))]
y = ytd.groupby(ytd.index.year).mean().loc[2021:].round(0)
print(f"\nExports, Jan 1 to {last:%b %d} each year (kb/d):"); print(y.to_string())
y.to_csv(R("product_exports_ytd.csv"))

# Longer view: same week every year since 2000 for distillate stocks, and export year-to-date since 2010
ds = L("WDISTUS1"); wk = ds.index[-1].isocalendar().week
same = ds[ds.index.isocalendar().week == wk]
print(f"\nDistillate stocks in week {wk}: lowest of any year since 1982 is {same.idxmin().year} at {same.min()/1000:.1f}m bbl; "
      f"next lowest {same.drop(same.idxmin()).min()/1000:.1f}m ({same.drop(same.idxmin()).idxmin().year})")
de = L("WDIEXUS2"); de = de[(de.index.month < last.month) | ((de.index.month == last.month) & (de.index.day <= last.day))]
dy = de.groupby(de.index.year).mean()
print(f"Distillate exports year to date: {dy.idxmax()} highest since {dy.index.min()} at {dy.max():.0f} kb/d; previous high {dy.drop(dy.idxmax()).max():.0f} ({dy.drop(dy.idxmax()).idxmax()})")
