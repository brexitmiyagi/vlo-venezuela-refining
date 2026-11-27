"""How noisy is the 2028 crack the rating hangs on, and does the hedge ratio hold up?

Inputs are my own calendar-year averages of the NY Harbor 2-1-1 (RBOB and ULSD in $/gal x 42,
averaged, less WTI) from CME's daily settlements, November 19-25, 2026, plus 2028 volume and open
interest totals from the same pages. CME's terms don't allow redistributing raw settlements, so
only these derived numbers are here. VLO closes are from Seeking Alpha.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *f: os.path.join(HERE, "..", "data", *f)

s = pd.read_csv(D("ny211_strip_daily_2026-11.csv"), parse_dates=["date"], index_col="date")
d = s.diff().dropna()
print(s.to_string()); print("\nday-to-day changes:"); print(d.round(2).to_string())
print(f"\n2028 strip: average absolute daily move ${d.ny211_2028.abs().mean():.2f}, largest ${d.ny211_2028.abs().max():.2f}, "
      f"move over the week ${s.ny211_2028.iloc[-1]-s.ny211_2028.iloc[0]:+.2f}")

# Value sensitivities from the model (street_gap.py): $7.13 a share per $1 of 2028, about $2.50 per $1 of 2027
V28, V27 = 7.13, 2.50
dv = V28 * (s.ny211_2028.iloc[-1] - s.ny211_2028.iloc[0]) + V27 * (s.ny211_2027.iloc[-1] - s.ny211_2027.iloc[0])
dp = s.vlo_close.iloc[-1] - s.vlo_close.iloc[0]
print(f"model value change Nov 19-25 from the curve alone: ${dv:+.2f}; stock: ${dp:+.2f} ({dp/dv:.0%} of the model's move)")
# Was the rating stable? Probability-weighted value on Nov 19 = 335.63 - dv; return = (value + 4.80)/price - 1 against 9.35% +/- 5 points
for dt, val in [(s.index[0], 335.63 - dv), (s.index[-1], 335.63)]:
    px = s.vlo_close.loc[dt]; r = (val + 4.80) / px - 1
    print(f"{dt.date()}: value ${val:.2f}, price ${px:.2f}, expected return {r:.1%} -> "
          f"{'HOLD' if 0.0435 <= r <= 0.1435 else ('BUY' if r > 0.1435 else 'SELL')}")

# Liquidity
liq = pd.read_csv(D("cme_2028_liquidity_2026-11-25.csv"))
print("\n" + liq.to_string(index=False))
bbl_per_10k_shares = V28 * 10000             # $ per $1 of 2028 crack = barrels of 2-1-1 exposure across the year
rb_contracts = bbl_per_10k_shares / 2 / 1000   # half the 2-1-1 is gasoline, 1,000 bbl per contract
print(f"\nHedging 10,000 shares: about {bbl_per_10k_shares:,.0f} bbl of 2028 2-1-1, i.e. about {rb_contracts:.0f} RBOB contracts")
rb_oi = liq.set_index("contract").loc["RBOB gasoline 2028", "open_interest_nov25"]
print(f"Shares whose 2028 gasoline leg would equal all open 2028 RBOB interest: {rb_oi/rb_contracts*10000:,.0f}")

# Basis: how far Valero's realized margin strays from what the NY Harbor crack says (model_choice.py)
rmse_all, rmse_hi = 0.56, 0.79          # annual out-of-sample error, $/bbl of margin, all years and high-crack years
bbl, tax, sh = 2.95 * 365, 0.23, 278.884
for lab, e in [("typical year", rmse_all), ("high-crack year", rmse_hi)]:
    print(f"basis the hedge can't cover, {lab}: ${e:.2f}/bbl of margin = ${e*bbl*(1-tax)/sh:.2f} a share of earnings")

# The zone: the published flip points hold the stock at $323
print(f"\nHOLD zone for the 2028 strip with the stock at $323: ${35.25-0.65:.2f} to ${35.25+3.85:.2f}")
