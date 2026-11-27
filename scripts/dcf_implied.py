# What crack does $323 imply on a DCF instead of the fitted multiple?
# DCF from valuation_211.py (NY model EPS, maintenance FCF, 2% terminal growth) at the 9.35% cost of equity,
# with Houston replaced by its standalone value ($5.39 at $700m analyst restart capex, scripts/houston_restart.py). One uniform shift to the curve.
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valuation_211 as V
r=0.0935; adj=lambda path,lr: V.value(path_m=path,lr_m=lr,r=r,q4=18.23,lyb=False)+5.39
p0=[V.mf(c) for c in V.FUT.values()]; print('DCF at 9.35%% on the curve: $%.2f'%adj(p0,p0[-1]))
lo,hi=-20,20
for _ in range(60):
    s=(lo+hi)/2; p=[V.mf(c+s) for c in V.FUT.values()]; lo,hi=(s,hi) if adj(p,p[-1])<323 else (lo,s)
print('$323 implies the whole curve %+.2f -> 2028 NY 2-1-1 %.2f (curve 35.25)'%(s,35.25+s))
