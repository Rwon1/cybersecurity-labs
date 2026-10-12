import csv
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

folder = Path(__file__).resolve().parent
data = folder / 'data'

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def save(name, rows):
    with (folder / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def utc(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    assert dt.utcoffset() is not None
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

events = read(data / 'events.csv')
assert events == read(data / 'security_events.csv')
save('events_sorted.csv', sorted(events, key=lambda r: utc(r['Time'])))
timeline = []
for name in ('windows.csv', 'linux.csv', 'lms.csv'):
    for r in read(data / name):
        timeline.append({'UTC': utc(r['Time']), 'OriginalTime': r['Time'], 'Source': name,
                         'User': r['User'], 'Action': r['Action'], 'SourceIP': r['SourceIP'],
                         'Detail': r.get('Detail', ''), 'EventId': r.get('EventId', '')})
timeline.sort(key=lambda r: (r['UTC'], r['Source']))
save('timeline.csv', timeline)
assert len(timeline) == 19
assert next(r for r in timeline if r['Source'] == 'windows.csv')['UTC'] == '2026-10-01T09:02:00Z'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

collected = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
evidence = []
for name in ('events.csv', 'windows.csv', 'linux.csv', 'lms.csv', 'tabletop_injects.csv', 'recovery_checks.csv'):
    source = data / name
    target = folder / 'evidence' / name
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source) == sha(target)
    evidence.append({'File': name, 'Source': 'data/' + name, 'Copy': 'evidence/' + name,
                     'SHA256': sha(source), 'CopySHA256': sha(target), 'Collector': 'Егоров',
                     'CollectedUTC': collected, 'Result': 'MATCH'})
save('evidence_register.csv', evidence)

backup = data / 'backup' / 'grades.csv'
target = folder / 'restore-test' / 'grades.csv'
target.parent.mkdir(exist_ok=True)
shutil.copy2(backup, target)
restore = []
for name, path in [('Полученный restore', data/'restore'/'grades.csv'),
                   ('Контрольный изменённый файл', data/'restore'/'grades_altered.csv'),
                   ('Локальное восстановление', target)]:
    restore.append({'Check': name, 'BackupSHA256': sha(backup), 'FileSHA256': sha(path),
                    'Result': 'MATCH' if sha(backup) == sha(path) else 'DIFFERENT'})
save('restore_hashes.csv', restore)
assert [r['Result'] for r in restore] == ['MATCH', 'DIFFERENT', 'MATCH']
assert len(read(target)) == 3
checks = read(data / 'recovery_checks.csv')
failed = [r for r in checks if r['Status'] != 'PASS']
lines = [f'events.csv: {len(events)} событий; security_events.csv — его дубликат.',
         f'Windows + Linux + LMS: {len(timeline)} событий, время UTC.',
         f'Сохранено копий журналов и материалов: {len(evidence)}; хеши совпали.',
         'Restore: исходный файл совпал; изменённый отличается; локальная копия совпала.',
         'В локальной копии 3 строки оценок.',
         'Учебные функциональные проверки из recovery_checks.csv:']
lines += [r['Test'] + ': ' + r['Status'] for r in checks]
lines += ['Закрытие INC-104: нельзя, есть FAIL и NOT_TESTED.']
(folder / 'output.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
