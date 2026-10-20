"""Collect sheets from the grid folders into <work>/manifest.json and render labeled preview pages <work>/pages/pNNN.png+txt.
Run from the repo root: python tools/manifest.py <work_dir>"""
import os,json,sys
from PIL import Image, ImageDraw
S=sys.argv[1]
os.makedirs(S+'/pages',exist_ok=True);os.makedirs(S+'/names',exist_ok=True)
items=[]
for d in ['2x2','3x3','4x4','6x6','7x7','8x8','etc']:
    for f in sorted(os.listdir(d)):
        if not f.endswith('.png'):continue
        p=os.path.join(d,f); w,h=Image.open(p).size
        # tiles are 16px: 32px sheet = 2x2, 48px = 3x3, 64px = 4x4 ...; anything else needs manual handling
        g=w//16 if w==h and w%16==0 and w<=128 else None
        if g is None: print('skip (not a 16px grid):',p,(w,h)); continue
        items.append({'id':len(items)+1,'path':p,'grid':g,'name':f[:-4]})
json.dump(items,open(S+'/manifest.json','w'),ensure_ascii=False,indent=0)
PER=20;COLS=5;CELL=168
for pg in range(0,len(items),PER):
    chunk=items[pg:pg+PER]; n=pg//PER+1
    rows=(len(chunk)+COLS-1)//COLS
    c=Image.new('RGB',(COLS*CELL,rows*(CELL+18)),(255,0,255))
    dr=ImageDraw.Draw(c)
    txt=[]
    for k,it in enumerate(chunk):
        im=Image.open(it['path']).convert('RGBA')
        sc=144//im.width; im=im.resize((im.width*sc,im.height*sc),Image.NEAREST)
        x=(k%COLS)*CELL+12; y=(k//COLS)*(CELL+18)
        dr.rectangle([x-2,y,x+146,y+16],fill=(0,0,0)); dr.text((x+2,y+2),f"#{it['id']}",fill=(255,255,0))
        bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im)
        c.paste(bg.convert('RGB'),(x,y+18))
        txt.append(f"{it['id']}\t{it['grid']}x{it['grid']}\t{it['name']}")
    c.save(f"{S}/pages/p{n:03d}.png"); open(f"{S}/pages/p{n:03d}.txt",'w',encoding='utf-8').write('\n'.join(txt))
print(len(items), (len(items)+PER-1)//PER)
