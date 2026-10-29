import csv,collections
with open('data/dns.csv',newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
print('DNS_RECORDS',len(rows))
for r in rows: print(r['name'],r['type'],r['status'],r['answer'] or '-')
print('NXDOMAIN',sum(r['status']=='NXDOMAIN' for r in rows))
print('EMPTY_AAAA',sum(r['type']=='AAAA' and not r['answer'] for r in rows))
