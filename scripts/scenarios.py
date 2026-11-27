# Bull / base / bear with probabilities, an expected value, a downside number, and a 2027 x 2028 crack grid.
# Same structure as the earlier odds script, on the blended margin model, calibrated to the workbook base ($337.00).
# Crack shock: one log shock to the whole curve, sd = the NY 2-1-1's annual log changes since 2007.
# Multiple: the crack-fitted forward multiple plus its own residual scatter.
import os,sys,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from eia_spot import load,SER
sp=pd.DataFrame({k:load(v) for k,v in SER.items()}).dropna(); sp['ny211']=(sp.ny_gas*42+sp.ny_ulsd*42)/2-sp.wti
sig=np.log(sp.groupby(sp.index.year).ny211.mean().loc[2007:2025]).diff().std()
fm=pd.read_csv(os.path.join(HERE,'..','data','vlo_forward_multiple.csv'),parse_dates=['date'],index_col=0)
h=fm.loc[:'2025-12-31']; h=h[h.index.year!=2020]; b=np.polyfit(h.crack_q,h.fwd,1); msd=np.std(h.fwd-np.polyval(b,h.crack_q),ddof=2)
W=0.77; mf=lambda c:W*(-0.965+0.4965*c)+(1-W)*(0.0525+0.5192*(c-2.15)); BBL=2.95*365
def raw(c27,c28,mres=0.0):
    e28=(mf(c28)-4.95)*BBL+400; e27=(mf(c27)-4.95)*BBL+400; ntm=e27/12+e28*11/12
    fcfe=(mf(c27)-4.95-2.42)*BBL*0.77+3016-2000
    return ((np.polyval(b,c28)+mres)*ntm+1231-3110+fcfe)/270.96+12.64
K=337.00-raw(44.75,35.25)              # calibration to the workbook base (payout 52%, Houston $5.39)
value=lambda c27,c28,mres=0.0: raw(c27,c28,mres)+K
rng=np.random.default_rng(7); n=400000; z=rng.normal(0,sig,n); mr=rng.normal(0,msd,n)
v=value(44.75*np.exp(z),35.25*np.exp(z),mr); P=323.0; DIV=4.8
print('crack log sd %.1f%%, multiple residual sd %.2fx, calibration %+.2f'%(sig*100,msd,K))
q=np.quantile(v,[0.25,0.75]); bear=v[v<=q[0]]; base=v[(v>q[0])&(v<q[1])]; bull=v[v>=q[1]]
print('bear (25%%): mean $%.0f | base (50%%): mean $%.0f | bull (25%%): mean $%.0f'%(bear.mean(),base.mean(),bull.mean()))
print('expected value $%.2f (return with dividend %+.1f%%); median $%.2f; 5th percentile $%.0f; 10th $%.0f'%(v.mean(),((v.mean()+DIV)/P-1)*100,np.median(v),np.percentile(v,5),np.percentile(v,10)))
for k in (200,250,280,323,400): print('   P(value < $%d) = %.0f%%'%(k,100*(v<k).mean()))
cz=lambda s:np.exp(np.quantile(z,s))
print('scenario cracks (2027/2028): bear %.1f/%.1f, base 44.8/35.3, bull %.1f/%.1f (25th/75th pct of the shock)'%(44.75*cz(.25),35.25*cz(.25),44.75*cz(.75),35.25*cz(.75)))
g27=[34.75,39.75,44.75,49.75,54.75]; g28=[25.25,30.25,35.25,40.25,45.25]
grid=pd.DataFrame([[round(value(a,c)) for a in g27] for c in g28],index=['2028 at %.2f'%c for c in g28],columns=['2027 at %.2f'%a for a in g27])
print(grid.to_string()); grid.to_csv(os.path.join(HERE,'..','data','value_grid_2027x2028.csv'))
# bucket detail for the article: average 2028 crack and value in each scenario bucket, and weight tilts
c28=35.25*np.exp(z)
for lab,m in [('bear',v<=q[0]),('base',(v>q[0])&(v<q[1])),('bull',v>=q[1])]:
    print('%s: value mean $%.0f, 2028 crack mean %.1f (range %.1f-%.1f)'%(lab,v[m].mean(),c28[m].mean(),np.percentile(c28[m],10),np.percentile(c28[m],90)))
print('5th percentile value $%.0f; P(value below price)=%.0f%%'%(np.percentile(v,5),100*(v<323).mean()))
