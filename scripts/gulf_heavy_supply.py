"""Where Gulf Coast refiners' foreign heavy-ish crude comes from, 2023-2026: Venezuela, Mexico and
Canadian pipeline barrels (entered at the northern border), from EIA company-level imports."""
import os, glob
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
R = lambda *f: os.path.join(HERE, "..", "results", *f)
files = [D("eia_company_imports", f) for f in ("impa23d.xlsx", "impa24d.xlsx", "impa25d.xlsx")] + \
        sorted(glob.glob(D("eia_company_imports", "imp_2026_0*.xlsx")))
x = pd.concat([pd.read_excel(f) for f in files])
x = x[x.PROD_NAME.astype(str).str.contains("Crude", case=False) & (x.PCOMP_PADD == 3)]
x["month"] = pd.to_datetime(x.RPT_PERIOD).dt.to_period("M")
c = x.CNTRY_NAME.astype(str).str.upper()
sel = {"Venezuela": c == "VENEZUELA", "Mexico": c == "MEXICO", "Canada by pipeline": (c == "CANADA") & (x.PORT_PADD == 2)}
out = {}
for k, m in sel.items():
    g = x[m].groupby("month").QUANTITY.sum()
    g = g.reindex(pd.period_range("2023-01", "2026-08", freq="M"), fill_value=0)
    out[k] = (g.groupby(g.index.year).sum() / g.groupby(g.index.year).apply(lambda s: sum(p.days_in_month for p in s.index))).round(0)
t = pd.DataFrame(out); t.index = [str(i) if i < 2026 else "2026 (Jan-Aug)" for i in t.index]
t["total"] = t.sum(axis=1)
print(t.to_string()); t.to_csv(R("gulf_heavy_supply.csv"))
