# Does the futures lean depend on the curve shape, and on the horizon?
# EIA monthly averages of NYMEX contracts 1-4 (WTI, RBOB, NY Harbor ULSD), Jan 2016 to the last month EIA published.
# For horizon h (1-3 months), compare the 2-1-1 on contract h+1 in month t with contract 1 in month t+h.
# Standard errors: Newey-West with h lags (the overlap), and a non-overlapping subsample.
import os,sys,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import futures_backtest as fb
codes={}
for k in (1,2,3,4): codes.update({'c%d'%k:'RCLC%d'%k,'g%d'%k:'EER_EPMRR_PE%d_Y35NY_DPG'%k,'h%d'%k:'EER_EPD2F_PE%d_Y35NY_DPG'%k})
df=pd.DataFrame({k:fb.load(v) for k,v in codes.items()}).dropna(); df=df[df.index>='2016-01-01']
cr=lambda k:(df['g%d'%k]*42+df['h%d'%k]*42)/2-df['c%d'%k]
for k in (1,2,3,4): df['k%d'%k]=cr(k)
df['slope']=df.k1-df.k4                       # backwardation measure: front minus 4th contract
def nw(e,L):
    e=e-e.mean(); n=len(e); g0=(e*e).mean(); s=g0
    for l in range(1,L+1): s+=2*(1-l/(L+1))*(e[l:]*e[:-l]).mean()
    return np.sqrt(s/n)
rows=[]
for h in (1,2,3):
    err=(df.k1.shift(-h)-df['k%d'%(h+1)]).rename('err'); d=pd.concat([err,df.slope],axis=1).dropna()
    for lab,mask in [('all',d.slope>-999),('backwardation > $5',d.slope>5),('backwardation $0-5',(d.slope>=0)&(d.slope<=5)),('contango',d.slope<0)]:
        e=d.err[mask].values
        if len(e)<6: continue
        se=nw(e,h); sub=d.err[mask].iloc[::h+1] if h>0 else d.err[mask]
        rows.append(dict(horizon_m=h,regime=lab,n=len(e),mean=e.mean(),t_nw=e.mean()/se,n_nonoverlap=len(sub),mean_nonoverlap=sub.mean(),share_positive=(e>0).mean()))
t=pd.DataFrame(rows); print(t.round(2).to_string(index=False))
d3=pd.concat([(df.k1.shift(-3)-df.k4).rename('err'),df.slope],axis=1).dropna()
b=np.polyfit(d3.slope,d3.err,1); print('3-month lean = %.2f + %.2f x backwardation (front minus 4th contract)'%(b[1],b[0]))
print('backwardation >$5 months by year:',d3[d3.slope>5].groupby(d3[d3.slope>5].index.year).size().to_dict())
t.round(3).to_csv(os.path.join(HERE,'..','data','lean_by_regime.csv'),index=False)
