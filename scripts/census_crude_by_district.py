"""US crude imports by customs district from Census trade data (HS 2709, HS10 level).

Gives, per month, origin and district: barrels, customs value (roughly the price at the
foreign port) and CIF value (with freight and insurance). CIF less customs value per barrel
is the freight-and-insurance cost for that route, which nobody publishes for free.
Needs a Census API key in data/census_key.txt (one line). The key is read from the file only.
"""
import os, json, urllib.request, urllib.parse
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
KEY = open(D("census_key.txt")).read().strip()
CTY = {"5130": "Kuwait", "3070": "Venezuela", "5050": "Iraq", "5170": "Saudi Arabia",
       "2010": "Mexico", "1220": "Canada", "3010": "Colombia", "3510": "Brazil", "3120": "Guyana"}
cols = "CTY_CODE,CTY_NAME,DISTRICT,DIST_NAME,I_COMMODITY,GEN_VAL_MO,GEN_CIF_MO,GEN_QY1_MO,UNIT_QY1"
rows = []
for code in CTY:
    q = {"get": cols, "COMM_LVL": "HS10", "I_COMMODITY": "2709*", "CTY_CODE": code,
         "time": "from 2025-01", "key": KEY}
    url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?" + urllib.parse.urlencode(q, safe="*,")
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=60).read())
    except Exception as e:
        print(CTY[code], "no data:", type(e).__name__); continue
    df = pd.DataFrame(data[1:], columns=data[0]); rows.append(df)
t = pd.concat(rows)
for c in ["GEN_VAL_MO", "GEN_CIF_MO", "GEN_QY1_MO"]:
    t[c] = pd.to_numeric(t[c], errors="coerce")
t = t[t.DISTRICT != "-"]
t.to_csv(D("census_crude_imports_by_district.csv"), index=False)
g = t.groupby(["time", "CTY_NAME", "DIST_NAME"])[["GEN_QY1_MO", "GEN_VAL_MO", "GEN_CIF_MO"]].sum()
g = g[g.GEN_QY1_MO > 0]
g["kbd"] = g.GEN_QY1_MO / 1000 / pd.to_datetime(g.index.get_level_values(0)).days_in_month.values
g["fob_per_bbl"] = g.GEN_VAL_MO / g.GEN_QY1_MO
g["cif_per_bbl"] = g.GEN_CIF_MO / g.GEN_QY1_MO
g["freight_ins_per_bbl"] = g.cif_per_bbl - g.fob_per_bbl
g = g.round(2)
os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
g.to_csv(os.path.join(HERE, "..", "results", "census_crude_by_district.csv"))
print("units:", t.UNIT_QY1.unique())
print(g.loc[g.index.get_level_values(1).str.upper().str.contains("KUWAIT")].to_string())
s = g.groupby(level=[0, 1])[["kbd"]].sum().join(
    g.groupby(level=[0, 1]).apply(lambda x: pd.Series({"fob": (x.fob_per_bbl * x.GEN_QY1_MO).sum() / x.GEN_QY1_MO.sum(),
                                                       "freight": (x.freight_ins_per_bbl * x.GEN_QY1_MO).sum() / x.GEN_QY1_MO.sum()}))).round(2)
s.to_csv(os.path.join(HERE, "..", "results", "census_crude_by_origin.csv"))
print(s.loc["2026-01":].to_string())
