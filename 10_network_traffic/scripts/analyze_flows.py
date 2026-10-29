import csv,collections
with open('data/flows.csv',newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
print('FLOWS',len(rows))
print('TCP',sum(r['proto']=='TCP' for r in rows))
print('UDP',sum(r['proto']=='UDP' for r in rows))
print('ICMP',sum(r['proto']=='ICMP' for r in rows))
for r in rows:
 if r['result'] in ('NO_RESPONSE','RST'):
  print('REVIEW',r['time'],r['dst'],r['dport'],r['result'])
print('SSH_HANDSHAKE',all(x in [r['flags'] for r in rows if r['dport']=='22' or r['sport']=='22'] for x in ['S','SA','A']))
