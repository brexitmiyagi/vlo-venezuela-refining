"""Valero Q4 2026 adjusted EPS from the Gulf Coast 2-1-1 crack, quarter to date. Rerun on the day of publishing.

Margin model (margin_indicator.py): margin = 0.0525 + 0.5192 x Gulf Coast 2-1-1, residual sd $1.29/bbl.
EPS = ((margin - Q4 cash opex) x Q4 barrels - Q4 D&A + net non-refining) x (1 - tax) / diluted shares,
with Q4 guidance from the Q3 call (2.925m b/d, $4.85/bbl opex, ~$700m D&A) and the non-refining line
calibrated in the workbook. Pass --refresh to download EIA's latest daily spot prices first.
"""
import os, sys, urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", "eia_spot", *f)
SER = {"gas": "EER_EPMRU_PF4_RGC_DPG", "ulsd": "EER_EPD2DXL0_PF4_RGC_DPG", "wti": "RWTC"}

if "--refresh" in sys.argv:
    for code in SER.values():
        raw = urllib.request.urlopen(f"https://www.eia.gov/dnav/pet/hist_xls/{code}d.xls", timeout=60).read()
        tmp = D(code + ".xls"); open(tmp, "wb").write(raw)
        pd.read_excel(tmp, sheet_name="Data 1", skiprows=2, index_col=0).iloc[:, 0].to_csv(D(code + ".csv"))
        os.remove(tmp)

s = pd.DataFrame({k: pd.read_csv(D(v + ".csv"), index_col=0, parse_dates=True).iloc[:, 0] for k, v in SER.items()}).dropna()
s["gc211"] = (s.gas + s.ulsd) / 2 * 42 - s.wti
q = s.loc["2026-10-01":"2026-12-31"]
# Refit the crack model exactly as margin_indicator.py does (31 quarters, 2019Q1-2026Q3)
import numpy as np
qi = pd.read_csv(os.path.join(HERE, "..", "data", "quarterly_model_inputs.csv"), index_col=0)
X = np.c_[np.ones(len(qi)), qi.gc211.values]
(A, B) = np.linalg.lstsq(X, qi.margin_bbl.values, rcond=None)[0]
SD = (qi.margin_bbl.values - X @ np.array([A, B])).std(ddof=2)
BBL, OPEX, DA, NONREF, TAX, SH = 269.1, 4.85, 700, 177, 0.23, 278.884
eps = lambda m: ((m - OPEX) * BBL - DA + NONREF) * (1 - TAX) / SH
gc = q.gc211.mean(); m = A + B * gc
print(f"Gulf Coast 2-1-1, Oct 1 to {q.index[-1]:%b %d}: ${gc:.2f} ({len(q)} days)")
print(f"Q4 margin ${m:.2f}/bbl -> adjusted EPS ${eps(m):.2f}, range ${eps(m - SD):.2f} to ${eps(m + SD):.2f}")
print("Consensus $19.51 (Seeking Alpha, Nov 27). The consensus needs a margin of "
      f"${(19.51 * SH / (1 - TAX) + DA - NONREF) / BBL + OPEX:.2f}")
