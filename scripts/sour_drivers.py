"""Is Valero's sour-crude edge following Venezuela or the Persian Gulf?

Monthly, 2023 to August 2026: US crude imports from Venezuela and from Persian Gulf countries
(EIA company-level data, all US refiners), against the landed cost of Maya less Brent (EIA).
Quarterly: Valero's own reported discounts to Brent for Maya, the Argus Sour Crude Index (a
US Gulf of Mexico medium sour basket) and WCS at Houston, from its earnings releases.
"""
import os, sys, glob
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
D = lambda *f: os.path.join(HERE, "..", "data", *f)
R = lambda *f: os.path.join(HERE, "..", "results", *f)
from eia_spot import load

files = [D("eia_company_imports", f) for f in ("impa23d.xlsx", "impa24d.xlsx", "impa25d.xlsx")] + \
        sorted(glob.glob(D("eia_company_imports", "imp_2026_0*.xlsx")))
x = pd.concat([pd.read_excel(f) for f in files])
x = x[x.PROD_NAME.astype(str).str.contains("Crude", case=False)]
x["month"] = pd.to_datetime(x.RPT_PERIOD).dt.to_period("M")
c = x.CNTRY_NAME.astype(str).str.upper()
PG = ["SAUDI ARABIA", "IRAQ", "KUWAIT", "UNITED ARAB EMIRATES", "QATAR", "BAHRAIN", "IRAN"]
months = pd.period_range("2023-01", "2026-08", freq="M")
kbd = lambda m: (x[m].groupby("month").QUANTITY.sum().reindex(months, fill_value=0) / months.days_in_month).round(0)
t = pd.DataFrame({"venezuela_kbd": kbd(c == "VENEZUELA"), "persian_gulf_kbd": kbd(c.isin(PG))})

b = load("RBRTE").resample("MS").mean(); b.index = b.index.to_period("M")
maya = pd.read_csv(D("eia_landed", "IMX2810008.csv"), index_col=0, parse_dates=True).iloc[:, 0]; maya.index = maya.index.to_period("M")
t["brent_less_maya_landed"] = (b - maya).reindex(months).round(2)
t.to_csv(R("sour_drivers_monthly.csv"))
print(t.loc["2025-10":].to_string())

# Regression on monthly changes, 2023-2026
d = t.dropna()
X = np.c_[np.ones(len(d)), d.venezuela_kbd / 100, d.persian_gulf_kbd / 100]
y = d.brent_less_maya_landed.values
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
res = y - X @ beta; n, k = X.shape
se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * (res @ res) / (n - k))
print(f"\nBrent less Maya (landed) on imports, per 100 kb/d, {n} months:")
for name, bb, s in zip(["const", "Venezuela", "Persian Gulf"], beta, se):
    print(f"  {name:12s} {bb:+.2f}  (se {s:.2f}, t {bb/s:+.1f})")
print(f"  R2 {1 - res.var()/y.var():.2f}")

rel = pd.read_csv(D("valero_quarterly_releases.csv")).set_index("quarter").sort_index()
q = rel.loc["2025Q1":"2026Q3", ["brent_less_maya", "brent_less_asci", "brent_less_wcs_houston"]]
qq = t.groupby(t.index.asfreq("Q"))[["venezuela_kbd", "persian_gulf_kbd"]].mean().round(0)
qq.index = qq.index.astype(str)
q = q.join(qq)
print("\nValero's reported discounts to Brent ($/bbl) and US imports (kb/d), by quarter:")
print(q.to_string()); q.to_csv(R("sour_drivers_quarterly.csv"))

# Same test as venezuela_controls.py (Maya landed less WTI, with Canada, Brent-WTI and a 2026 dummy,
# Newey-West errors), adding Persian Gulf imports. Discount is negative, so a wider discount is a more negative number.
z = pd.read_csv(D("venezuela_controls_monthly.csv"), index_col=0)
z.index = pd.PeriodIndex(z.index, freq="M")
z["pg"] = t.persian_gulf_kbd / 100
def nw(yname, cols):
    u = z.dropna(subset=[yname] + cols); X = np.c_[np.ones(len(u)), u[cols].values]; Y = u[yname].values
    bb = np.linalg.lstsq(X, Y, rcond=None)[0]; e = Y - X @ bb
    XtXi = np.linalg.inv(X.T @ X); S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, 4):
        w = 1 - l / 4; G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None]); S += w * (G + G.T)
    return bb, np.sqrt(np.diag(XtXi @ S @ XtXi)), len(u), 1 - e.var() / Y.var()
for cols in (["ve", "pg"], ["ve", "pg", "ca", "bw", "war"]):
    bb, se, n, r2 = nw("mexico_maya_vs_wti", cols)
    print(f"\nMaya less WTI, n={n}, R2 {r2:.2f}: " + " | ".join(f"{k} {v:+.2f} (se {s:.2f})" for k, v, s in zip(["const"] + cols, bb, se)))

# What the controlled regression implies for losing Venezuela (the numbers quoted in the article)
bb, se, n, r2 = nw("mexico_maya_vs_wti", ["ve", "pg", "ca", "bw", "war"])
ven_aug = t.loc["2026-08", "venezuela_kbd"]
narrow = -bb[1] * ven_aug / 100          # discount is negative, so a negative coefficient means wider with more barrels
lo, hi = -(bb[1] + 1.96 * se[1]) * ven_aug / 100, -(bb[1] - 1.96 * se[1]) * ven_aug / 100
# Same arithmetic as street_gap.py: heavy-sour share 0.178 of 2.95m b/d, 23% tax, 262.2m average 2027 shares
per_dollar = 0.178 * 2.95 * 365 * 0.77 / 262.2
print(f"\nUS imports of Venezuelan crude, August 2026: {ven_aug:.0f} kb/d")
print(f"Implied narrowing of Maya's discount if they stop: ${narrow:.2f}/bbl (95% range ${lo:.2f} to ${hi:.2f})")
print(f"Cost to Valero: ${narrow*per_dollar:.2f} a share a year, plus the $0.69 direct cost = ${narrow*per_dollar+0.69:.2f}")
print(f"Gulf imports, Feb {t.loc['2026-02','persian_gulf_kbd']:.0f} -> Jun {t.loc['2026-06','persian_gulf_kbd']:.0f} kb/d; "
      f"Venezuela over the same months {t.loc['2026-02','venezuela_kbd']:.0f} -> {t.loc['2026-06','venezuela_kbd']:.0f}")
