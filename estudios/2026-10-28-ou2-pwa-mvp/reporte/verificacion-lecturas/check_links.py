"""Check reader entry points for raw-document exits, including noscript links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
ROOT=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('src','href') and value:self.refs.append((tag,key,value))
count=0;raw=[]
pages=list(ROOT.glob('*.html'))+list((ROOT/'lecturas').glob('*.html'))
for page in pages:
    parser=Links();parser.feed(page.read_text())
    for tag,key,href in parser.refs:
        path=urlsplit(href)
        if tag=='a' and Path(path.path).suffix.lower() in ('.json','.yaml','.yml','.md'):raw.append([page.name,href])
        if not path.scheme and path.path:
            assert (page.parent/unquote(path.path)).exists(),(page.name,href)
            count+=1
assert not raw,raw
main=ROOT/'oupwa-pdu-originacion-unica-2-0-pwa-sintetico_2026-10-28-v1.html'
assert main.read_bytes()==(ROOT/'fuente-editorial.html').read_bytes()
print(json.dumps({'html_pages_checked':len(pages),'local_resources_and_links':count,'raw_document_links':raw,'source_delivery_identical':True},ensure_ascii=False,indent=2))
