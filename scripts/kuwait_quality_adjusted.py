"""Was Kuwait's August 2026 discount real once crude quality is allowed for?

Prices: Census customs value per barrel at the loading port, by origin and month (census_all_origins.py).
Quality: EIA company-level imports give API gravity and sulfur for every cargo; I volume-weight them by
origin and month. Model, fit on every origin except Kuwait and Canada (Canada is mostly pipeline crude
priced inland), weighted by volume:
    price at loading port = month effect + a x API gravity + b x sulfur
The month effect soaks up the oil price level, so only quality and origin are left. Kuwait's residual
is how far its price sat from what its quality says it should have been in that month.
"""
import os, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)

c = pd.read_csv(D("census_crude_all_origins.csv"))
c = c.groupby(["time", "CTY_NAME"])[["GEN_VAL_MO", "GEN_QY1_MO"]].sum().reset_index()
c = c[c.GEN_QY1_MO > 0]
c["price"] = c.GEN_VAL_MO / c.GEN_QY1_MO
c["kbd"] = c.GEN_QY1_MO / 1000 / pd.to_datetime(c.time).dt.days_in_month
c["origin"] = c.CTY_NAME.str.upper().str.strip()

files = sorted(glob.glob(D("eia_company_imports", "imp_2026_*.xlsx"))) + [D("eia_company_imports", "impa25d.xlsx")]
q = pd.concat([pd.read_excel(f) for f in files])
q = q[q.PROD_NAME.astype(str).str.contains("Crude", case=False) & (q.APIGRAVITY > 0)]
q["time"] = pd.to_datetime(q.RPT_PERIOD).dt.strftime("%Y-%m")
q["origin"] = q.CNTRY_NAME.astype(str).str.upper().str.strip()
q["w_api"] = q.APIGRAVITY * q.QUANTITY; q["w_s"] = q.SULFUR * q.QUANTITY
g = q.groupby(["time", "origin"])[["w_api", "w_s", "QUANTITY"]].sum()
g["api"] = g.w_api / g.QUANTITY; g["sulfur"] = g.w_s / g.QUANTITY
g = g[["api", "sulfur"]].reset_index()

m = c.merge(g, on=["time", "origin"], how="inner")
m = m[m.kbd >= 5]                                   # drop tiny, odd parcels
fit = m[~m.origin.isin(["KUWAIT", "CANADA"])]
months = sorted(m.time.unique())
def X(df):
    fe = pd.get_dummies(df.time).reindex(columns=months, fill_value=0).astype(float)
    return np.column_stack([fe.values, df.api.values, df.sulfur.values])
w = np.sqrt(fit.kbd.values)
beta, *_ = np.linalg.lstsq(X(fit) * w[:, None], fit.price.values * w, rcond=None)
a_api, b_s = beta[-2], beta[-1]
resid_fit = fit.price.values - X(fit) @ beta
print("fit: %d origin-months, %d origins; $%.2f per API degree, $%.2f per 1%% sulfur; residual sd $%.2f"
      % (len(fit), fit.origin.nunique(), a_api, b_s, np.sqrt(np.average(resid_fit**2, weights=fit.kbd))))

k = m[m.origin.isin(["KUWAIT", "SAUDI ARABIA", "IRAQ"])].copy()
k["predicted"] = X(k) @ beta
k["vs_quality"] = k.price - k.predicted
out = k[["time", "origin", "kbd", "api", "sulfur", "price", "predicted", "vs_quality"]].round(2).sort_values(["origin", "time"])
print(out.to_string(index=False))
ku = out[out.origin == "KUWAIT"]
print("Kuwait vs quality: 2025 average %+.2f (n=%d), Aug 2026 %s"
      % (ku[ku.time < "2026"].vs_quality.mean(), (ku.time < "2026").sum(), ku[ku.time == "2026-08"].vs_quality.tolist()))
os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
out.to_csv(os.path.join(HERE, "..", "results", "kuwait_quality_adjusted.csv"), index=False)
