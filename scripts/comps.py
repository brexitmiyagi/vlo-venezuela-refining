# Covered-universe comps: Seeking Alpha market data (25 Nov 2026 close) and consensus (27 Nov 2026).
import os,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=lambda f:os.path.join(HERE,'..','data',f)
m=pd.read_csv(D('peer_market_2026-11-25.csv'),index_col=0); c=pd.read_csv(D('peer_check.csv'),index_col=0)
t=pd.DataFrame(index=m.index)
t['Price']=c['price_2026-11-25']; t['Mkt cap $bn']=m.mcap_m/1000; t['EV $bn']=m.tev_m/1000
t['EV/EBITDA 27']=m.tev_m/c.cons_ebitda_2027; t['EV/EBITDA 28']=m.tev_m/c.cons_ebitda_2028
t['P/E 27']=c['price_2026-11-25']/c.cons_eps_2027; t['P/E 28']=c['price_2026-11-25']/c.cons_eps_2028
t['Div yield %']=m.div_yield_fwd_pct; t['Street 27 vs 2022 analog %']=c['excess27_%']; t['Street 28 vs 2023 analog %']=c['excess28_%']
mine=dict(eps27=44.64,eps28=29.80,ebitda27=18752,ebitda28=13050)
print(t.round(2).to_string())
print('VLO on my numbers: EV/EBITDA 27 %.2fx, 28 %.2fx; P/E 27 %.2fx, 28 %.2fx'%(m.loc['VLO','tev_m']/mine['ebitda27'],m.loc['VLO','tev_m']/mine['ebitda28'],323/mine['eps27'],323/mine['eps28']))
t.round(2).to_csv(D('comps_2026-11-25.csv'))
