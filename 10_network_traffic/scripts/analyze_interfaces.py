import csv,ipaddress
with open('data/interfaces.csv',newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
print('INTERFACES',len(rows))
for r in rows:
 net=ipaddress.ip_interface(r['address']+'/'+r['prefix']).network
 print(r['interface'],r['role'],str(net),'GATEWAY',r['gateway'] or '-')
print('DEFAULT_ROUTE',next((r['gateway'] for r in rows if r['gateway']),'-'))
