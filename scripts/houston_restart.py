# Houston restart valued on its own. Disclosed (8-K, 30 Oct 2026): $320.5m price, 165,000 b/d of light sweet
# capacity restarted by year-end 2027, ">25% after-tax IRR using forward mid-cycle pricing, assuming minimal
# commercial synergies". Not disclosed: restart capex, operating cost, margin. Those are my assumptions, stated below.
import numpy as np
W=0.77; mf=lambda c:W*(-0.965+0.4965*c)+(1-W)*(0.0525+0.5192*(c-2.15))
BBL=0.165*365            # m bbl a year at full rates
DISC=2.0                 # $/bbl margin discount vs Valero's system (light sweet, no coker) - assumption
OPEX=6.0                 # $/bbl cash opex - assumption
SUST=1.0                 # $/bbl sustaining capex - assumption
T=0.23; SH=270.97; COE=0.0935; LIFE=20
def flows(capex,m28,mlr,start=2028,ramp=1.0):
    cf={2026:-320.5,2027:-capex}
    for y in range(start,start+LIFE):
        m=m28 if y==2028 else mlr
        cf[y]=cf.get(y,0)+((m-DISC-OPEX)*BBL*(1-T)-SUST*BBL)*(ramp if y==start else 1)
    return cf
def irr(cf):
    ys=sorted(cf); lo,hi=-0.9,3.0
    for _ in range(200):
        r=(lo+hi)/2; npv=sum(cf[y]/(1+r)**(y-2026) for y in ys); lo,hi=(r,hi) if npv>0 else (lo,r)
    return r
def npv_ps(cf,r=COE): return sum(v/(1+r)**(y-2026.9) for y,v in cf.items())/SH   # discounted to late Nov 2026
m28,m29=mf(35.25),mf(32.39)
print('Margins on the curve (blend): 2028 %.2f, 2029 on %.2f; Houston margin = system less $%.0f'%(m28,m29,DISC))
for mid,lab in [(m29,'2029 curve held flat'),(mf(36.49),'2023 crack held flat'),(15.57-0.0,'2022-25 Valero average margin')]:
    lo,hi=0,20000
    for _ in range(100):
        c=(lo+hi)/2; lo,hi=(c,hi) if irr(flows(c,m28,mid))>0.25 else (lo,c)
    print('  mid-cycle = %-30s margin %.2f: 25%% IRR allows restart capex up to $%.0fm; NPV at 9.35%% with that capex $%.2f/share; with $500m $%.2f; $1bn $%.2f'%(lab,mid,c,npv_ps(flows(c,m28,mid)),npv_ps(flows(500,m28,mid)),npv_ps(flows(1000,m28,mid))))
base=flows(500,m28,m29); print('base case (capex $500m, 2029 curve): IRR %.0f%%, NPV $%.2f/share'%(irr(base)*100,npv_ps(base)))
d6=flows(500,m28,m29,start=2028,ramp=0.5); print('six-month delay (half of 2028 lost): NPV $%.2f/share'%npv_ps(d6))
d12={**{2026:-320.5,2027:-500},**{y:v for y,v in flows(500,m28,m29,start=2029).items() if y>=2029}}; print('one-year delay: NPV $%.2f/share'%npv_ps(d12))
print('each $1/bbl of Houston margin: $%.0fm a year after tax, NPV $%.2f/share'%(BBL*(1-T),sum(BBL*(1-T)/(1+COE)**(y-2026.9) for y in range(2028,2048))/SH))

# Analyst restart-cost estimates (Reuters, Nov 19 2026): TD Cowen up to $700m; Turner, Mason $600m-$700m,
# full capacity possibly not until mid-2028. Valero has not disclosed restart capex.
for c in (600,700):
    f=flows(c,m28,m29); print('analyst capex $%dm: IRR %.0f%%, NPV $%.2f/share'%(c,irr(f)*100,npv_ps(f)))
f=flows(700,m28,m29,start=2028,ramp=0.5); print('analyst $700m and half of 2028 lost (mid-2028 full rates): NPV $%.2f/share'%npv_ps(f))
