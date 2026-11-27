"""The 2019 natural experiment: what did heavy-sour discounts do when Venezuelan crude left the US?

US sanctions on PDVSA in late January 2019 took Venezuelan crude out of US refineries within a few
months, the mirror image of 2026. Discounts are Valero's own quarterly "Brent less Maya" from its
earnings releases (spot-based), with EIA's monthly landed cost of Maya less Brent as a cross-check.
I use Brent, not WTI, because the Brent-WTI spread was unusually wide and volatile in 2018-19.
"""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
D = lambda *f: os.path.join(HERE, "..", "data", *f)
R = lambda *f: os.path.join(HERE, "..", "results", *f)
from eia_spot import load

ven = pd.read_csv(D("eia_spot", "MCRIMUSVE2.csv"), index_col=0, parse_dates=True).v
# EIA stops listing the series once imports hit zero, so fill the missing months through 2022 with 0
ven = ven.reindex(pd.date_range("1973-01-15", "2022-12-15", freq="MS") + pd.Timedelta(days=14)).fillna(ven).fillna(0)
mex = pd.read_csv(D("eia_spot", "MCRIMUSMX2.csv"), index_col=0, parse_dates=True).v
print("US imports from Venezuela, kb/d:")
print(ven.loc["2018-01":"2019-08"].to_string())
print(f"2018 average {ven.loc['2018'].mean():.0f} kb/d")

rel = pd.read_csv(D("valero_quarterly_releases.csv"))
rel = rel.set_index("quarter").sort_index()
q = rel.loc["2018Q4":"2020Q1", ["brent_less_maya", "brent_less_wti"]]
q["ven_imports_kbd"] = [ven[(ven.index.to_period("Q") == pd.Period(p))].mean() for p in q.index]
print("\nValero's reported Brent less Maya ($/bbl) against US imports from Venezuela:")
print(q.round(2).to_string())

b = load("RBRTE").resample("MS").mean()
maya = pd.read_csv(D("eia_landed", "IMX2810008.csv"), index_col=0, parse_dates=True).iloc[:, 0]
m = (b - maya).rename("brent_less_maya_landed").loc["2018-01":"2019-12"]
before, after = m.loc["2018-11":"2019-01"].mean(), m.loc["2019-03":"2019-08"].mean()
print(f"\nEIA landed Maya, Brent less Maya: Nov 2018-Jan 2019 {before:.2f}, Mar-Aug 2019 {after:.2f}")
v_before = q.loc["2018Q4", "brent_less_maya"]; v_after = q.loc[["2019Q1", "2019Q2", "2019Q3"], "brent_less_maya"].mean()
print(f"Valero's series: Q4 2018 {v_before:.2f}, Q1-Q3 2019 average {v_after:.2f} (change {v_after - v_before:+.2f})")

# 2026: did Maya widen as Venezuelan barrels arrived?
qi = pd.read_csv(D("quarterly_model_inputs.csv")).set_index("qp")
ca = pd.read_csv(R("canada_substitute.csv"), index_col=0)
ca.index = pd.PeriodIndex(ca.index, freq="M")
vq = ca.eia_venezuela_to_padd3_kbd.groupby(ca.index.asfreq("Q")).mean()
w = pd.DataFrame({"maya_less_wti": qi.maya_wti.loc["2025Q1":"2026Q3"].values},
                 index=pd.PeriodIndex(qi.loc["2025Q1":"2026Q3"].index, freq="Q"))
w["venezuela_to_gulf_refiners_kbd"] = vq.reindex(w.index)
print("\n2025-26, Maya discount to WTI against Venezuelan barrels into Gulf refiners:")
print(w.round(2).to_string())

print("\nUS imports from Mexico, kb/d, annual average:")
print(mex.groupby(mex.index.year).mean().loc[2018:].round(0).to_string())

# What losing Venezuela would cost if Maya also went back to its 2025 average
from_street = 0.178 * (8.00 - 5.17) * 2.95 * 365 * 0.77 / 262.2   # same arithmetic as street_gap.py: after tax, 2027 average shares
print(f"\nIf Q3's $8.00 Maya discount went back to 2025's $5.17: ${from_street:.2f} a share a year after tax")
print(f"Plus the direct cost of replacing Venezuelan barrels ($0.69): ${from_street + 0.69:.2f}")
q.round(2).to_csv(R("sanctions_2019.csv"))
w.round(2).to_csv(R("maya_vs_venezuela_2025_26.csv"))
