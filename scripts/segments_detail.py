"""Diamond Green Diesel and ethanol: what the model assumes, and what a margin move is worth.

Q3 2026 release: Renewable Diesel (DGD, 100%) operating income $353m on 3.4m gal/day;
Ethanol operating income $272m on 4.8m gal/day. Margins per gallon and volumes by quarter
come from Valero's releases (data/valero_segments_quarterly.csv).
Cost per gallon (opex plus D&A) is backed out of Q3: margin x volume less operating income.
"""
import os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
s = pd.read_csv(os.path.join(HERE, "..", "data", "valero_segments_quarterly.csv")).set_index("quarter").sort_index()
SH, TAX, DAYS = 278.884, 0.23, 92
q3 = s.loc["2026Q3"]
rd_cost = (q3.rd_margin_gal * q3.rd_vol_kgd * 1e3 * DAYS - 353e6) / (q3.rd_vol_kgd * 1e3 * DAYS)
eth_cost = (q3.eth_margin_gal * q3.eth_vol_kgd * 1e3 * DAYS - 272e6) / (q3.eth_vol_kgd * 1e3 * DAYS)
rd_gal_yr, eth_gal_yr = q3.rd_vol_kgd * 1e3 * 365, q3.eth_vol_kgd * 1e3 * 365
model_rd, model_eth = 1000e6, 620e6           # 2027E operating income in the workbook (DGD at 100%)
print("costs per gallon backed out of Q3 2026: DGD $%.2f, ethanol $%.2f" % (rd_cost, eth_cost))
print("margin the 2027 model implies: DGD $%.2f/gal (Q3 $%.2f), ethanol $%.2f/gal (Q3 $%.2f)"
      % (model_rd / rd_gal_yr + rd_cost, q3.rd_margin_gal, model_eth / eth_gal_yr + eth_cost, q3.eth_margin_gal))
print("Q3 2026 annualised operating income: DGD $%.0fm, ethanol $%.0fm" % (353 * 365 / DAYS, 272 * 365 / DAYS))
print("each $0.10/gal: DGD $%.0fm a year at 100%% (Valero's half after tax $%.2f a share); ethanol $%.0fm ($%.2f a share)"
      % (rd_gal_yr * 0.1 / 1e6, rd_gal_yr * 0.1 * 0.5 * (1 - TAX) / 1e6 / SH, eth_gal_yr * 0.1 / 1e6, eth_gal_yr * 0.1 * (1 - TAX) / 1e6 / SH))
h = s.loc["2023Q1":"2026Q3"]
print("margins 2023Q1-2026Q3: DGD avg $%.2f (range %.2f-%.2f), ethanol avg $%.2f (range %.2f-%.2f)"
      % (h.rd_margin_gal.mean(), h.rd_margin_gal.min(), h.rd_margin_gal.max(), h.eth_margin_gal.mean(), h.eth_margin_gal.min(), h.eth_margin_gal.max()))
