# vlo-venezuela-refining

This is the data and code behind my Seeking Alpha piece on Valero (VLO), written November 27, 2026. The call is a HOLD, $337.00 base value, $335.63 probability-weighted, against $323.00 on November 25. The piece argues that the stock is priced almost exactly on the 2028 refining crack, and that Venezuelan crude, Valero's biggest new supply, runs on Treasury licences that keep getting rewritten but would cost little to lose.

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
- q4_forecast.py: the Q4 2026 call, $18.23 adjusted EPS, range $17.28 to $19.19, from the Gulf Coast crack quarter to date. Run it with --refresh to pull EIA's latest prices.
- q4_model_bias.py: my quarterly model has never come in below consensus in nine clean quarters. Median error +$0.21 a share.

Venezuela and Kuwait

- venezuela_exposure.py: who imports Venezuelan crude and how much of each plant it is (Valero 255,000 b/d; 39% of Port Arthur, 37% of St. Charles).
- heavy_discount_landed.py: landed discounts by grade ($8.36 Venezuela, $5.69 Maya, $11.97 Bow River under WTI in 2026).
- venezuela_controls.py: the regression of heavy discounts on Venezuelan volumes. No detectable effect on its own, but it leaves out Persian Gulf supply; see sour_drivers.py.
- venezuela_event_study.py, venezuela_event_study_crack.py, prices.py: the market reaction after January 3, with placebo windows. The second script is the one in the piece.
- kuwait_test.py: EIA's Persian Gulf landed cost against Brent.
- kuwait_quality_adjusted.py: Kuwait's August cargoes against what their gravity and sulfur say they should cost ($8.01 cheap; Saudi $0.75).
- product_balance.py: distillate and gasoline stocks against the five-year range, and product exports. Distillate stocks on November 20 were the lowest for that week since 1982.
- strip_noise_and_hedge.py: how much the 2028 strip moved day to day from November 19 to 25 (average $0.54), the one-week check of the hedge ratio (the stock moved 71% of what the model said), 2028 futures liquidity, and the basis a NY Harbor hedge can't cover.
- crack_cycles.py: annual NY Harbor 2-1-1 since 2007 and what happened the year after peaks. After top-quarter years the next-year change averaged -$6.78 (-16%); the curve has 2028 $9.50 (21%) below 2027.
- licence_history.py: compares every version of Treasury's general licences 46, 50 and 52 word by word, using the Federal Register text. My reading of each change is in data/ofac_licence_history.csv: nine of eleven rewrites loosened the terms, none tightened the crude trade.
- peer_heavy_exposure.py: imported heavy crude by refiner and what a $1 wider heavy discount is worth per share (Valero 0.11% of its price, PBF 0.77%).
- canada_substitute.py: Canadian crude reaching Gulf Coast refineries by month, and Canadian entries at Gulf customs districts.
- canada_tmx.py: splits that Canadian crude by where it entered the US. The whole drop since 2024 is pipeline barrels from the northern border (366,000 to 95,000 b/d). 129,000 went by 2025, which is Trans Mountain; 142,000 went in 2026 as Venezuelan crude arrived, and that part could come back.
- sanctions_2019.py: the 2019 natural experiment. Venezuelan imports went from 505,000 b/d in 2018 to nothing by mid-2019, and Valero's Brent less Maya went from $4.76 to an average $5.57. Also the 2025-26 Maya discount against Venezuelan barrels, and the $2.28 a share cost if Maya went back to its 2025 average.
- sour_drivers.py: whether Maya's discount follows Venezuela or the Persian Gulf. On its own, Venezuela shows no clear effect. With Persian Gulf imports added to the controls, each 100,000 b/d of Venezuelan crude widens Maya's discount by about $0.83 (Gulf crude about $0.74), so losing August's 655,000 b/d would narrow it by about $5.42 (95% range $0.44 to $10.39), about $3.74 a share a year for Valero with the direct cost. I missed this in my first test, which left the Gulf out.
- gulf_heavy_supply.py: Venezuelan, Mexican and Canadian pipeline crude into Gulf Coast refineries by year. Mexico fell from 626,000 b/d in 2023 to 246,000 in 2026.
- segments_detail.py: Diamond Green Diesel and ethanol. The margins the model implies ($1.30 and $0.77 a gallon), and what $0.10 a gallon is worth ($0.17 and $0.48 a share).
- census_all_origins.py, census_crude_by_district.py: the Census customs pulls. These need your own Census API key in data/census_key.txt. The key is free from the Census Bureau. Mine isn't in here.
- valero_heavy_crude_tracker.py: the monthly plant table. Rerun it after each EIA release.
- update_trackers.py, eia_spot.py: download and cache the EIA data.

## Sources

- EIA company-level crude imports: https://www.eia.gov/petroleum/imports/companylevel/
- EIA landed costs by origin: https://www.eia.gov/dnav/pet/pet_pri_land1_k_m.htm
- EIA spot and NYMEX futures prices: https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm and https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm
- EIA refinery capacity report: https://www.eia.gov/petroleum/refinerycapacity/
- EIA weekly stocks and exports, and monthly imports from Venezuela and Mexico (series WDISTUS1, WGTSTUS1, WDIEXUS2, W_EPM0F_EEX_NUS-Z00_MBBLD, MCRIMUSVE2, MCRIMUSMX2): spreadsheet downloads at https://www.eia.gov/dnav/pet/hist_xls/
- US Census Bureau international trade API: https://api.census.gov/data/timeseries/intltrade/imports/hs
- Treasury OFAC Venezuela general licences: https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions
- Federal Register API (earlier licence versions): https://www.federalregister.gov/developers/documentation/api/v1
- Valero Q3 2026 earnings release: https://www.sec.gov/Archives/edgar/data/1035002/000162828026066795/a9302026exh9901earningsrel.htm
- Daily prices, dividend factors and consensus: Seeking Alpha.
- CME settlement prices for the futures curve: CME's own settlement pages. I typed the November 25 strip averages into the workbook by hand. CME's terms don't allow redistributing its data, so the raw settlements aren't in here.

## Things to be careful with

- The 2027 and 2028 crack inputs come from one day's settlements, November 25. Most 2028 gasoline months didn't trade that day, so those settlements are CME's marks. data/ny211_strip_daily_2026-11.csv holds my calendar-year averages for five days, not CME's raw settlements.
- The hedge check is one week. It shows the stock moving with the deferred crack, nothing more.
- The Venezuela-plus-Gulf regression explains about a fifth of the monthly moves, and EIA landed costs lag spot prices, which mattered while Brent swung in 2026. US imports from the Gulf stand in for Gulf supply.
- The 2019 comparison isn't clean. Saudi and Canadian production cuts were tightening heavy supply at the same time, and Mexico was sending far more crude to the Gulf than it does now.
- Houston restart capex is an analyst estimate. Valero hasn't disclosed it.
- The Kuwait quality model is rough. Its typical miss is $5.65 a barrel, so the $8.01 is a lead, not proof.
- The event study is one event. The placebo windows tell you how unusual it was, not why.
- EIA's company data dates cargoes by arrival at the refinery. Census dates them by customs entry, so their monthly numbers differ (262,000 against 309,000 b/d from Kuwait in August).
- The licence comparison is my reading of the text. The Federal Register version of 46D leaves out its chemicals annex, so I can't rule out an annex change in 46E.
- The peer table is imports only. Domestic heavy crude and some Canadian pipeline barrels aren't tied to a refiner.
- The licence dates come from the licences themselves and the Federal Register. EIA doesn't show the seller of each cargo, so nothing here splits Valero's barrels by licence.

## Corrections

- November 27, 2026, before publication: an earlier draft said this year's data didn't tie heavy discounts to Venezuela. Once Persian Gulf supply is controlled for, they do (sour_drivers.py).
