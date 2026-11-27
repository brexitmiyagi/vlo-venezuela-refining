import os
HERE=os.path.dirname(os.path.abspath(__file__))
# Valero per-share earnings as a function of refining margin per barrel.
BBL=2.95*365          # million barrels a year (2026 nine-month run-rate 2.946 mb/d)
OPEX=4.95             # $/bbl, 2026 nine months: 3,985 / 804.3
DA=2.42               # $/bbl, 2026 nine months: 1,947 / 804.3
CORP=-1000            # $m pre-tax: ethanol + VLO share of renewable diesel - G&A - interest + other
TAX=0.23
SH=278.884            # million shares, 23 Oct 2026 (10-Q cover)
def eps(margin,sh=SH,corp=CORP):
    return ((margin-OPEX-DA)*BBL+corp)*(1-TAX)/sh
def margin_for_eps(e,sh=SH,corp=CORP):
    return (e*sh/(1-TAX)-corp)/BBL+OPEX+DA
def margin_from_crack(c321_wti): return 0.07+0.501*c321_wti   # fit 2016-2025, r2 0.98
def crack_from_margin(m): return (m-0.07)/0.501
if __name__=='__main__':
    print('EPS per $1/bbl margin: %.2f'%(eps(11)-eps(10)))
    for y,e in [(2026,59.78),(2027,49.86),(2028,29.29)]:
        m=margin_for_eps(e); print(y,'consensus EPS %.2f needs margin %.2f, 3-2-1 crack %.1f'%(e,m,crack_from_margin(m)))
    for y,c in [(2027,38.70),(2028,31.66),(2029,29.96)]:
        m=margin_from_crack(c); print(y,'futures crack %.2f -> margin %.2f -> EPS %.2f'%(c,m,eps(m)))
