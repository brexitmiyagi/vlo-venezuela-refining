# Monthly/weekly refresh of the public data behind the Venezuela tracker and the margin indicator.
# EIA only (public, no key): company-level imports (monthly, ~2-month lag, next release on EIA's page),
# landed costs by origin (monthly), daily spot prices, weekly PADD 3 utilization.
# CME settlement data is NOT pulled here: CME's Data Terms of Use prohibit scripted access to its website.
import os,io,urllib.request,datetime,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=lambda *f:os.path.join(HERE,'..','data',*f)
UA={'User-Agent':'Mozilla/5.0'}; get=lambda u:urllib.request.urlopen(urllib.request.Request(u,headers=UA)).read()
B='https://www.eia.gov/petroleum/imports/companylevel'
def company_imports():
    today=datetime.date.today()
    for k in range(1,5):
        y,m=divmod(today.year*12+today.month-1-k,12); m+=1
        f=D('eia_company_imports','imp_%d_%02d.xlsx'%(y,m))
        if os.path.exists(f): continue
        try:
            b=get('%s/archive/%d/%d_%02d/data/import.xlsx'%(B,y,y,m)); open(f,'wb').write(b); print('saved',f)
        except Exception as e: print('not yet published:',y,m)
def landed():
    import re
    for c in ['I000000008','IVE0000008','IMX0000008','ICA0000008','IMX2810008','ICA2440008']:
        h=get('https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=%s&f=M'%c).decode('latin1')
        t=[x for x in pd.read_html(io.StringIO(h)) if x.shape[1]==13][0]; t.columns=['Year']+list(range(1,13)); t=t[pd.to_numeric(t.Year,errors='coerce').notna()]
        s=t.melt(id_vars='Year',var_name='m',value_name='v'); s['v']=pd.to_numeric(s.v,errors='coerce'); s=s.dropna()
        s.index=pd.to_datetime(s.Year.astype(int).astype(str)+'-'+s.m.astype(str)+'-01'); s.v.sort_index().to_csv(D('eia_landed',c+'.csv'))
    print('landed costs refreshed')
if __name__=='__main__':
    company_imports(); landed()
    import subprocess,sys
    for s in ('heavy_discount_landed.py','venezuela_exposure.py','valero_refinery_model.py'):
        subprocess.run([sys.executable,os.path.join(HERE,s)])
