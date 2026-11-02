// Regression checks on the real renderers and data. No browser or visual assertions.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.dataset={};this.style={};this.value='';this.classList={add(){},remove(){}};this._text='';}
 set textContent(v){this._text=String(v);}get textContent(){return this._text;}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;}setAttribute(k,v){this.attrs[k]=v;}addEventListener(k,v){this.listeners[k]=v;}
 querySelectorAll(tag){let all=[];for(const c of this.children)if(c instanceof Element){if(c.tag===tag)all.push(c);all.push(...c.querySelectorAll(tag));}return all;}
 pause(){this.paused=true;}
}
const context={window:{},Node:Element,URL,matchMedia:()=>({matches:false}),location:{origin:'null'},document:{currentScript:{src:'file://'+root+'/assets/report-reader/reader.js'},createElement:t=>new Element(t),createTextNode:t=>{const n=new Element('#text');n.textContent=t;return n;},querySelectorAll:()=>[],addEventListener(){},body:new Element('body')}};
vm.createContext(context);
function run(file){vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);}
run('assets/report-reader/manifest.js');for(const file of fs.readdirSync(path.join(root,'assets/report-reader/data')))run('assets/report-reader/data/'+file);
run('assets/report-reader/insights.js');run('assets/evidence/evidence.js');
let source=fs.readFileSync(path.join(root,'assets/report-reader/reader.js'),'utf8');source=source.replace('const standalone=document.body.dataset.readerPage;', 'window.ReaderTest={renderContent,readingURL,link}; const standalone=document.body.dataset.readerPage;');vm.runInContext(source,context);
const {renderContent,readingURL,link}=context.window.ReaderTest,manifest=context.window.ReportReaderManifest;
let routes=0;for(const [id,m]of Object.entries(manifest)){
 if(m.original&&/\.(json|ya?ml|md)$/.test(m.original)){
   const href=readingURL(m.original);assert(href.endsWith('.html'),id);assert(link('Ir',m.original,true).href.endsWith('.html'),id+' bypass');routes++;
 }
}
assert(readingURL('../datos/sesiones/T2-arturo-1.json').endsWith('/lecturas/T2-arturo-1.html'));
function collect(node){return [node,...node.children.flatMap(n=>n instanceof Element?collect(n):[])];}
let rendered=0;for(const id of [...Object.keys(manifest).filter(id=>manifest[id].kind==='session'),'sintesis','auditoria','tecnico']){
 const view=renderContent(id,context.window.ReportReaderData[id]);const nodes=collect(view);assert(!nodes.some(n=>n.textContent.includes('[object Object]')),id+' object text');assert(!nodes.some(n=>n.tag==='a'&&/\.(json|ya?ml|md)(?:[#?]|$)/.test(n.href)),id+' raw link');assert(nodes.some(n=>n.tag==='h3'),id+' no headings');rendered++;
 if(id==='auditoria'){const input=nodes.find(n=>n.tag==='input');input.value='incodeUbicacion';input.listeners.input();assert(collect(view).some(n=>n.tag==='summary'&&n.textContent.includes('incodeUbicacion')));input.value='impossible-no-match';input.listeners.input();assert(collect(view).some(n=>n.textContent.includes('No hay coincidencias')));}
}
assert(!source.includes('Abrir fuente original'));assert(!source.includes('url(m.original),true'));
console.log(JSON.stringify({sourceRoutesCovered:routes,structuredPagesRendered:rendered,arturoRoute:'styled HTML',rawDocumentAnchors:0,auditSearch:'passed',visualVerification:'not performed'},null,2));
