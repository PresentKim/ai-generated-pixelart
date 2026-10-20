"""Split sheets into 16x16 tiles, remove the white background, save as <out>/<name>-NNNN.png.
Run from anywhere: python tools/split.py <work_dir> <repo_root> <out_dir> [test]
Needs <work_dir>/manifest.json (tools/manifest.py) and <work_dir>/names/*.json ({"id": "name"}).
`test` mode splits the first 40 sheets with dummy names so the background removal can be eyeballed."""
import os,sys,json,re,subprocess,collections
from PIL import Image
def bgfill(t):
    px=t.load();w,h=t.size
    white=lambda p:p[3]>0 and min(p[:3])>=235
    st=[(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)]
    seen=set();bg=set()
    while st:
        x,y=st.pop()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y))
        if not white(px[x,y]):continue
        bg.add(px[x,y][:3]);px[x,y]=(0,0,0,0)
        st+= [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    holes(t,white,bg)
    return t
MATCH,RATIO,DARK=0,0.6,450
N4=((1,0),(-1,0),(0,1),(0,-1))
def holes(t,white,bg):
    # enclosed white regions (bow interior, key ring, wrench jaw) are background when they are
    # walled by the same outline colors that border the outer background; highlights are walled by fill colors
    px=t.load();w,h=t.size
    inb=lambda x,y:0<=x<w and 0<=y<h
    outline=set()
    for y in range(h):
        for x in range(w):
            if px[x,y][3] and any(inb(x+dx,y+dy) and px[x+dx,y+dy][3]==0 for dx,dy in N4): outline.add(px[x,y][:3])
    if not outline: return
    near=lambda c:any(sum(abs(a-b) for a,b in zip(c,o))<=60 for o in outline)
    seen=set()
    for y in range(h):
        for x in range(w):
            if (x,y) in seen or not white(px[x,y]): continue
            comp=[];st=[(x,y)];wall=set()
            while st:
                a,b=st.pop()
                if (a,b) in seen: continue
                if not white(px[a,b]): wall.add((a,b)); continue
                seen.add((a,b));comp.append((a,b))
                st+=[(a+dx,b+dy) for dx,dy in N4 if inb(a+dx,b+dy)]
            if len(comp)<3 or not wall: continue
            # the sheet background is one flat color; drawn whites (eye, glass) are noisy and don't match it
            if sum(1 for q in comp if px[q][:3] in bg)/len(comp)<MATCH: continue
            if sum(1 for q in wall if near(px[q][:3]) and sum(px[q][:3])<=DARK)/len(wall)>=RATIO:
                for q in comp: px[q]=(0,0,0,0)
def save(t,path):
    cols=t.getcolors(256)
    if cols is not None and len(cols)<=255:
        # palette mode with index 0 transparent, like main
        pal=[(0,0,0,0)]+[c for _,c in cols if c[3]!=0]
        if all(c[3] in (0,255) for c in pal):
            p=Image.new('P',t.size);idx={c:i for i,c in enumerate(pal)}
            p.putpalette([v for c in pal for v in c[:3]])
            p.putdata([0 if c[3]==0 else idx[c] for c in t.get_flattened_data()])
            p.save(path,transparency=0,optimize=True);return
    t.save(path,optimize=True)
if __name__=='__main__':
    S,REPO,OUT=sys.argv[1],sys.argv[2],sys.argv[3]

    TEST=len(sys.argv)>4
    items=json.load(open(S+'/manifest.json',encoding='utf-8'))
    names={}
    if not TEST:
        for f in os.listdir(S+'/names'):
            if f.endswith('.json'): names.update({int(k):v for k,v in json.load(open(S+'/names/'+f,encoding='utf-8')).items()})
    # continue numbering after files already on main
    used=collections.defaultdict(int)
    for line in subprocess.run(['git','-C',REPO,'ls-tree','--name-only','main'],capture_output=True,text=True,encoding='utf-8').stdout.splitlines():
        m=re.match(r'(.+)-(\d{4})\.png$',line)
        if m: used[m.group(1)]=max(used[m.group(1)],int(m.group(2)))
    os.makedirs(OUT,exist_ok=True)
    log=[];missing=[]
    for it in (items[:40] if TEST else items):
        name=f"test_{it['id']}" if TEST else names.get(it['id'])
        if not name or not re.fullmatch(r'[a-z0-9_]+',name): missing.append((it['id'],name));continue
        im=Image.open(os.path.join(REPO,it['path'])).convert('RGBA')
        g=it['grid']
        for r in range(g):
            for c in range(g):
                t=bgfill(im.crop((c*16,r*16,c*16+16,r*16+16)))
                if t.getbbox() is None: continue
                used[name]+=1
                fn=f"{name}-{used[name]:04d}.png"
                save(t,os.path.join(OUT,fn)); log.append(f"{it['path']}\t{r*g+c+1}\t{fn}")
    open(S+'/split_log.tsv','w',encoding='utf-8').write('\n'.join(log))
    print('tiles',len(log),'missing',len(missing),missing[:20])
