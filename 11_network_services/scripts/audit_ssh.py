import csv,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'data/ssh_policy.csv';rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
print('SSH_SETTINGS',len(rows));findings=[]
for r in rows:
 if r['value']!=r['expected']:findings.append(r)
for r in findings:print('REVIEW',r['setting'],'actual='+r['value'],'target='+r['expected'])
print('REVIEW_COUNT',len(findings))
