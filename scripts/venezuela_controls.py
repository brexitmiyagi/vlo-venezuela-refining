# Do heavy-crude discounts move with Venezuelan supply once other drivers are held fixed?
# Monthly, Jan 2023 - Aug 2026. Dependent: landed cost minus WTI Cushing (EIA) for Mexican Maya and Canadian Bow River heavy.
# Controls: US crude imports from Canada (EIA company-level, kb/d), Brent minus WTI spot (EIA), a 2026 dummy (the war year).
import os,sys,glob,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); D=lambda *f:os.path.join(HERE,'..','data',*f)
from eia_spot import load
fs=[D('eia_company_imports','impa%sd.xlsx'%y) for y in ('23','24','25')]+sorted(glob.glob(D('eia_company_imports','imp_2026_0*.xlsx')))
x=pd.concat([pd.read_excel(f) for f in fs]); x=x[x.PROD_NAME.str.contains('Crude',case=False,na=False)].copy()
x['m']=pd.to_datetime(x.RPT_PERIOD).dt.to_period('M')
idx=pd.period_range('2023-01','2026-08',freq='M'); dm=pd.Series(idx.days_in_month,index=idx)
f=lambda c:(x[x.CNTRY_NAME.str.upper()==c].groupby('m').QUANTITY.sum().reindex(idx).fillna(0)/dm)
ve,ca=f('VENEZUELA'),f('CANADA')
bw=(load('RBRTE')-load('RWTC')).resample('MS').mean(); bw.index=bw.index.to_period('M')
d=pd.read_csv(D('heavy_discount_landed_monthly.csv'),index_col=0,parse_dates=True); d.index=d.index.to_period('M')
z=pd.DataFrame({'ve':ve/100,'ca':ca/1000,'bw':bw.reindex(idx),'war':(idx.year==2026).astype(int)},index=idx).join(d)
print('Venezuelan landed-cost months reported: %d of %d (Jan 2023-Aug 2026)'%(z.venezuela_vs_wti.notna().sum(),len(z)))
print('months with US Venezuelan imports under 100 kb/d: %d'%(z.ve<1).sum())
def ols(y,cols):
    t=z.dropna(subset=[y]+cols); X=np.c_[np.ones(len(t)),t[cols].values]; Y=t[y].values
    b=np.linalg.lstsq(X,Y,rcond=None)[0]; e=Y-X@b; n,k=X.shape
    # Newey-West, 3 lags
    XtXi=np.linalg.inv(X.T@X); S=(X*e[:,None]).T@(X*e[:,None])
    for l in range(1,4):
        w=1-l/4; G=(X[l:]*e[l:,None]).T@(X[:-l]*e[:-l,None]); S+=w*(G+G.T)
    se=np.sqrt(np.diag(XtXi@S@XtXi)); r2=1-e.var()/Y.var()
    return dict(zip(['const']+cols,zip(b,se))),n,r2
for y in ('mexico_maya_vs_wti','canada_bow_river_heavy_vs_wti'):
    for cols in (['ve'],['ve','ca','bw','war']):
        res,n,r2=ols(y,cols)
        print('%-30s n=%d r2=%.2f | '%(y,n,r2)+' | '.join('%s %+.2f (se %.2f)'%(k,b,s) for k,(b,s) in res.items()))
z.round(3).to_csv(D('venezuela_controls_monthly.csv'))
