# Which margin model to trust for 2027: NY Harbor or Gulf Coast? Same 31 quarters, same tests.
# (1) leave-one-quarter-out errors, all quarters and high-crack quarters
# (2) fit on 2019-2021 only, predict 2022-2026 (the high-crack regime nobody had seen)
# (3) annual errors, throughput-weighted, from the quarterly fits
# Then weight the two 2027 forecasts by inverse squared out-of-sample error.
import os,numpy as np,pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); D=lambda f:os.path.join(HERE,'..','data',f)
q=pd.read_csv(D('quarterly_model_inputs.csv'),index_col=0)
r=pd.read_csv(D('valero_quarterly_releases.csv')).set_index('quarter'); q['thru']=r.throughput_kbd.reindex(q.index)
def fit(x,y): b=np.polyfit(x,y,1); return b
def loo(col):
    e=[]
    for i in q.index:
        t=q.drop(i); b=fit(t[col],t.margin_bbl); e.append(q.loc[i,'margin_bbl']-np.polyval(b,q.loc[i,col]))
    return pd.Series(e,index=q.index)
q['e_ny']=loo('ny211'); q['e_gc']=loo('gc211')
hi=q[q.ny211>35]
print('LOO quarterly RMSE all: NY %.2f GC %.2f | NY 2-1-1 > $35 (n=%d): NY %.2f GC %.2f'%(np.sqrt((q.e_ny**2).mean()),np.sqrt((q.e_gc**2).mean()),len(hi),np.sqrt((hi.e_ny**2).mean()),np.sqrt((hi.e_gc**2).mean())))
print(hi[['ny211','gc211','margin_bbl','e_ny','e_gc']].round(2).to_string())
tr=q.loc[:'2021Q4']; te=q.loc['2022Q1':]
bn=fit(tr.ny211,tr.margin_bbl); bg=fit(tr.gc211,tr.margin_bbl)
te=te.assign(o_ny=te.margin_bbl-np.polyval(bn,te.ny211),o_gc=te.margin_bbl-np.polyval(bg,te.gc211))
print('fit 2019-21, predict 2022-26Q3 (n=%d): RMSE NY %.2f GC %.2f; mean error NY %+.2f GC %+.2f'%(len(te),np.sqrt((te.o_ny**2).mean()),np.sqrt((te.o_gc**2).mean()),te.o_ny.mean(),te.o_gc.mean()))
q['yr']=q.index.str[:4]
ann=q.groupby('yr').apply(lambda x:pd.Series(dict(e_ny=np.average(x.e_ny,weights=x.thru),e_gc=np.average(x.e_gc,weights=x.thru),ny=np.average(x.ny211,weights=x.thru))))
print('annual LOO errors:'); print(ann.round(2).T.to_string())
annhi=ann[ann.ny>35]; print('annual RMSE all: NY %.2f GC %.2f; high-crack years %s: NY %.2f GC %.2f'%(np.sqrt((ann.e_ny**2).mean()),np.sqrt((ann.e_gc**2).mean()),list(annhi.index),np.sqrt((annhi.e_ny**2).mean()),np.sqrt((annhi.e_gc**2).mean())))
# gap uncertainty for the Gulf route: annual futures-less-Gulf-spot 2016-2024 (gulf_basis.py)
gap=np.array([2.20,1.32,2.06,1.66,2.23,1.86,1.81,2.22,3.96]); sg=gap.std(ddof=1)
bG=fit(q.gc211,q.margin_bbl); bN=fit(q.ny211,q.margin_bbl)
var_g=np.sqrt((annhi.e_gc**2).mean())**2+(bG[0]*sg)**2; var_n=np.sqrt((annhi.e_ny**2).mean())**2
w_n=(1/var_n)/(1/var_n+1/var_g)
print('quarterly-fit NY model: margin = %.3f + %.4f x NY 2-1-1'%(bN[1],bN[0]))
print('Gulf route adds gap uncertainty: sd of annual gap %.2f -> %.2f/bbl of margin'%(sg,bG[0]*sg))
print('weights from high-crack annual errors (+gap risk on Gulf): NY %.2f, Gulf %.2f'%(w_n,1-w_n))
c27=44.75; mn=np.polyval(bN,c27); mg=np.polyval(bG,c27-gap.mean()); ma=0.809+0.445*c27
print('2027 margin: annual NY model %.2f | quarterly NY model %.2f | Gulf model %.2f'%(ma,mn,mg))
pd.DataFrame(dict(w_ny=[w_n],sd_ny=[np.sqrt(var_n)],sd_gc=[np.sqrt(var_g)],m_ny_q=[mn],m_gc=[mg],m_ny_a=[ma])).round(4).to_csv(D('model_choice.csv'),index=False)
