# Helper: set inputs on a copy of the workbook, recalculate with LibreOffice, read results.
import os,shutil,subprocess,sys,json,tempfile
from openpyxl import load_workbook
HERE=os.path.dirname(os.path.abspath(__file__)); BASE=os.path.join(HERE,'..','model','VLO-three-statement-model.xlsx')
RECALC=os.environ.get('RECALC','recalc.py')
def run(sets):
    d=tempfile.mkdtemp(); f=os.path.join(d,'w.xlsx'); shutil.copy(BASE,f)
    w=load_workbook(f)
    for (sh,cell),v in sets.items(): w[sh][cell]=v
    w.save(f); subprocess.run([sys.executable,RECALC,f,'90'],capture_output=True)
    w=load_workbook(f,data_only=True); I=w['IS']; V=w['Value']
    return dict(m27=I['I5'].value,m28=I['J5'].value,eps27=I['I22'].value,eps28=I['J22'].value,ebitda27=I['I23'].value,ebitda28=I['J23'].value,value=V['C18'].value,ret=V['C19'].value,rating=V['C20'].value,mult=V['C8'].value,ntm=V['C9'].value)
if __name__=='__main__': print(json.dumps(run({}),indent=0))
