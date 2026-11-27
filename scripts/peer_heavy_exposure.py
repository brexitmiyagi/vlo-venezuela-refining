"""Who gains most per share from a $1 wider heavy-crude discount?

EIA company-level imports, June-August 2026. Heavy = API gravity under 25. Volumes are imports only:
domestic heavy crude isn't in the data, and some Canadian pipeline crude is listed under an
'unknown processor', so Midwest heavy runs are understated. Treat this as imported heavy exposure.
Dollars per share use shares from data/peer_market_2026-11-25.csv and a 23% tax rate.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
TAX = 0.23
OWNER = {   # refiner names in EIA's data -> listed parent
    "VLO": ["VALERO", "PREMCOR"],
    "PBF": ["TOLEDO REFINING", "PAULSBORO REFINING", "DELAWARE CITY REFINING", "CHALMETTE REFINING",
            "MARTINEZ REFINING", "TORRANCE REFINING"],
    "PSX": ["PHILLIPS 66"],
    "MPC": ["MARATHON PETROLEUM", "TESORO", "ST PAUL PARK", "DICKINSON"],
    "DINO": ["HF SINCLAIR", "HOLLYFRONTIER", "HOLLY ", "SINCLAIR"],
}
x = pd.concat([pd.read_excel(D("eia_company_imports", f"imp_2026_0{m}.xlsx")) for m in (6, 7, 8)])
x = x[x.PROD_NAME.astype(str).str.contains("Crude", case=False)].copy()
x["name"] = x.PCOMP_RNAM.fillna("").astype(str).str.upper()
days = 30 + 31 + 31
def parent(n):
    for tk, keys in OWNER.items():
        if any(n.startswith(k) or k in n for k in keys):
            return tk
    return None
x["tk"] = x.name.map(parent)
x = x[x.tk.notna()]
heavy = x[x.APIGRAVITY < 25]
ven = x[x.CNTRY_NAME.astype(str).str.upper() == "VENEZUELA"]
mkt = pd.read_csv(D("peer_market_2026-11-25.csv"), index_col=0)
out = pd.DataFrame({
    "imported_crude_kbd": x.groupby("tk").QUANTITY.sum() / days,
    "imported_heavy_kbd": heavy.groupby("tk").QUANTITY.sum() / days,
    "venezuelan_kbd": ven.groupby("tk").QUANTITY.sum() / days,
}).fillna(0).reindex(list(OWNER))
out["pretax_m_per_1usd"] = out.imported_heavy_kbd * 365 / 1000
out["after_tax_per_share_per_1usd"] = out.pretax_m_per_1usd * (1 - TAX) / mkt.loc[out.index, "shares_m"]
out["pct_of_price_per_1usd"] = out.after_tax_per_share_per_1usd / (mkt.loc[out.index, "mcap_m"] / mkt.loc[out.index, "shares_m"]) * 100
out["venezuelan_replacement_at_maya_per_share"] = out.venezuelan_kbd * 365 / 1000 * (8.36 - 5.69) * (1 - TAX) / mkt.loc[out.index, "shares_m"]
out = out.round(3)
print(out.to_string())
os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
out.to_csv(os.path.join(HERE, "..", "results", "peer_heavy_exposure.csv"))
