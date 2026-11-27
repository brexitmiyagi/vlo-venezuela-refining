# Daily EIA spot prices: Gulf Coast and NY Harbor gasoline and ULSD, WTI and Brent. Saved to data/eia_spot/.
import os, io, urllib.request, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(HERE,'..','data','eia_spot')
SER={'gc_gas':'EER_EPMRU_PF4_RGC_DPG','gc_ulsd':'EER_EPD2DXL0_PF4_RGC_DPG','ny_gas':'EER_EPMRU_PF4_Y35NY_DPG','ny_ulsd':'EER_EPD2DXL0_PF4_Y35NY_DPG','wti':'RWTC','brent':'RBRTE'}
def load(code):
    f=os.path.join(D,code+'.csv')
    if not os.path.exists(f):
        u='https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=%s&f=D'%code
        html=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read().decode('latin1')
        t=[x for x in pd.read_html(io.StringIO(html)) if 'Week Of' in list(x.columns)][0]
        rows=[]
        for _,r in t.dropna(subset=['Week Of']).iterrows():
            yr,rest=str(r['Week Of']).split(' ',1); first=rest.split(' to ')[0].replace(' ','')
            start=pd.to_datetime(yr+'-'+first,format='%Y-%b-%d',errors='coerce')
            if pd.isna(start): continue
            for j,dname in enumerate(['Mon','Tue','Wed','Thu','Fri']):
                if pd.notna(r[dname]): rows.append((start+pd.Timedelta(days=j),float(r[dname])))
        s=pd.Series(dict(rows)).sort_index(); s.to_csv(f)
    return pd.read_csv(f,index_col=0,parse_dates=True).iloc[:,0]
if __name__=='__main__':
    df=pd.DataFrame({k:load(v) for k,v in SER.items()})
    print(df.dropna().tail(3)); print(df.dropna().index.min())
