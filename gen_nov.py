import json,re,sys
docx=open(sys.argv[1]).read().split('\n'); shas=dict(l.split('\t')[:2] for l in open(sys.argv[2]).read().strip().split('\n'))
cap={}; cur=None
for line in docx:
    m=re.match(r'^(\d{2})/11\s*-?\s*$',line.strip())
    if m: cur=m.group(1); cap[cur]=[]; continue
    cap[cur].append(line.rstrip())
# correções combinadas
first12=cap['11'].pop()            # linha do 12/11 que caiu no bloco do 11 (confirmado no pptx)
assert first12.startswith('Se o truque'); cap['12'].insert(0,first12)
del cap['11']                       # limpeza a seco: NUNCA publicar
cap['06']=[l.replace('Ammidonage','Amidonnage') for l in cap['06']]
cap['02']=[l.replace('App, Delivery, Lockers ou','App, Delivery ou') for l in cap['02']]
C={k:'\n'.join(l.strip() for l in v if l.strip()) for k,v in cap.items()}
def n(d,kind,k): return [f'{d}_{kind}.png'] if k==1 else [f'{d}_{kind}_{i}.png' for i in range(1,k+1)]
S=[]
def story(d,k=1): S.append({'date':f'{d}/11','type':'story','assets':n(d,'story',k),'caption':'','slot':'story'})
def feed(d,k=1,post_date=None,src=None):
    S.append({'date':f'{post_date or d}/11','type':'feed' if k==1 else 'carousel','assets':n(d,'feed',k),'caption':C[src or d],'slot':'feed'})
def reel(d,cover): S.append({'date':f'{d}/11','type':'reel','assets':[f'{d}_reel.mp4'],'cover':cover,'caption':C[d],'slot':'reels'})
reel('05','05_capa.jpg')
story('06',7); feed('06',7)
story('07'); feed('07')
feed('01',post_date='08')            # atrasado 01/11 -> 08/11
reel('09','09_capa.jpg')
story('10'); feed('10')
story('12',3); feed('12',3)
story('13')
story('14'); feed('14')
story('15'); feed('15')
feed('02',post_date='16')            # atrasado 02/11 -> 16/11
story('17'); feed('17')
story('18',2); feed('18',2)
story('19',4); feed('19',4)
story('20',4); feed('20',4)
story('21'); feed('21')
feed('03',post_date='22')            # atrasado 03/11 -> 22/11
story('23'); feed('23')
story('24'); feed('24')
story('25',6); feed('25',6)
reel('26',None)
reel('27','27_capa.jpg')
story('28'); feed('28')
feed('04',post_date='29')            # atrasado 04/11 -> 29/11
story('30'); feed('30')
for e in S:
    for a in e['assets']+([e['cover']] if e.get('cover') else []): assert a[:2] in shas, a
json.dump(S,open(sys.argv[3],'w'),ensure_ascii=False,indent=1)
js='const JSD="https://cdn.jsdelivr.net/gh/guilhermemarquesia/5asec-midia-novembro";\n'
js+='const PAGES="https://guilhermemarquesia.github.io/5asec-midia-novembro";\n'
js+='// commit isolado por dia (branch dia-DD, < 50MB) -> evita o 403 "Package size exceeded 50 MB" do jsDelivr\n'
js+='const DAY_SHA='+json.dumps({k:v for k,v in shas.items()})+';\n'
js+='const SCHEDULE='+json.dumps(S,ensure_ascii=False)+';\n'
js+=r'''const url=a=>`${JSD}@${DAY_SHA[a.slice(0,2)]}/${a}`; const alt=a=>`${PAGES}/${a}`;
const p=Object.fromEntries(new Intl.DateTimeFormat("en-CA",{timeZone:"America/Sao_Paulo",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",hour12:false}).formatToParts(new Date()).map(x=>[x.type,x.value]));
const today=`${p.day}/${p.month}`; const hour=parseInt(p.hour,10);
const slot=hour<11?"story":(hour<16?"feed":"reels");
const due=SCHEDULE.filter(x=>x.date===today&&x.slot===slot);
const out=[];
for(const post of due){
  const all=[...post.assets,...(post.cover?[post.cover]:[])];
  const altMap=Object.fromEntries(all.map(a=>[url(a),alt(a)]));
  if(post.type==="feed") out.push({json:{type:"feed",caption:post.caption,image_url:url(post.assets[0]),alt:altMap}});
  else if(post.type==="carousel") out.push({json:{type:"carousel",caption:post.caption,assetsUrls:post.assets.map(url),alt:altMap}});
  else if(post.type==="reel") out.push({json:{type:"reel",caption:post.caption,video_url:url(post.assets[0]),...(post.cover?{cover_url:url(post.cover)}:{}),alt:altMap}});
  else if(post.type==="story") out.push({json:{type:"story",frames:post.assets.map(a=>({url:url(a),field:a.toLowerCase().endsWith(".mp4")?"video_url":"image_url"})),alt:altMap}});
}
return out;
'''
open(sys.argv[4],'w').write(js)
print(len(S),'entradas'); 
