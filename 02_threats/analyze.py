import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

folder=Path(__file__).resolve().parent
def read(name):
    with (folder/'data'/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

counts=defaultdict(Counter)
for row in read('auth_attempts.csv'):
    counts[(row['User'],row['SourceIP'])][row['Result']]+=1
lines=['Входы: пользователь | IP | FAIL | SUCCESS']
for (user,ip),count in sorted(counts.items()):
    lines.append(f'{user} | {ip} | {count["FAIL"]} | {count["SUCCESS"]}')
metrics=read('service_metrics.csv')
for label,rows in [('До 10:12',metrics[:12]),('10:12–10:21',metrics[12:22]),('После 10:21',metrics[22:])]:
    lines.append(f'{label}: запросов/мин={mean(int(r["Requests"]) for r in rows):.1f}; '
                 f'ошибок={mean(float(r["ErrorRatePct"]) for r in rows):.1f}%; '
                 f'задержка={mean(int(r["LatencyMs"]) for r in rows):.1f} мс')
lines.append('Пик относительно среднего до всплеска: '+str(round(max(int(r['Requests']) for r in metrics)/mean(int(r['Requests']) for r in metrics[:12]),2))+' раза')
text='\n'.join(lines)+'\n'
(folder/'output.txt').write_text(text,encoding='utf-8')
print(text)
