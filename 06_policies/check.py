import csv
import hashlib
import shutil
from datetime import date, timedelta
from pathlib import Path

folder = Path(__file__).resolve().parent
data = folder / 'data'
as_of = date(2026, 10, 13)

def read(name):
    with (data / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def save(name, rows):
    with (folder / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

accounts = {r['User']: r for r in read('accounts.csv')}
mfa = [r for r in accounts.values() if r['Type'] == 'Staff' and r['MFA'] != 'Enabled']
save('mfa_violations.csv', mfa)
expected = {(r['User'], r['Group']) for r in read('expected_access.csv')}
deviations = []
for r in read('actual_access.csv'):
    reasons = []
    if (r['User'], r['Group']) not in expected:
        reasons.append('Нет в согласованном списке')
    if date.fromisoformat(r['Expires']) < as_of:
        reasons.append('Срок истёк')
    account = accounts.get(r['User'])
    if account and account['Status'] == 'Disabled':
        reasons.append('У отключённой учётной записи осталось право')
    if account and account['Type'] == 'Staff' and account['MFA'] != 'Enabled':
        reasons.append('Staff без MFA')
    if reasons:
        deviations.append({**r, 'Reason': '; '.join(reasons)})
save('access_review.csv', deviations)

remote = []
for r in read('remote_access.csv'):
    reasons = []
    for field, required in [('MFA', 'Enabled'), ('ManagedDevice', 'yes'), ('VPN', 'yes'), ('Approval', 'Approved')]:
        if r[field] != required:
            reasons.append(field + '=' + r[field])
    if accounts[r['User']]['Status'] != 'Active':
        reasons.append('Аккаунт отключён')
    remote.append({**r, 'Result': 'FAIL' if reasons else 'PASS', 'Reason': '; '.join(reasons)})
save('remote_review.csv', remote)

training = []
for r in read('training.csv'):
    due = date.fromisoformat(r['LastCompleted']) + timedelta(days=int(r['RequiredIntervalDays']))
    training.append({**r, 'Due': due.isoformat(), 'OverdueDays': max(0, (as_of - due).days)})
save('training_review.csv', training)
save('timeline.csv', sorted(read('security_events.csv'), key=lambda r: r['Time']))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

checks = []
for source in sorted((data / 'course-data').iterdir()):
    if not source.is_file():
        continue
    backup = folder / 'backup' / source.name
    restored = folder / 'restore-test' / source.name
    backup.parent.mkdir(exist_ok=True)
    restored.parent.mkdir(exist_ok=True)
    shutil.copy2(source, backup)
    shutil.copy2(backup, restored)
    hashes = [sha(p) for p in (source, backup, restored)]
    same = len(set(hashes)) == 1
    checks.append({'File': source.name, 'OriginalSHA256': hashes[0], 'BackupSHA256': hashes[1],
                   'RestoreSHA256': hashes[2], 'Result': 'PASS' if same else 'FAIL'})
    assert same
save('backup_check.csv', checks)
lines = [f'Дата проверки: {as_of}', f'Staff без MFA: {len(mfa)}',
         'Пользователи без MFA: ' + ', '.join(r['User'] for r in mfa),
         f'Строк доступа с отклонениями: {len(deviations)}',
         'Удалённый доступ: ' + ', '.join(r['User'] + ' ' + r['Result'] for r in remote),
         'Просроченное обучение: ' + ', '.join(r['User'] + ': ' + str(r['OverdueDays']) + ' дн.' for r in training if r['OverdueDays']),
         f'Создана копия и восстановлены файлы: {len(checks)}; SHA-256 совпали.']
(folder / 'output.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
