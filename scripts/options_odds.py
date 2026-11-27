# Market-implied odds for VLO from listed options (Nasdaq option chain, quotes at the 25 Nov 2026 close).
# r = 1-year Treasury 4.56% (25 Nov 2026); dividends $1.20 a quarter. Implied vols from OTM mid quotes,
# smoothed with a quadratic in log-moneyness; probabilities from the slope of the smoothed call curve.
import os,numpy as np,pandas as pd
from math import log,sqrt,exp
from statistics import NormalDist
HERE=os.path.dirname(os.path.abspath(__file__)); o=pd.read_csv(os.path.join(HERE,'..','data','vlo_options_2026-11-25.csv'),parse_dates=['exp'])
S,r=323.0,0.0456; N=NormalDist(); t0=pd.Timestamp('2026-11-25')
divs=[pd.Timestamp(d) for d in ['2027-02-15','2027-05-15','2027-08-15','2027-11-15']]
def call(F,K,DF,v,T):
    d1=(log(F/K)+0.5*v*v*T)/(v*sqrt(T)); d2=d1-v*sqrt(T); return DF*(F*N.cdf(d1)-K*N.cdf(d2))
res={}
for exp_,g in o.groupby('exp'):
    T=(exp_-t0).days/365.25; DF=exp(-r*T)
    pv=sum(1.20*exp(-r*(d-t0).days/365.25) for d in divs if d<exp_); F=(S-pv)/DF
    g=g.copy(); g['c']=(g.c_bid+g.c_ask)/2; g['p']=(g.p_bid+g.p_ask)/2
    ivs=[]
    for _,x in g.iterrows():
        K=x.strike; px=x.p if K<F else x.c
        tgt=(px+DF*(F-K)) if K<F else px   # convert put to call by parity
        lo,hi=0.05,2.0
        for _ in range(80):
            mid=(lo+hi)/2; lo,hi=(mid,hi) if call(F,K,DF,mid,T)<tgt else (lo,mid)
        ivs.append(mid)
    g['iv']=ivs; k=np.log(g.strike/F); w=(g.strike>=180)&(g.strike<=450)
    coef=np.polyfit(k[w],g.iv[w],2); smile=lambda K:np.polyval(coef,log(K/F))
    def pbelow(K,h=1.0): return 1+(call(F,K+h,DF,smile(K+h),T)-call(F,K-h,DF,smile(K-h),T))/(2*h)/DF
    atm=smile(F)
    res[str(exp_.date())]={K:pbelow(K) for K in (200,250,266,280,291,299,323,332,361,400)}
    print('%s T=%.2fy forward $%.2f, ATM implied vol %.1f%% (90%% strike %.1f%%, 120%% strike %.1f%%)'%(exp_.date(),T,F,atm*100,smile(0.9*F)*100,smile(1.2*F)*100))
    for K,pv_ in res[str(exp_.date())].items(): print('   P(VLO < $%d) = %.0f%%'%(K,100*pv_))
pd.DataFrame(res).round(3).to_csv(os.path.join(HERE,'..','data','options_implied_odds.csv'))
