# Is my quarterly model low the way the consensus is? Uses the clean (pre-print data only) backtest from
# indicator_backtest_clean.py: crack-only margin forecast, translated to EPS with each quarter's EPS-per-$1 margin.
import os, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__))
t=pd.read_csv(os.path.join(HERE,'..','data','indicator_backtest_clean.csv')); t=t.rename(columns={t.columns[0]:'quarter'})
t['model_err']=t.crack_only_eps-t.eps_actual; t['consensus_err']=t.consensus-t.eps_actual; t['model_minus_consensus']=t.crack_only_eps-t.consensus
print(t[['quarter','eps_actual','consensus','crack_only_eps','model_err','consensus_err','model_minus_consensus']].round(2).to_string(index=False))
print('quarters: %d; model below consensus: %d; median error model %+.2f, consensus %+.2f; mean error model %+.2f, consensus %+.2f; mean absolute error model %.2f, consensus %.2f'%(
 len(t),(t.model_minus_consensus<0).sum(),t.model_err.median(),t.consensus_err.median(),t.model_err.mean(),t.consensus_err.mean(),t.model_err.abs().mean(),t.consensus_err.abs().mean()))
t.round(3).to_csv(os.path.join(HERE,'..','results','q4_model_bias.csv'),index=False)
