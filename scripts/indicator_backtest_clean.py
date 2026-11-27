# The indicator backtest without look-ahead. At each print the only crude-side inputs used are the
# PREVIOUS quarter's reported differentials (known before the quarter being predicted) plus the
# within-quarter crack move from EIA spot prices. Coefficients are fit on earlier quarters only.
import os,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=lambda f:os.path.join(HERE,'..','data',f)
z=pd.read_csv(D('margin_indicator_quarterly.csv'),index_col=0)
q=pd.read_csv(D('quarterly_model_inputs.csv'),index_col=0); r=pd.read_csv(D('valero_quarterly_releases.csv')).set_index('quarter')
e=pd.read_csv(D('vlo_quarterly_eps_consensus.csv'),index_col=0)
SH={'2024':322,'2025':309,'2026':290}
for c in ('dated_cost','hou_prem','maya_wti'): z[c+'_lag']=z[c].shift(1)
X=['dated_cost_lag','hou_prem_lag','maya_wti_lag','chg']
def ols(y,M): M=np.c_[np.ones(len(y)),M]; return np.linalg.lstsq(M,y,rcond=None)[0]
rows=[]
for p in [x for x in z.index if x>='2024Q3']:
    past=q.loc[:p].iloc[:-1]; b=np.polyfit(past.gc211,past.margin_bbl,1); co=np.polyval(b,q.loc[p,'gc211'])
    zp=z.loc[:p].iloc[:-1].dropna(subset=X)
    res=zp.margin_bbl-np.polyval(b,zp.gc211); c=ols(res.values,zp[X].values)
    ind=co+c[0]+sum(c[i+1]*z.loc[p,X[i]] for i in range(4))
    days={'1':90,'2':91,'3':92,'4':92}[p[-1]]; k=r.loc[p,'throughput_kbd']*days/1000*0.77/SH[p[:4]]
    rows.append(dict(q=p,n_fit=len(zp),actual=q.loc[p,'margin_bbl'],crack_only=co,indicator=ind,eps_actual=e.loc[p,'actual_eps_adj'],consensus=e.loc[p,'consensus_eps'],k=k))
t=pd.DataFrame(rows).set_index('q')
for m in ('crack_only','indicator'): t[m+'_eps']=t.eps_actual+(t[m]-t.actual)*t.k
print(t.round(2).to_string())
for m in ('crack_only','indicator'):
    print('%-10s margin MAE %.2f, mean error %+.2f, EPS MAE %.2f'%(m,(t[m]-t.actual).abs().mean(),(t[m]-t.actual).mean(),(t[m+'_eps']-t.eps_actual).abs().mean()))
print('consensus EPS MAE %.2f'%(t.consensus-t.eps_actual).abs().mean())
# Q4 2026 with the same no-look-ahead rule: Q3's differentials, Oct-Nov crack move
q3=z.iloc[-1]; zp=z.dropna(subset=X); b=np.polyfit(q.gc211,q.margin_bbl,1); res=zp.margin_bbl-np.polyval(b,zp.gc211); c=ols(res.values,zp[X].values)
m4=np.polyval(b,60.24)+c[0]+c[1]*q3.dated_cost+c[2]*q3.hou_prem+c[3]*q3.maya_wti+c[4]*(49.59-68.48)
SHq=278.884; print('Q4 2026 clean indicator: margin %.2f -> EPS %.2f'%(m4,((m4-4.85)*269.1-700+177)*0.77/SHq))
t.round(3).to_csv(D('indicator_backtest_clean.csv'))
