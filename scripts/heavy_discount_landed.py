# A monthly heavy-crude discount from EIA's landed-cost series (cost of imported crude delivered to the US,
# by origin and selected stream), set against WTI Cushing spot (EIA, monthly average). Through August 2026.
import os,sys,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); D=lambda *f:os.path.join(HERE,'..','data',*f)
from eia_spot import load
w=load('RWTC').resample('MS').mean()
L=lambda c:pd.read_csv(D('eia_landed',c+'.csv'),index_col=0,parse_dates=True).iloc[:,0]
t=pd.DataFrame({'all_imports':L('I000000008'),'venezuela':L('IVE0000008'),'mexico_maya':L('IMX2810008'),'canada_bow_river_heavy':L('ICA2440008'),'mexico_all':L('IMX0000008')})
d=t.sub(w,axis=0).loc['2023-01':]; d.columns=[c+'_vs_wti' for c in d.columns]
print(d.round(2).tail(14).to_string())
q=d.groupby(d.index.to_period('Q')).mean(); print(q.round(2).loc['2024Q1':].to_string())
y=d.groupby(d.index.year).mean(); print(y.round(2).to_string())
d.round(3).to_csv(D('heavy_discount_landed_monthly.csv'))
