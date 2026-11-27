"""Is a $9.50 drop in the NY Harbor 2-1-1 from 2027 to 2028 normal after a peak year?

Annual average NY Harbor 2-1-1 from EIA daily spot prices (conventional gasoline and ULSD at
New York Harbor, WTI Cushing), 2007 onward (ULSD spot starts mid-2006). For every year, the change
one year later. The futures curve on Nov 25 2026 has 2027 at $44.75 and 2028 at $35.25.
"""
import os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda s: pd.read_csv(os.path.join(HERE, "..", "data", "eia_spot", s + ".csv"), index_col=0, parse_dates=True).iloc[:, 0]
g, d, w = L("EER_EPMRU_PF4_Y35NY_DPG"), L("EER_EPD2DXL0_PF4_Y35NY_DPG"), L("RWTC")
c = ((g + d) / 2 * 42 - w).dropna()
a = c.resample("YE").mean().loc["2007":]
a.index = a.index.year
t = pd.DataFrame({"crack": a.round(2)})
t["next_year"] = t.crack.shift(-1)
t["change"] = (t.next_year - t.crack).round(2)
t["pct"] = (t.change / t.crack * 100).round(1)
print(t.to_string())
top = t.crack.quantile(0.75)
hi = t[(t.crack >= top) & t.next_year.notna()]
print("years in the top quarter (>= $%.2f): next-year change mean %+.2f (%+.1f%%), range %+.2f to %+.2f, n=%d"
      % (top, hi.change.mean(), hi.pct.mean(), hi.change.min(), hi.change.max(), len(hi)))
print("all years: next-year change sd $%.2f; curve 2027->2028: -9.50 (-21.2%%)" % t.change.std())
print("2026 year to date: $%.2f" % c.loc["2026"].mean())
t.to_csv(os.path.join(HERE, "..", "results", "crack_cycles.csv"))
