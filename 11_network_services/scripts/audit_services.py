import csv,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'data/services.csv'
rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
print('SERVICES',len(rows))
findings=[]
for r in rows:
 why=[]
 if r['enabled']=='yes' and r['expected']=='loopback' and r['bind'] not in ('127.0.0.1','127.0.0.53','::1'):why.append('exposed-beyond-loopback')
 if r['enabled']=='no' and r['bind']=='0.0.0.0':why.append('verify-disabled')
 if why:findings.append((r['service'],','.join(why)))
for n,w in findings:print('REVIEW',n,w)
print('REVIEW_COUNT',len(findings))
