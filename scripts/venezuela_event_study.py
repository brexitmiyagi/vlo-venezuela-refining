"""Did the market price Venezuela into Valero? A market-model event study.

Event: Maduro captured Saturday Jan 3 2026, so day 0 is Monday Jan 5.
Estimation window: daily log returns Jan 2 2025 to Dec 19 2025.
Benchmarks: XLE (energy sector), an equal-weight MPC/DINO refiner pair, and SPY.
Windows end Jan 28 so Valero's own Q4 2025 print (Jan 29) stays out. Jan 30 shown for reference.
Placebos: every rolling window of the same length inside the estimation year,
using the same fitted model. The p-value is the share of placebo windows with an
abnormal return at least as large in absolute size.
Closes are dividend-adjusted with Seeking Alpha's adjustment factors (prices.py).
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
from prices import adjusted_closes
px = adjusted_closes()
r = np.log(px).diff().dropna()
r["peer"] = (r["mpc"] + r["dino"]) / 2

est = r.loc["2025-01-02":"2025-12-19"]
day0 = r.index.get_loc(pd.Timestamp("2026-01-05"))
windows = {"Jan 5": "2026-01-05", "Jan 5-9": "2026-01-09",
           "Jan 5-28": "2026-01-28", "Jan 5-30 (incl. print)": "2026-01-30"}

rows = []
for bench in ["xle", "peer", "spy"]:
    b, a = np.polyfit(est[bench], est["vlo"], 1)
    resid_sd = np.std(est["vlo"] - a - b * est[bench], ddof=2)
    ar_all = r["vlo"] - a - b * r[bench]
    ar_est = ar_all.loc[est.index].values
    for label, end in windows.items():
        e = r.index.get_loc(pd.Timestamp(end))
        L = e - day0 + 1
        car = ar_all.iloc[day0:e + 1].sum()
        placebo = np.array([ar_est[k:k + L].sum() for k in range(len(ar_est) - L + 1)])
        p = (np.abs(placebo) >= abs(car)).mean()
        rows.append(dict(benchmark=bench, beta=round(b, 3), window=label, days=L,
                         abnormal_pct=round(car * 100, 2),
                         placebo_sd_pct=round(placebo.std() * 100, 2),
                         t=round(car / (resid_sd * np.sqrt(L)), 2),
                         placebo_p=round(p, 3), n_placebo=len(placebo)))

out = pd.DataFrame(rows)
print(out.to_string(index=False))
os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
out.to_csv(os.path.join(HERE, "..", "results", "venezuela_event_study.csv"), index=False)
