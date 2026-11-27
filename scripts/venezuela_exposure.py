# Which US refineries run on Venezuelan crude, and what happens to heavy discounts when the flow stops.
# Volumes: EIA company-level imports, Jan 2023 to Aug 2026 (crude only, by processing refinery).
# Capacity: EIA Refinery Capacity Report 2026 (atmospheric crude distillation, barrels per calendar day).
# Discounts: EIA landed costs by origin/stream minus WTI Cushing spot (heavy_discount_landed.py).
import os,glob,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=lambda *f:os.path.join(HERE,'..','data',*f)
fs=[D('eia_company_imports','impa%sd.xlsx'%y) for y in ('23','24','25')]+sorted(glob.glob(D('eia_company_imports','imp_2026_0*.xlsx')))
x=pd.concat([pd.read_excel(f) for f in fs]); x=x[x.PROD_NAME.str.contains('Crude',case=False,na=False)].copy()
x['m']=pd.to_datetime(x.RPT_PERIOD).dt.to_period('M'); days=lambda s:s.dt.days_in_month
ve=x[x.CNTRY_NAME.str.upper()=='VENEZUELA']
us=(ve.groupby('m').QUANTITY.sum()/ve.groupby('m').m.first().dt.days_in_month).reindex(pd.period_range('2023-01','2026-08',freq='M')).fillna(0)
print('US Venezuelan crude imports, kb/d, by quarter:'); print(us.groupby(us.index.asfreq('Q')).mean().round(0).to_string())
# refinery table, Jun-Aug 2026
win=ve[ve.m>='2026-06']; nd=92
t=win.groupby(['PCOMP_RNAM','PCOMP_SNAM','PCOMP_STAT']).QUANTITY.sum().div(nd).rename('venez_kbd').reset_index()
allc=x[x.m>='2026-06'].groupby(['PCOMP_RNAM','PCOMP_SNAM']).QUANTITY.sum().div(nd).rename('all_imports_kbd').reset_index()
t=t.merge(allc,on=['PCOMP_RNAM','PCOMP_SNAM'],how='left')
cap=pd.read_excel(D('eia_refcap26.xlsx')); cap=cap[(cap.PRODUCT=='TOTAL OPERABLE CAPACITY')&cap.SUPPLY.str.contains('Atmospheric Crude Distillation Capacity \\(barrels per calendar day\\)',regex=True)]
cap=cap.groupby(['COMPANY_NAME','SITE']).QUANTITY.sum().reset_index()
coke=pd.read_excel(D('eia_refcap26.xlsx')); coke=coke[coke.PRODUCT.str.contains('COKING')&coke.SUPPLY.str.contains('Current Year \\(barrels per calendar day\\)',regex=True)].groupby(['COMPANY_NAME','SITE']).QUANTITY.sum().rename('coking_bpcd').reset_index()
def match(row):
    s=cap[cap.SITE.str.upper().str.contains(row.PCOMP_SNAM.split()[0].upper())]
    if len(s)>1: s2=s[s.COMPANY_NAME.str.upper().str.contains(row.PCOMP_RNAM.split()[0].upper())]; s=s2 if len(s2) else s
    return pd.Series(dict(cap_site=(s.COMPANY_NAME.iloc[0]+' / '+s.SITE.iloc[0]) if len(s)==1 else '',cap_kbd=s.QUANTITY.iloc[0]/1000 if len(s)==1 else np.nan))
t=pd.concat([t,t.apply(match,axis=1)],axis=1)
t['venez_share_of_capacity']=t.venez_kbd/t.cap_kbd
t=t.sort_values('venez_kbd',ascending=False)
print(t[t.venez_kbd>=5].round(3).to_string(index=False))
t.round(3).to_csv(D('venezuela_by_refinery_jun-aug2026.csv'),index=False)
by_co=t.assign(co=t.PCOMP_RNAM.str.replace(' REFG.*| REFINING.*| PETROLEUM.*| USA.*| LLC| LP| INC| CO$','',regex=True)).groupby('co').venez_kbd.sum().sort_values(ascending=False)
print('by company (kb/d, Jun-Aug 2026):',by_co.head(10).round(0).to_dict())
# natural experiment: heavy discounts vs Venezuelan volumes
d=pd.read_csv(D('heavy_discount_landed_monthly.csv'),index_col=0,parse_dates=True); d.index=d.index.to_period('M')
z=pd.concat([us.rename('ve_kbd'),d],axis=1).dropna(subset=['mexico_maya_vs_wti','canada_bow_river_heavy_vs_wti'])
for c in ('mexico_maya_vs_wti','canada_bow_river_heavy_vs_wti','all_imports_vs_wti'):
    b=np.polyfit(z.ve_kbd/100,z[c],1); r=np.corrcoef(z.ve_kbd,z[c])[0,1]
    print('%-32s = %+.2f %+.2f per 100 kb/d of US Venezuelan imports (corr %.2f, n %d)'%(c,b[1],b[0],r,len(z)))
lo=z[z.ve_kbd<100]; hi=z[z.ve_kbd>=400]
print('months under 100 kb/d (n=%d): Maya %+.2f, Bow River %+.2f | months over 400 kb/d (n=%d): Maya %+.2f, Bow River %+.2f'%(len(lo),lo.mexico_maya_vs_wti.mean(),lo.canada_bow_river_heavy_vs_wti.mean(),len(hi),hi.mexico_maya_vs_wti.mean(),hi.canada_bow_river_heavy_vs_wti.mean()))
z.round(3).to_csv(D('venezuela_vs_heavy_discounts.csv'))
