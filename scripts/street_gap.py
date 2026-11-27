# Breaks the gap between Street 2027 EBITDA/EPS and my curve-based model into named assumptions,
# and solves for the crack the Street and the share price each imply. Uses the workbook via run_workbook.py.
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, os
from run_workbook import run
STREET27,STREET28,EPS27S=20395,12468,49.86; PRICE,DIV,COE=323.0,4.80,0.0935
b=run({}); lean=run({('Inputs','C23'):2.04}); c28u=run({('Inputs','C21'):40.25}); c27u=run({('Inputs','C20'):49.75})
BBL=2.95*365; crude=0.178*(8.00-5.17)*BBL      # Q3 Maya discount ($8.00) held all year vs 2025 ($5.17), heavy-sour share 0.178
s27=(c27u['ebitda27']-b['ebitda27'])/5; s28=(c28u['ebitda28']-b['ebitda28'])/5; v28=(c28u['value']-b['value'])/5
print('my 2027 EBITDA $%.0fm, EPS %.2f | Street $%d, %.2f | gap $%.0fm (%.1f%%), EPS %.2f'%(b['ebitda27'],b['eps27'],STREET27,EPS27S,STREET27-b['ebitda27'],(STREET27/b['ebitda27']-1)*100,EPS27S-b['eps27']))
print(' 1. realized cracks beat futures by the 2016-24 average ($2.04): +$%.0fm EBITDA, EPS +%.2f'%(lean['ebitda27']-b['ebitda27'],lean['eps27']-b['eps27']))
print(' 2. Q3 heavy-crude discount lasts all year: +$%.0fm EBITDA, EPS +%.2f'%(crude,crude*0.77/b.get('sh27',262.2)))
print('    left after 1 and 2: $%.0fm EBITDA'%(STREET27-b['ebitda27']-(lean['ebitda27']-b['ebitda27'])-crude))
print('EBITDA per $1 of crack: 2027 $%.0fm, 2028 $%.0fm; value per $1 of 2028 crack $%.2f'%(s27,s28,v28))
print('Street-implied NY 2-1-1: 2027 %.2f (curve 44.75), 2028 %.2f (curve 35.25)'%(44.75+(STREET27-b['ebitda27'])/s27,35.25+(STREET28-b['ebitda28'])/s28))
tgt=PRICE*(1+COE)-DIV; c=35.25+(tgt-b['value'])/v28
chk=run({('Inputs','C21'):round(c,2)})
print('price-implied 2028 NY 2-1-1 (value that earns the 9.35%% cost of equity, $%.2f): %.2f; check value at that crack $%.2f'%(tgt,c,chk['value']))
json.dump(dict(base=b,lean=lean,s27=s27,s28=s28,v28=v28,implied28=c,check=chk),open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results','street_gap.json'),'w'),default=float)
