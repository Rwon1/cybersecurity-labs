import hashlib
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'data/document.txt';a=p.read_bytes();b=a+b'change\n'
print('ORIGINAL_SHA256',hashlib.sha256(a).hexdigest())
print('CHANGED_SHA256',hashlib.sha256(b).hexdigest())
print('DIFFERENT',hashlib.sha256(a).digest()!=hashlib.sha256(b).digest())
