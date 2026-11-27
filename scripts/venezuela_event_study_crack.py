"""Event study with a refining-margin factor.

Same event and placebo design as venezuela_event_study.py, but the market model
adds the daily change in the NY Harbor 3-2-1 crack against WTI (EIA spot prices,
$/bbl) so that oil and margin moves are held constant. Benchmarks:
  A: XLE + crack      B: MPC/DINO pair + crack      C: XLE + pair + crack
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda f: os.path.join(HERE, "..", "data", f)
from prices import adjusted_closes
px = adjusted_closes()
cr = pd.read_csv(D("cracks_daily.csv"), parse_dates=["date"], index_col="date")["c321_wti"]
r = np.log(px).diff()
r["peer"] = (r["mpc"] + r["dino"]) / 2
r["dcrack"] = cr.reindex(px.index).ffill().diff()   # crack change, $/bbl; holidays carried forward
r = r.dropna()

est = r.loc["2025-01-02":"2025-12-19"]
day0 = r.index.get_loc(pd.Timestamp("2026-01-05"))
windows = {"Jan 5": "2026-01-05", "Jan 5-9": "2026-01-09", "Jan 5-28": "2026-01-28"}
models = {"XLE+crack": ["xle", "dcrack"], "pair+crack": ["peer", "dcrack"], "XLE+pair+crack": ["xle", "peer", "dcrack"]}

rows = []
for name, cols in models.items():
    X = np.column_stack([np.ones(len(est))] + [est[c] for c in cols])
    beta, *_ = np.linalg.lstsq(X, est["vlo"], rcond=None)
    fit = X @ beta
    r2 = 1 - ((est["vlo"] - fit) ** 2).sum() / ((est["vlo"] - est["vlo"].mean()) ** 2).sum()
    Xa = np.column_stack([np.ones(len(r))] + [r[c] for c in cols])
    ar = pd.Series(r["vlo"].values - Xa @ beta, index=r.index)
    ar_est = ar.loc[est.index].values
    for label, end in windows.items():
        e = r.index.get_loc(pd.Timestamp(end)); L = e - day0 + 1
        car = ar.iloc[day0:e + 1].sum()
        pl = np.array([ar_est[k:k + L].sum() for k in range(len(ar_est) - L + 1)])
        rows.append(dict(model=name, r2=round(r2, 3), crack_beta_pct_per_usd=round(beta[-1] * 100, 3),
                         window=label, days=L, abnormal_pct=round(car * 100, 2),
                         placebo_p=round((np.abs(pl) >= abs(car)).mean(), 3)))
out = pd.DataFrame(rows)
print(out.to_string(index=False))
print("crack change Jan 2 to Jan 28: %+.2f $/bbl" % (cr.loc["2026-01-28"] - cr.loc["2026-01-02"]))
out.to_csv(os.path.join(HERE, "..", "results", "venezuela_event_study_crack.csv"), index=False)
