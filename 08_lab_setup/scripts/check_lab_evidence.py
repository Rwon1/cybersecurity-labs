#!/usr/bin/env python3
"""Offline audit of a synthetic evidence checklist. No system changes."""
import csv,sys
from pathlib import Path
ALLOWED={'pass','review'}
def main():
    if len(sys.argv)!=2:
        print('USAGE python3 scripts/check_lab_evidence.py data/example_checks.csv');return 2
    p=Path(sys.argv[1]); rows=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
    if not rows or set(rows[0])!={'check_id','status','reason'}:
        print('ERROR invalid CSV schema');return 2
    ids=set()
    for row in rows:
        if not row['check_id'] or row['check_id'] in ids or row['status'] not in ALLOWED:
            print('ERROR invalid or duplicate check');return 2
        ids.add(row['check_id'])
    rev=[r for r in rows if r['status']=='review']
    print('CHECKS',len(rows));print('PASS',len(rows)-len(rev));print('REVIEW',len(rev))
    for r in rev:print('REVIEW',r['check_id'],r['reason'] or 'reason-not-provided')
    return 0
if __name__=='__main__':raise SystemExit(main())
