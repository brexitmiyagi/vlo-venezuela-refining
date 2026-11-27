"""Could Canadian heavy crude replace Venezuelan barrels on the Gulf Coast?

Two public views:
1. EIA company-level imports: Canadian crude delivered to Gulf Coast (PADD 3) refineries, by month.
   This includes pipeline barrels, because EIA records the refinery that took them.
2. Census trade data: Canadian crude entered at Gulf Coast customs districts. Pipeline crude
   enters at the border, so Gulf entries are essentially seaborne cargoes (mostly via the Trans
   Mountain line to the Pacific coast, then by tanker).
"""
import os, glob
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)
R = lambda *f: os.path.join(HERE, "..", "results", *f)

files = [D("eia_company_imports", f) for f in ("impa23d.xlsx", "impa24d.xlsx", "impa25d.xlsx")] + \
        sorted(glob.glob(D("eia_company_imports", "imp_2026_0*.xlsx")))
x = pd.concat([pd.read_excel(f) for f in files])
x = x[x.PROD_NAME.astype(str).str.contains("Crude", case=False)]
x["month"] = pd.to_datetime(x.RPT_PERIOD).dt.to_period("M")
p3 = x[pd.to_numeric(x.PCOMP_PADD, errors="coerce") == 3]
kbd = lambda d: d.groupby("month").QUANTITY.sum() / d.groupby("month").month.first().dt.days_in_month
eia = pd.DataFrame({
    "eia_canada_to_padd3_kbd": kbd(p3[p3.CNTRY_NAME.astype(str).str.upper() == "CANADA"]),
    "eia_venezuela_to_padd3_kbd": kbd(p3[p3.CNTRY_NAME.astype(str).str.upper() == "VENEZUELA"]),
}).fillna(0)

c = pd.read_csv(D("census_crude_imports_by_district.csv"))
gulf = c[(c.CTY_NAME.str.upper() == "CANADA") & c.DIST_NAME.str.contains("HOUSTON|PORT ARTHUR|NEW ORLEANS|MOBILE|LAREDO|CORPUS", case=False)]
g = gulf.groupby("time")[["GEN_QY1_MO", "GEN_VAL_MO", "VES_VAL_MO"]].sum() if "VES_VAL_MO" in gulf else gulf.groupby("time")[["GEN_QY1_MO", "GEN_VAL_MO"]].sum()
g.index = pd.PeriodIndex(g.index, freq="M")
cen = pd.DataFrame({"census_canada_gulf_entries_kbd": g.GEN_QY1_MO / 1000 / g.index.days_in_month})
out = eia.join(cen, how="outer").loc["2023-01":].round(1)
print(out.to_string())
out.to_csv(R("canada_substitute.csv"))
y = out.copy(); y["year"] = y.index.year
print(y.groupby("year").mean(numeric_only=True).round(1).to_string())
