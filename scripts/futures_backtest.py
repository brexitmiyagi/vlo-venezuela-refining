# Does the NYMEX 2-1-1 futures crack forecast what that same contract settles at when it becomes front month?
# EIA publishes monthly averages of contracts 1-4 for WTI, RBOB and NY Harbor ULSD (heating oil) up to April 2024.
# Test: 2-1-1 on contract 4 in month t vs 2-1-1 on contract 1 in month t+3 (the same delivery month).
import os, io, urllib.request, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(HERE,'..','data','eia_futures')
SER={'c1':'RCLC1','c4':'RCLC4','g1':'EER_EPMRR_PE1_Y35NY_DPG','g4':'EER_EPMRR_PE4_Y35NY_DPG','h1':'EER_EPD2F_PE1_Y35NY_DPG','h4':'EER_EPD2F_PE4_Y35NY_DPG'}
def load(code):
    f=os.path.join(D,code+'.csv')
    if not os.path.exists(f):
        url='https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=%s&f=M'%code
        html=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})).read().decode('latin1')
        t=[x for x in pd.read_html(io.StringIO(html)) if x.shape[1]==13][0]
        t.columns=['Year']+list(range(1,13)); t=t[pd.to_numeric(t.Year,errors='coerce').notna()]
        s=t.melt(id_vars='Year',var_name='m',value_name='v').dropna()
        s['date']=pd.to_datetime(s.Year.astype(int).astype(str)+'-'+s.m.astype(str)+'-01')
        s.set_index('date').v.astype(float).sort_index().to_csv(f)
    return pd.read_csv(f,index_col=0,parse_dates=True).iloc[:,0]
if __name__=="__main__":
    df=pd.DataFrame({k:load(v) for k,v in SER.items()}).dropna()
    cr=lambda g,h,c:(g*42+h*42)/2-c
    df['fut4']=cr(df.g4,df.h4,df.c4); df['front']=cr(df.g1,df.h1,df.c1)
    df['real']=df.front.shift(-3); df['err']=df.real-df.fut4; df['slope']=df.front-df.fut4
    bt=df.dropna(subset=['real']); bt=bt[bt.index>='2016-01-01']
    def s(x,l): print('%-28s n=%3d  realized minus futures: mean %+.2f  median %+.2f  MAE %.2f  realized higher %d%%'%(l,len(x),x.err.mean(),x.err.median(),x.err.abs().mean(),round(100*(x.err>0).mean())))
    s(bt,'Jan 2016 - Jan 2024')
    s(bt[bt.slope>5],'backwardation > $5')
    s(bt[bt.slope<0],'contango')
    s(bt[(bt.index>='2022-03-01')&(bt.index<='2022-12-01')],'Mar-Dec 2022')
    print('no-change forecast MAE %.2f vs futures MAE %.2f'%((bt.real-bt.front).abs().mean(),bt.err.abs().mean()))
    bt[['fut4','front','real','err','slope']].round(2).to_csv(os.path.join(HERE,'..','data','futures_backtest_211.csv'))

