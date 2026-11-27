# Kuwait in August: test one idea. Hypothesis: Brent-linked crude got expensive in Q2 (Dated Brent ran far over futures),
# so Middle East sour priced off Dubai/Oman landed cheap in the US a cargo-cycle later. Data: EIA landed cost of
# Persian Gulf crude (I040000008) vs EIA Brent spot and WTI spot, monthly.
import os,sys,io,urllib.request,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); D=lambda *f:os.path.join(HERE,'..','data',*f)
from eia_spot import load
f=D('eia_landed','I040000008.csv')
if not os.path.exists(f):
    h=urllib.request.urlopen(urllib.request.Request('https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=I040000008&f=M',headers={'User-Agent':'Mozilla/5.0'})).read().decode('latin1')
    t=[x for x in pd.read_html(io.StringIO(h)) if x.shape[1]==13][0]; t.columns=['Year']+list(range(1,13)); t=t[pd.to_numeric(t.Year,errors='coerce').notna()]
    s=t.melt(id_vars='Year',var_name='m',value_name='v'); s['v']=pd.to_numeric(s.v,errors='coerce'); s=s.dropna()
    s.index=pd.to_datetime(s.Year.astype(int).astype(str)+'-'+s.m.astype(str)+'-01'); s.v.sort_index().to_csv(f)
pg=pd.read_csv(f,index_col=0,parse_dates=True).iloc[:,0]
b=load('RBRTE').resample('MS').mean(); w=load('RWTC').resample('MS').mean()
t=pd.DataFrame({'pg_vs_brent':pg-b,'pg_vs_wti':pg-w,'landed_all_vs_brent':pd.read_csv(D('eia_landed','I000000008.csv'),index_col=0,parse_dates=True).iloc[:,0]-b}).loc['2024-01':'2026-08']
print(t.round(2).to_string()); print('2024-25 average:',t.loc[:'2025-12'].mean().round(2).to_dict())
t.round(3).to_csv(D('kuwait_test.csv'))
