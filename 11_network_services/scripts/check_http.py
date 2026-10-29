import csv,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'data/http_cases.csv';rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
print('HTTP_CASES',len(rows))
for r in rows:print(r['case'],r['method'],r['path'],r['status'])
print('ERROR_RESPONSES',sum(int(r['status'])>=400 for r in rows))
