import sys
from pathlib import Path
if len(sys.argv)!=3:sys.exit('Usage: tamper.py source destination')
a=bytearray(Path(sys.argv[1]).read_bytes());a[-1]^=1
p=Path(sys.argv[2]);
if p.exists():sys.exit('Refusing to overwrite')
p.write_bytes(a);print('Tampered copy:',p)
