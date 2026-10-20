"""Delete the source sheets listed in <work_dir>/manifest.json after split.py succeeded.
Run from the repo root: python tools/remove_originals.py <work_dir>"""
import json,os,sys
items=json.load(open(sys.argv[1]+'/manifest.json',encoding='utf-8'))
for it in items:
    if os.path.exists(it['path']): os.remove(it['path'])
print('removed',len(items))
