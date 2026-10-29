import csv
from pathlib import Path

folder=Path(__file__).resolve().parent
def read(name):
    with (folder/'data'/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))
users={r['User']:r for r in read('users.csv')}
resources={r['Resource']:r for r in read('resources.csv')}
original={(r['Role'],r['ResourceType'],r['Action']) for r in read('role_permissions.csv')}
corrected=original-{('Student','RoleConfig','manage')}

def evaluate(user,resource,action,permissions):
    if user['Status']!='Active':return 'DENY','Учетная запись отключена'
    if (user['Role'],resource['Type'],action) not in permissions:return 'DENY','Роль не разрешает действие'
    if resource['Type']=='OwnGrade' and resource['Owner']!=user['User']:return 'DENY','Чужая оценка'
    if resource['Type']=='GroupGrades' and user['Department']!=resource['Department']:return 'DENY','Другая кафедра'
    if action in ('write','manage') and user['ManagedDevice']!='yes':return 'DENY','Неуправляемое устройство'
    return 'ALLOW','Роль и условия доступа выполнены'

rows=[]
for req in read('access_requests.csv'):
    u=users[req['User']];r=resources[req['Resource']]
    before,_=evaluate(u,r,req['Action'],original)
    after,reason=evaluate(u,r,req['Action'],corrected)
    rows.append({**req,'Before':before,'After':after,'Reason':reason})
with (folder/'decisions.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
for r in rows:print(r['Request'],r['Before'],'->',r['After'],r['Reason'])

teacher=dict(users['teacher1'])
teacher['Role']='Methodist'
assert evaluate(teacher,resources['group_cs'],'read',corrected)[0]=='ALLOW'
assert evaluate(teacher,resources['group_cs'],'write',corrected)[0]=='DENY'
assert evaluate(users['student1'],resources['grade_s2'],'read',corrected)[0]=='DENY'
assert evaluate(users['former1'],resources['group_cs'],'write',corrected)[0]=='DENY'
assert next(r for r in rows if r['Request']=='R08')['Before']=='ALLOW'
assert next(r for r in rows if r['Request']=='R08')['After']=='DENY'
(folder/'role_change.txt').write_text('teacher1: Teacher -> Methodist\ngroup_cs read: ALLOW\ngroup_cs write: DENY\nformer1 write: DENY\nЭто проверка модели в CSV, не изменение реальной учетной записи.\n',encoding='utf-8')
print('Смена роли: read ALLOW, write DENY. Чужая оценка и бывший сотрудник: DENY.')
