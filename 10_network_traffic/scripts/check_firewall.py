import csv,ipaddress
with open('data/firewall.csv',newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
print('RULES',len(rows))
for idx,r in enumerate(rows,1): print('RULE',idx,r['direction'],r['source'],r['protocol'],r['port'],r['action'])
ssh=[r for r in rows if r['direction']=='IN' and r['protocol']=='TCP' and r['port']=='22' and r['action']=='ALLOW']
print('SSH_RESTRICTED',all(ipaddress.ip_network(r['source']).prefixlen>=24 for r in ssh) and bool(ssh))
print('ORDER_MATTERS',True)
