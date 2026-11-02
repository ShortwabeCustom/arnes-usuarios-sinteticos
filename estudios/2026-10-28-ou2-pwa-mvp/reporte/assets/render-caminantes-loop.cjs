/* Render the report hero as a deterministic, seamless, silent 48 fps video.
   Run with NODE_PATH pointing to the bundled workspace node_modules. */
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const W = 1280;
const H = 720;
const FPS = 48;
const SECONDS = 10;
const FRAMES = FPS * SECONDS;
const base = __dirname;
const backgroundPath = path.join(base, 'plaza-caminantes.png');
const posterPath = path.join(base, 'caminantes-poster.jpg');
const videoPath = path.join(base, 'caminantes-loop.mp4');
const posterOnly = process.argv.includes('--poster-only');

const people = [
  { offset: .02, direction: 1, route: 0, scale: .76, jacket: '#d7e1f6', pants: '#36528d', hair: '#23366b', skin: '#b66f52', bag: '#637b9d', kind: 'bun' },
  { offset: .43, direction: -1, route: 0, scale: .72, jacket: '#e5b18a', pants: '#354c76', hair: '#28335e', skin: '#d49a73', bag: '#789897', kind: 'short' },
  { offset: .81, direction: 1, route: 0, scale: .69, jacket: '#a4b9d9', pants: '#2f457e', hair: '#493a42', skin: '#8a543d', bag: '#e3bb82', kind: 'curly' },
  { offset: .15, direction: -1, route: 1, scale: .91, jacket: '#aabfbd', pants: '#263f78', hair: '#243054', skin: '#ce8e67', bag: '#d59768', kind: 'long' },
  { offset: .55, direction: 1, route: 1, scale: .96, jacket: '#d99c78', pants: '#243d75', hair: '#29386e', skin: '#a8664b', bag: '#acc7b4', kind: 'short' },
  { offset: .89, direction: -1, route: 1, scale: .89, jacket: '#c1cbee', pants: '#344f8e', hair: '#2a3060', skin: '#d1a47f', bag: '#9bbaac', kind: 'bun' },
  { offset: .08, direction: 1, route: 2, scale: 1.13, jacket: '#7898b9', pants: '#243568', hair: '#463444', skin: '#ad6a51', bag: '#d39b75', kind: 'curly' },
  { offset: .49, direction: -1, route: 2, scale: 1.1, jacket: '#e2b79b', pants: '#2e4a82', hair: '#2b365a', skin: '#c78d6e', bag: '#98b7aa', kind: 'long' },
  { offset: .77, direction: 1, route: 2, scale: 1.07, jacket: '#c6d0e8', pants: '#3d598e', hair: '#343153', skin: '#9b5a41', bag: '#bd977c', kind: 'short' },
];

function hair(kind, color) {
  const common = `fill="${color}" stroke="#253972" stroke-width="2.2"`;
  if (kind === 'bun') return `<path d="M-13-91 Q-16-112 2-113 Q18-111 19-91 Q12-102 1-100 Q-6-93-13-91Z" ${common}/><circle cx="-12" cy="-110" r="8" ${common}/>`;
  if (kind === 'long') return `<path d="M-13-88 Q-19-111-1-113 Q19-112 19-91 L24-58 Q7-62 8-84 Q-7-97-13-88Z" ${common}/>`;
  if (kind === 'curly') return `<path d="M-16-89 Q-19-105-12-109 Q-13-120-3-116 Q3-124 10-115 Q21-115 19-104 Q25-96 16-89 Q8-102-4-98 Q-12-93-16-89Z" ${common}/><circle cx="-15" cy="-102" r="5" ${common}/>`;
  return `<path d="M-14-89 Q-16-111-2-113 Q14-116 19-99 L16-91 Q8-101-3-99 Q-9-91-14-89Z" ${common}/>`;
}

function personMarkup(p, t) {
  const span = 1540;
  const phaseX = (p.offset + t / SECONDS) % 1;
  const x = p.direction === 1 ? -130 + span * phaseX : 1410 - span * phaseX;
  const y = p.route === 0 ? 292 + .02*x : p.route === 1 ? 438 + .012*x : 578 - .008*x;
  const phase = 2 * Math.PI * (16 * t / SECONDS + p.offset * 3);
  const leg = Math.sin(phase) * 23;
  const arm = Math.sin(phase) * 11;
  const bob = 2.4 * Math.cos(2 * phase);
  const sway = Math.sin(phase) * 1.8;
  const flip = p.direction === 1 ? 1 : -1;
  const perspective = .74 + Math.max(0,Math.min(H,y))/1100;
  const scale = p.scale * perspective;
  const dark = '#233a83';
  const jacket = p.jacket;
  const pants = p.pants;
  const skin = p.skin;
  const bag = p.bag;
  const coatTail = p.kind === 'long' || p.kind === 'bun' ? `<path d="M-18-28 L-25 20 Q-3 29 19 18 L14-29Z" fill="${jacket}" stroke="${dark}" stroke-width="2.5"/><path d="M-15-19 L-19 12" fill="none" stroke="#7c92bb" stroke-width="2"/>` : '';
  return `<g transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${(flip * scale).toFixed(3)} ${scale.toFixed(3)})">
    <ellipse cx="0" cy="79" rx="39" ry="7" fill="#273d72" opacity=".17"/>
    <g transform="translate(0 ${bob.toFixed(2)})" stroke-linecap="round" stroke-linejoin="round">
      <g transform="rotate(${(-leg).toFixed(2)} -7 0)"><path d="M-7 0 Q-10 34-16 70" fill="none" stroke="${dark}" stroke-width="18"/><path d="M-7 1 Q-12 35-16 69" fill="none" stroke="${pants}" stroke-width="13"/><path d="M-17 69 Q-10 76 9 73" fill="#fcfcf8" stroke="${dark}" stroke-width="3"/></g>
      <g transform="rotate(${leg.toFixed(2)} 7 0)"><path d="M7 0 Q10 31 15 69" fill="none" stroke="${dark}" stroke-width="18"/><path d="M7 1 Q10 35 15 69" fill="none" stroke="${pants}" stroke-width="13"/><path d="M14 69 Q24 76 36 72" fill="#fcfcf8" stroke="${dark}" stroke-width="3"/></g>
      <g transform="rotate(${(-arm).toFixed(2)} -17 -53)"><path d="M-17-52 Q-29-35-27-12" fill="none" stroke="${dark}" stroke-width="15"/><path d="M-17-52 Q-29-35-27-12" fill="none" stroke="${jacket}" stroke-width="11"/><circle cx="-27" cy="-11" r="5" fill="${skin}" stroke="${dark}" stroke-width="2"/></g>
      <path d="M-18-49 Q-29-48-31-29 L-29-7 Q-19-3-15-14Z" fill="${bag}" stroke="${dark}" stroke-width="2.6"/><path d="M-27-47 Q-31-56-17-61" fill="none" stroke="${dark}" stroke-width="3"/>
      <g transform="rotate(${sway.toFixed(2)} 0 -36)">${coatTail}<path d="M-16-64 Q-1-72 15-63 L19-44 L14 2 Q-1 10-16 1 L-21-43Z" fill="${jacket}" stroke="${dark}" stroke-width="2.8"/><path d="M-4-64 L0-49 L4-64 M-15-58 L-4-40 L-1-56 M14-57 L5-40 L2-56" fill="none" stroke="${dark}" stroke-width="1.7"/><path d="M-8-28 L-7-5 M9-27 L9-5" fill="none" stroke="#8296b6" stroke-width="1.5"/>
      <path d="M15-54 Q27-45 26-29 L28-24" fill="none" stroke="${dark}" stroke-width="15"/><path d="M15-54 Q27-45 26-29 L28-24" fill="none" stroke="${jacket}" stroke-width="10"/><circle cx="28" cy="-23" r="5" fill="${skin}" stroke="${dark}" stroke-width="2"/>
      <rect x="24" y="-53" width="13" height="24" rx="2.5" transform="rotate(-12 30 -41)" fill="${dark}" stroke="#172a65" stroke-width="1.5"/><path d="M28-48 L33-49" fill="none" stroke="#c8d7f5" stroke-width="1.6"/>
      <path d="M-4-70 L-4-77 M6-70 L7-78" fill="none" stroke="${skin}" stroke-width="8"/><circle cx="2" cy="-91" r="17" fill="${skin}" stroke="${dark}" stroke-width="2.6"/><path d="M16-89 L21-85 L16-83" fill="${skin}" stroke="${dark}" stroke-width="2"/><circle cx="10" cy="-92" r="1.3" fill="${dark}"/>${hair(p.kind,p.hair)}</g>
    </g>
  </g>`;
}

function overlaySvg(t) {
  const back = people.filter(p => p.route === 0).map(p => personMarkup(p,t)).join('');
  const middle = people.filter(p => p.route === 1).map(p => personMarkup(p,t)).join('');
  const front = people.filter(p => p.route === 2).map(p => personMarkup(p,t)).join('');
  const pulse = .45 + .18 * Math.sin(2*Math.PI*t/SECONDS);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <defs><linearGradient id="edge" x1="0" x2="1"><stop stop-color="#fbfaf6" stop-opacity=".72"/><stop offset=".13" stop-color="#fbfaf6" stop-opacity="0"/><stop offset=".87" stop-color="#fbfaf6" stop-opacity="0"/><stop offset="1" stop-color="#fbfaf6" stop-opacity=".72"/></linearGradient></defs>
    <path d="M-10 291 L1290 317" fill="none" stroke="#4869b1" stroke-width="2" stroke-dasharray="3 18" opacity=".28"/>
    <path d="M-10 438 L1290 453" fill="none" stroke="#4869b1" stroke-width="2" stroke-dasharray="3 18" opacity=".28"/>
    <path d="M-10 578 L1290 568" fill="none" stroke="#4869b1" stroke-width="2" stroke-dasharray="3 18" opacity=".28"/>
    <circle cx="640" cy="446" r="10" fill="#fff" stroke="#496ab7" stroke-width="2" opacity="${pulse.toFixed(2)}"/><circle cx="640" cy="446" r="3" fill="#3155bb" opacity=".6"/>
    ${back}${middle}${front}<rect width="${W}" height="${H}" fill="url(#edge)" pointer-events="none"/>
  </svg>`;
}

async function frame(t, bgRaw) {
  const svg = Buffer.from(overlaySvg(t));
  return sharp(bgRaw, { raw: {width:W,height:H,channels:4} }).composite([{ input: svg, top:0, left:0 }]).raw().toBuffer();
}

async function main() {
  if (!fs.existsSync(backgroundPath)) throw new Error(`Missing ${backgroundPath}`);
  const bgRaw = await sharp(backgroundPath).resize(W,H,{fit:'cover'}).ensureAlpha().raw().toBuffer();
  const first = await frame(0,bgRaw);
  await sharp(first,{raw:{width:W,height:H,channels:4}}).jpeg({quality:88,mozjpeg:true}).toFile(posterPath);
  console.log(`Poster: ${posterPath}`);
  if (posterOnly) return;
  const ff = spawn('ffmpeg',['-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s',`${W}x${H}`,'-r',`${FPS}`,'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',videoPath],{stdio:['pipe','inherit','inherit']});
  const done = new Promise((resolve,reject)=>{ff.once('error',reject);ff.once('close',code=>code===0?resolve():reject(new Error(`ffmpeg exited ${code}`)));});
  for(let i=0;i<FRAMES;i++) {
    const raw = i===0 ? first : await frame(i/FPS,bgRaw);
    if(!ff.stdin.write(raw)) await new Promise(resolve=>ff.stdin.once('drain',resolve));
    if(i%96===0) console.log(`${Math.round(100*i/FRAMES)}%`);
  }
  ff.stdin.end();
  await done;
  console.log(`Video: ${videoPath}`);
}

main().catch(error=>{console.error(error);process.exitCode=1;});
