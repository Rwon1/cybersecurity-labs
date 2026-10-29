#!/usr/bin/env python3
"""Read synthetic permission metadata; never inspect or change the real filesystem."""
import csv,sys
from pathlib import Path

def main():
    source=Path(sys.argv[1] if len(sys.argv)>1 else 'data/permissions.csv')
    with source.open(encoding='utf-8',newline='') as f: records=list(csv.DictReader(f))
    reviews=[]
    for r in records:
        issues=[]
        try: mode=int(r['mode'],8)
        except ValueError: issues.append('invalid-mode');mode=0
        if not r['owner'].strip():issues.append('missing-owner')
        if mode & 0o002:issues.append('world-writable')
        if r['sensitive']=='yes' and (mode & 0o004):issues.append('sensitive-world-readable')
        if r['sensitive']=='yes' and (mode & 0o020):issues.append('sensitive-group-writable')
        if issues:reviews.append((r['id'],','.join(issues)))
    print(f'OBJECTS {len(records)}')
    print(f'PASS {len(records)-len(reviews)}')
    print(f'REVIEW {len(reviews)}')
    for key,issues in reviews:print(f'REVIEW {key} {issues}')
if __name__=='__main__':main()
