import csv
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'data/cases.csv'
with p.open(encoding='utf8') as f:rows=list(csv.DictReader(f))
print('CASES',len(rows))
for r in rows:print(r['case'],r['control'],r['limitation'],sep=' | ')
print('ALL_HAVE_LIMITATION',all(r['limitation'] for r in rows))
