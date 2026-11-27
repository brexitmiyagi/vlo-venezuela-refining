# Valero's framework: minimum 40-50% of adjusted operating cash flow through the cycle, excess cash above a
# $4-5bn floor returned "over time" (Q4 2025 and Q3 2026 calls). Solve the payout share that ends 2027 with
# (a) cash held near today's $9.8bn, (b) cash at the $5bn top of the floor. Value is unchanged by design
# (cash is counted either way); EPS and the capital return are what move.
import os,sys,shutil,subprocess,tempfile
from openpyxl import load_workbook
HERE=os.path.dirname(os.path.abspath(__file__)); BASE=os.path.join(HERE,'..','model','VLO-three-statement-model.xlsx')
RECALC=os.environ.get('RECALC','recalc.py'); MCAP=90080
def run(p):
    d=tempfile.mkdtemp(); f=os.path.join(d,'w.xlsx'); shutil.copy(BASE,f)
    w=load_workbook(f); w['Inputs']['C38']=p; w.save(f); subprocess.run([sys.executable,RECALC,f,'90'],capture_output=True)
    w=load_workbook(f,data_only=True); C=w['CF']; I=w['IS']; V=w['Value']
    g=lambda r,c: C.cell(r,c).value
    return dict(p=p,cash27=g(16,9),div27=-g(11,9),bb27=-g(12,9),ret27=g(19,9),ret28=g(19,10),eps27=I['I22'].value,eps28=I['J22'].value,value=V['C18'].value)
def solve(target):
    lo,hi=0.52,1.5
    for _ in range(12):
        m=(lo+hi)/2; r=run(m)
        if r['cash27']>target: lo=m
        else: hi=m
    return run((lo+hi)/2)
for lab,res in [('Valero actual 52%',run(0.52)),('cash held at $9.8bn',solve(9800)),('cash to $5bn floor',solve(5000)),('FY2025 actual 67%',run(0.67))]:
    print('%-22s payout %3.0f%%: 2027 return $%.2fbn (%.1f%% of mkt cap; buybacks $%.2fbn), 2028 $%.2fbn (%.1f%%), cash end-27 $%.1fbn, EPS27 $%.2f, EPS28 $%.2f, value $%.2f'%(
        lab,res['p']*100,res['ret27']/1e3,res['ret27']/MCAP*100,res['bb27']/1e3,res['ret28']/1e3,res['ret28']/MCAP*100,res['cash27']/1e3,res['eps27'],res['eps28'],res['value']))
