import os,sys
import pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from model import eps, SH
# margin = 0.81 + 0.445 x NY Harbor 2-1-1 crack (gasoline+ULSD over WTI), fit 2016-2025, r2 0.984
A,B=0.81,0.445
mf=lambda c:A+B*c
cf=lambda m:(m-A)/B
R=0.10;G=0.02
FCF=(2800-2000)/SH                 # D&A run-rate (Q4 guide ~$700m/qtr) above ~$2.0bn capex guide
ND=(9840-10012-989)/SH             # cash less debt and finance leases, 30 Sep 2026
LYB_PRICE=320.5/SH                 # Houston site purchase, closing by end-2026
CORP=[0,-500,-1000]
FUT={2027:(20.27+56.53)/2+(83.58-77.24),2028:(19.83+41.33)/2+(73.89-69.22),2029:(20.32+34.90)/2+(71.06-66.28)}
def lyb_value(lr_margin,r):
    # 165 kb/d light sweet restart by end-2027: margin $2 under system, $6/bbl opex, 23% tax, from 2028
    bbl=0.165*365
    ann=max(0,(lr_margin-2-6))*bbl*(1-0.23)/SH
    return ann*(1+G)/(r-G)/(1+r)**1.1 - LYB_PRICE
def value(path_m=None,lr_m=None,r=R,q4=15.4,lyb=True):
    path_m=path_m or [mf(c) for c in FUT.values()]
    lr_m=path_m[-1] if lr_m is None else lr_m
    t0=0.1;v=q4/(1+r)**t0
    for i,m in enumerate(path_m): v+=(eps(m,corp=CORP[i])+FCF)/(1+r)**(i+1+t0)
    v+=(eps(lr_m)+FCF)*(1+G)/(r-G)/(1+r)**(3+t0)
    return v+ND+(lyb_value(lr_m,r) if lyb else 0)
def implied_lr(price=323.0,r=R):
    lo,hi=5,40
    for _ in range(60):
        m=(lo+hi)/2; lo,hi=(m,hi) if value(lr_m=m,r=r)<price else (lo,m)
    return m
if __name__=='__main__':
    df=pd.read_csv(os.path.join(HERE,'..','data','cracks_daily.csv'),index_col=0,parse_dates=True)
    df['c211']=(df.DGASNYH*42+df.DDFUELNYH*42)/2-df.DCOILWTICO
    y=df.groupby(df.index.year).c211.mean()
    avg1625,avg2225=y.loc[2016:2025].mean(),y.loc[2022:2025].mean()
    path=[mf(c) for c in FUT.values()]
    base=value(); bear=value(lr_m=mf(avg1625)); bull=value(path_m=[m+B*5 for m in path],lr_m=mf(avg2225))
    print('futures 2-1-1:',{k:round(v,2) for k,v in FUT.items()},'margins',[round(m,2) for m in path])
    print('EPS on futures 2027 %.2f 2028 %.2f 2029 %.2f'%tuple(eps(m,corp=CORP[i]) for i,m in enumerate(path)))
    print('2-1-1 avg 2016-25 %.2f 2022-25 %.2f'%(avg1625,avg2225))
    print('base %.2f bear %.2f bull %.2f weighted %.2f'%(base,bear,bull,0.25*bear+0.5*base+0.25*bull))
    print('LYB adds at base: %.2f'%lyb_value(path[-1],R))
    for r in (0.09,0.10,0.11):
        m=implied_lr(r=r); print('r %d%%: $323 needs LR margin %.2f = 2-1-1 %.1f; base %.2f'%(r*100,m,cf(m),value(r=r)))
    print('grid'); 
    for lm in (12,14,16,18,20): print(lm,round(cf(lm),1),[round(value(lr_m=lm,r=r)) for r in (0.09,0.10,0.11)])
    print('consensus 2027 $49.86 needs margin',round((49.85512*SH/0.77)/(2.95*365)+4.95+2.42,2),'2-1-1',round(cf((49.85512*SH/0.77)/(2.95*365)+4.95+2.42),1))
