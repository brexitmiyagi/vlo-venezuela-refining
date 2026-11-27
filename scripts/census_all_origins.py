"""US crude imports (HS 2709) for every origin country, monthly, from Census trade data.
Needs data/census_key.txt (one line, never published). Output: data/census_crude_all_origins.csv"""
import os, json, urllib.request, urllib.parse
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
KEY = open(D("census_key.txt")).read().strip()
q = {"get": "CTY_CODE,CTY_NAME,I_COMMODITY,GEN_VAL_MO,GEN_CIF_MO,GEN_QY1_MO", "COMM_LVL": "HS10",
     "I_COMMODITY": "2709*", "time": "from 2025-01", "key": KEY}
url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?" + urllib.parse.urlencode(q, safe="*,")
d = json.loads(urllib.request.urlopen(url, timeout=120).read())
t = pd.DataFrame(d[1:], columns=d[0])
for c in ["GEN_VAL_MO", "GEN_CIF_MO", "GEN_QY1_MO"]:
    t[c] = pd.to_numeric(t[c], errors="coerce")
t = t[t.CTY_CODE.str.fullmatch(r"[1-9]\d{3}")]          # countries only, no regional totals
t.to_csv(D("census_crude_all_origins.csv"), index=False)
print(len(t), "rows;", t.CTY_NAME.nunique(), "countries;", t.time.min(), "to", t.time.max())
