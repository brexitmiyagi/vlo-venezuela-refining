"""Load the daily closes and apply Seeking Alpha's dividend-adjustment factors (close x factor),
so ex-dividend drops don't show up as returns."""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda f: os.path.join(HERE, "..", "data", f)

def adjusted_closes():
    px = pd.read_csv(D("daily_close_vlo_peers_2025-01_2026-02.csv"), parse_dates=["date"], index_col="date")
    f = pd.read_csv(D("div_adj_factors_seekingalpha.csv"), parse_dates=["from_date"])
    for t in px.columns:
        s = f[f.ticker == t].set_index("from_date")["div_adj_factor"]
        fac = s.reindex(px.index.union(s.index)).ffill().reindex(px.index)
        px[t] = px[t] * fac
    return px
