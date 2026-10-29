#!/usr/bin/env python3
import argparse,os,sys
from pathlib import Path
try:
 from cryptography.hazmat.primitives.ciphers.aead import AESGCM
 from cryptography.exceptions import InvalidTag
except ImportError:sys.exit('Install python3-cryptography')
p=argparse.ArgumentParser();p.add_argument('action',choices=['encrypt','decrypt']);p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--keyfile',required=True);a=p.parse_args()
src=Path(a.input);dst=Path(a.output);keyfile=Path(a.keyfile)
if dst.exists():sys.exit('Refusing to overwrite output')
if a.action=='encrypt':
 if keyfile.exists():sys.exit('Refusing to overwrite key')
 key=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12);cipher=AESGCM(key).encrypt(nonce,src.read_bytes(),b'lecture12-v1')
 fd=os.open(keyfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(key)
 dst.write_bytes(b'L12A'+nonce+cipher);print('Encrypted:',dst);print('Key:',keyfile)
else:
 data=src.read_bytes()
 if len(data)<32 or data[:4]!=b'L12A':sys.exit('Invalid file format')
 try:plain=AESGCM(keyfile.read_bytes()).decrypt(data[4:16],data[16:],b'lecture12-v1')
 except (InvalidTag,ValueError):sys.exit('Authentication failed')
 dst.write_bytes(plain);print('Decrypted:',dst)
