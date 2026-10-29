import csv,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'data/checks.csv';rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
print('CHECKS',len(rows));gaps=[r for r in rows if r['result']!=r['expected']]
for r in gaps:print('GAP',r['id'],r['layer'],r['test'])
print('GAP_COUNT',len(gaps))
