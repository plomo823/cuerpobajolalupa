from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
pages=list(root.glob('*.html'))+list((root/'guias').glob('*.html'))
class Parser(HTMLParser):
 def __init__(self): super().__init__(); self.ids=set(); self.links=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.add(a['id'])
  for k in ('href','src'):
   if k in a:self.links.append(a[k])
parsed={}
for p in pages:
 s=p.read_text(encoding='utf-8'); q=Parser();q.feed(s);parsed[p]=q
 for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):json.loads(x)
 assert 'index,follow' in s,p
 assert s.count('adsbygoogle.js')==(0 if p.name=='herramientas.html' else 1),p
errors=[]
for p,q in parsed.items():
 for link in q.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  if not u.path: target=p
  else:target=(root/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path).resolve()
  if target.is_dir(): target=target/'index.html'
  if not target.exists():errors.append((str(p.relative_to(root)),link,'missing'))
  elif u.fragment and target in parsed and unquote(u.fragment) not in parsed[target].ids:errors.append((str(p.relative_to(root)),link,'anchor'))
sm=ET.parse(root/'sitemap.xml')
for p in pages:
 url='https://cuerpobajolalupa.es/'+str(p.relative_to(root)).replace(chr(92),'/').replace('index.html','')
 if not any(e.text==url for e in sm.iter() if e.tag.endswith('}loc')):errors.append((str(p.relative_to(root)),url,'sitemap'))
print('Pages:',len(pages),'errors:',errors)
assert not errors
