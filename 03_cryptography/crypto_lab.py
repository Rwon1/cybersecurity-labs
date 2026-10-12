from pathlib import Path
import hashlib, hmac, secrets, time
from cryptography.exceptions import InvalidTag, InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

folder=Path(__file__).resolve().parent
message=(folder/'data/message.txt').read_bytes()
changed=message.replace(b'85',b'86',1)
assert len(message)==len(changed) and sum(a!=b for a,b in zip(message,changed))==1
lines=[]
def show(text):
    lines.append(text)
    print(text)

def caesar(text,shift):
    result=''
    for c in text:
        if 'A'<=c<='Z': result+=chr((ord(c)-ord('A')+shift)%26+ord('A'))
        elif 'a'<=c<='z': result+=chr((ord(c)-ord('a')+shift)%26+ord('a'))
        else: result+=c
    return result

encrypted=caesar('UNIVERSITY',3)
assert caesar(encrypted,-3)=='UNIVERSITY'
show('Caesar: '+encrypted+' -> '+caesar(encrypted,-3))
show('Перебор сдвигов: '+'; '.join(f'{i}: {caesar(encrypted,-i)}' for i in range(1,26)))
show('SHA-256 исходный: '+hashlib.sha256(message).hexdigest())
show('SHA-256 после замены 85 на 86: '+hashlib.sha256(changed).hexdigest())

key=AESGCM.generate_key(bit_length=256)
nonce=secrets.token_bytes(12)
aad=b'course=SEC101'
ciphertext=AESGCM(key).encrypt(nonce,message,aad)
assert AESGCM(key).decrypt(nonce,ciphertext,aad)==message
show('AES-GCM: расшифрование совпало с исходным сообщением')
tampered=bytearray(ciphertext);tampered[0]^=1
for label,data,metadata in [('Подмена шифротекста',bytes(tampered),aad),('Подмена AAD',ciphertext,b'course=OTHER')]:
    try:
        AESGCM(key).decrypt(nonce,data,metadata)
    except InvalidTag:
        show(label+': отклонена (InvalidTag)')
    else:
        raise AssertionError('Подмена не обнаружена')

private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
public=private.public_key()
oaep=padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None)
wrapped=public.encrypt(key,oaep)
unwrapped=private.decrypt(wrapped,oaep)
assert AESGCM(unwrapped).decrypt(nonce,ciphertext,aad)==message
show('Гибридная схема: RSA-OAEP передал AES-ключ; AES-GCM восстановил сообщение')
pss=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH)
signature=private.sign(message,pss,hashes.SHA256())
public.verify(signature,message,pss,hashes.SHA256())
show('RSA-PSS: подпись создана закрытым ключом и проверена открытым')
try:
    public.verify(signature,changed,pss,hashes.SHA256())
except InvalidSignature:
    show('RSA-PSS: изменённое сообщение отклонено')
else:
    raise AssertionError('Изменённая подпись принята')

alice=ec.generate_private_key(ec.SECP256R1())
bob=ec.generate_private_key(ec.SECP256R1())
a_secret=alice.exchange(ec.ECDH(),bob.public_key())
b_secret=bob.exchange(ec.ECDH(),alice.public_key())
salt=secrets.token_bytes(16)
def derive(secret):
    return HKDF(algorithm=hashes.SHA256(),length=32,salt=salt,info=b'SEC101 ECDH').derive(secret)
a_key,b_key=derive(a_secret),derive(b_secret)
assert a_key==b_key
ec_nonce=secrets.token_bytes(12)
ec_cipher=AESGCM(a_key).encrypt(ec_nonce,message,aad)
assert AESGCM(b_key).decrypt(ec_nonce,ec_cipher,aad)==message
show('ECDH + HKDF + AES-GCM: общий ключ совпал, сообщение восстановлено')

password=b'fictional-course-passphrase'
salt1,salt2=secrets.token_bytes(16),secrets.token_bytes(16)
def kdf(p,s):
    return hashlib.scrypt(p,salt=s,n=2**14,r=8,p=1,dklen=32)
start=time.perf_counter(); digest1=kdf(password,salt1); slow=time.perf_counter()-start
digest2=kdf(password,salt2)
assert digest1!=digest2
assert hmac.compare_digest(digest1,kdf(password,salt1))
assert not hmac.compare_digest(digest1,kdf(b'wrong-password',salt1))
start=time.perf_counter()
for _ in range(10000): hashlib.sha256(password).digest()
fast=(time.perf_counter()-start)/10000
show('scrypt: одна фраза с двумя разными salt даёт разные результаты')
show('scrypt: верный пароль принят, неверный отклонён')
show(f'Учебные параметры scrypt: N=16384, r=8, p=1, salt=16 байт; {slow*1000:.3f} мс')
show(f'SHA-256: {fast*1000:.6f} мс на операцию (среднее 10000 повторов)')
show('Ключи существуют только в памяти и в файл не записываются.')
(folder/'output.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
