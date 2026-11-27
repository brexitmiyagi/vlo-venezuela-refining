"""Did Venezuela push Canadian crude out of the Gulf Coast, or did Trans Mountain pull it west?

EIA's company-level imports record, for each cargo, the port where it entered the US and the
refinery that took it. Canadian crude bought by Gulf Coast (PADD 3) refiners either enters at the
northern border and comes south by pipeline (entry port in PADD 2) or arrives at a Gulf port
(entry port in PADD 3, mostly tankers). Trans Mountain's expansion started May 1, 2024.
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
can = x[x.CNTRY_NAME.astype(str).str.upper() == "CANADA"]
ven = x[x.CNTRY_NAME.astype(str).str.upper() == "VENEZUELA"]

periods = [("Jan 2023-Apr 2024, before TMX", "2023-01", "2024-04"),
           ("May-Dec 2024", "2024-05", "2024-12"),
           ("2025", "2025-01", "2025-12"),
           ("Jan-Aug 2026", "2026-01", "2026-08")]

def kbd(df, a, b):
    m = pd.period_range(a, b, freq="M")
    return df[df.month.isin(m)].QUANTITY.sum() / sum(p.days_in_month for p in m)

rows = []
for name, a, b in periods:
    p3 = can[can.PCOMP_PADD == 3]
    rows.append({
        "period": name,
        "canada_to_padd3_refiners": kbd(p3, a, b),
        "of_which_entered_at_northern_border": kbd(p3[p3.PORT_PADD == 2], a, b),
        "of_which_entered_at_gulf_ports": kbd(p3[p3.PORT_PADD == 3], a, b),
        "canada_to_padd2_refiners": kbd(can[can.PCOMP_PADD == 2], a, b),
        "canada_to_padd5_refiners": kbd(can[can.PCOMP_PADD == 5], a, b),
        "canada_to_all_us": kbd(can, a, b),
        "venezuela_to_padd3_refiners": kbd(ven[ven.PCOMP_PADD == 3], a, b),
    })
t = pd.DataFrame(rows).set_index("period").round(0)
print(t.T.to_string())
t.to_csv(R("canada_tmx.csv"))

pipe = t.of_which_entered_at_northern_border
drop_total = pipe.iloc[0] - pipe.iloc[-1]
drop_2026 = pipe.iloc[-2] - pipe.iloc[-1]
print(f"\nPipeline barrels into Gulf refiners fell {drop_total:.0f} kb/d from before TMX to 2026.")
print(f"{pipe.iloc[0]-pipe.iloc[-2]:.0f} of that happened by 2025, when Venezuelan barrels into the Gulf were back to "
      f"their pre-TMX level ({t.venezuela_to_padd3_refiners.iloc[0]:.0f} -> {t.venezuela_to_padd3_refiners.iloc[2]:.0f} kb/d).")
print(f"{drop_2026:.0f} happened in 2026, as Venezuelan barrels rose to {t.venezuela_to_padd3_refiners.iloc[-1]:.0f} kb/d "
      f"and Midwest refiners took {t.canada_to_padd2_refiners.iloc[-1]-t.canada_to_padd2_refiners.iloc[-2]:.0f} kb/d more Canadian crude.")
print(f"Total US imports of Canadian crude: {t.canada_to_all_us.iloc[0]:.0f} -> {t.canada_to_all_us.iloc[-1]:.0f} kb/d.")
aug_ven = kbd(ven[ven.PCOMP_PADD == 3], "2026-08", "2026-08")
print(f"2026 drop as a share of August's {aug_ven:.0f} kb/d of Venezuelan crude into Gulf refiners: {drop_2026/aug_ven:.0%}")
