"""Monthly Valero heavy-crude tracker from EIA company-level imports.

Run after EIA's monthly release (update_trackers.py downloads the new file first).
Writes results/valero_heavy_tracker.csv: per month, Valero crude imports by plant and origin
(thousand b/d), plus the US total from Venezuela and Kuwait, so the plant table and the
Venezuela/Kuwait lines in the piece can be refreshed each month.
"""
import os, glob
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
files = sorted(glob.glob(D("eia_company_imports", "imp_2026_*.xlsx")))
frames = []
for f in files:
    x = pd.read_excel(f)
    x = x[x.PROD_NAME.astype(str).str.contains("Crude", case=False)]
    frames.append(x)
x = pd.concat(frames)
x["month"] = pd.to_datetime(x.RPT_PERIOD).dt.to_period("M")
x["kbd"] = x.QUANTITY / x.month.dt.days_in_month
x["origin"] = x.CNTRY_NAME.astype(str).str.title()

us = x[x.origin.isin(["Venezuela", "Kuwait"])].pivot_table(index="month", columns="origin", values="kbd", aggfunc="sum").fillna(0)
us.columns = ["US from " + c for c in us.columns]
v = x[x.R_S_NAME.astype(str).str.upper().str.startswith("VALERO")]
plant = v.pivot_table(index="month", columns=["PCOMP_SNAM", "origin"], values="kbd", aggfunc="sum").fillna(0)
plant.columns = [f"{p} | {o}" for p, o in plant.columns]
tot = v.pivot_table(index="month", columns="origin", values="kbd", aggfunc="sum").fillna(0)
out = pd.concat([us, tot.add_prefix("Valero total | "), plant], axis=1).round(1)
os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
out.to_csv(os.path.join(HERE, "..", "results", "valero_heavy_tracker.csv"))
last = out.index.max()
print("latest month:", last)
print(out.loc[last][out.loc[last] > 0].sort_values(ascending=False).head(25).to_string())
