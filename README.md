# vlo-venezuela-refining

This is the data and code behind my Seeking Alpha piece on Valero (VLO), written November 27, 2026. The call is a HOLD, $337.00 base value, $335.63 probability-weighted, against $323.00 on November 25. The piece argues that Valero's biggest new crude supply, Venezuelan barrels, runs on Treasury licences that keep getting rewritten, and that the stock itself is priced almost exactly on the 2028 refining crack.

Everything here runs on public data. If you think a number is wrong, rerun the script and tell me.

## How to run it

You need Python 3 with pandas, numpy and openpyxl. The scripts that touch the model workbook also need LibreOffice to recalculate it; point the RECALC environment variable at a recalc script, or just open the workbook in Excel.

    pip install -r requirements.txt
    python scripts/venezuela_event_study_crack.py

Every script finds its own data, so you can run it from anywhere.

## Which script backs which claim

Valuation and the Street

- run_workbook.py: the base case from the model. $337.00 value, 2027 EPS $44.78, EBITDA $18.75bn.
- street_gap.py: the gap to the Street's 2027 EBITDA, split into the futures lean ($1.10bn, $3.38 a share) and cheap heavy crude ($0.54bn, $1.59). Also the crack the price implies on the multiple ($36.85), the Street's 2028 crack ($34.17) and the $7.13 of value per $1 of 2028 crack that the hedge ratio comes from.
- dcf_implied.py: the DCF ($346.09) and the 2028 crack $323 implies on it ($33.91).
- model_choice.py: why I blend the NY Harbor and Gulf Coast margin models 77/23.
- futures_backtest.py, lean_by_regime.py: realized cracks beat the futures by $0.87, $1.54 and $2.04 at one, two and three months.
- scenarios.py: the 25/50/25 scenarios ($147, $327, $541), the $335.63 weighted value and the 20% chance of finishing under $200.
- options_odds.py: the same odds from December 2027 option prices (20.3% under $200, 55% under $323).
- comps.py: the peer multiples.
- payout_framework.py: Valero's payout on its own framework. 52% gives 2027 EPS of $44.78; holding cash at $9.8bn gives $47.50; running cash down to the $5bn floor gives $49.43.
- houston_restart.py: Houston valued on its own, $5.39 a share at $700m of restart capex.
- q4_model_bias.py: my quarterly model has never come in below consensus in nine clean quarters. Median error +$0.21 a share.

Venezuela and Kuwait

- venezuela_exposure.py: who imports Venezuelan crude and how much of each plant it is (Valero 255,000 b/d; 39% of Port Arthur, 37% of St. Charles).
- heavy_discount_landed.py: landed discounts by grade ($8.36 Venezuela, $5.69 Maya, $11.97 Bow River under WTI in 2026).
- venezuela_controls.py: the regression of heavy discounts on Venezuelan volumes. No detectable effect, wide range.
- venezuela_event_study.py, venezuela_event_study_crack.py, prices.py: the market reaction after January 3, with placebo windows. The second script is the one in the piece.
- kuwait_test.py: EIA's Persian Gulf landed cost against Brent.
- kuwait_quality_adjusted.py: Kuwait's August cargoes against what their gravity and sulfur say they should cost ($8.01 cheap; Saudi $0.75).
- census_all_origins.py, census_crude_by_district.py: the Census customs pulls. These need your own Census API key in data/census_key.txt. The key is free from the Census Bureau. Mine isn't in here.
- valero_heavy_crude_tracker.py: the monthly plant table. Rerun it after each EIA release.
- update_trackers.py, eia_spot.py: download and cache the EIA data.

## Sources

- EIA company-level crude imports: https://www.eia.gov/petroleum/imports/companylevel/
- EIA landed costs by origin: https://www.eia.gov/dnav/pet/pet_pri_land1_k_m.htm
- EIA spot and NYMEX futures prices: https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm and https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm
- EIA refinery capacity report: https://www.eia.gov/petroleum/refinerycapacity/
- US Census Bureau international trade API: https://api.census.gov/data/timeseries/intltrade/imports/hs
- Treasury OFAC Venezuela general licences: https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions
- Valero Q3 2026 earnings release: https://www.sec.gov/Archives/edgar/data/1035002/000162828026066795/a9302026exh9901earningsrel.htm
- Daily prices, dividend factors and consensus: Seeking Alpha.
- CME settlement prices for the futures curve: CME's own settlement pages. I typed the November 25 strip averages into the workbook by hand. CME's terms don't allow redistributing its data, so the raw settlements aren't in here.

## Things to be careful with

- The 2027 and 2028 crack inputs come from one day's settlements, November 25.
- Houston restart capex is an analyst estimate. Valero hasn't disclosed it.
- The Kuwait quality model is rough. Its typical miss is $5.65 a barrel, so the $8.01 is a lead, not proof.
- The event study is one event. The placebo windows tell you how unusual it was, not why.
- EIA's company data dates cargoes by arrival at the refinery. Census dates them by customs entry, so their monthly numbers differ (262,000 against 309,000 b/d from Kuwait in August).
- The licence dates come from the licences themselves and the Federal Register. EIA doesn't show the seller of each cargo, so nothing here splits Valero's barrels by licence.

## Corrections

None so far.
