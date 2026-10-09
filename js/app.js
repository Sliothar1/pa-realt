/* PA Réalt · main script. Real data only: SMR (NMS), townland names (Tailte Éireann),
   horizons (Copernicus GLO-30), stars (d3-celestial/Hipparcos), Newgrange observations (NMS 2024). */
(function(){
'use strict';
const C=window.PA_CONFIG, A=window.PAAstro, D=Math.PI/180, $=s=>document.querySelector(s);
const TZ='Europe/Dublin';
const GCOL={pt:'#f3c46b',ct:'#e2805f',po:'#f2a7a0',wt:'#d8935a',mu:'#c7a27f',sc:'#f7ecd6',sr:'#c3b2ee',sp:'#9fbbe4',he:'#ead78c',cu:'#cfd7a6',bb:'#d9b4c9',ss:'#a08672'};
let SITES=null, META=null, HOR=null, SKY=null, NG=null, map=null, layer=null, rayLayer=null, featLayer=null, selected=null, era=-3199, active=new Set(Object.keys(GCOL).filter(g=>g!=='ss')), standing=null;

/* ---------- config: one spot for the name ---------- */
document.querySelectorAll('[data-cfg]').forEach(el=>{const v=C[el.getAttribute('data-cfg')];if(v)el.textContent=v;});
document.title=`${C.name} · ${C.subtitle} · ${C.author}`;
$('#lnkResearch').href=C.repo+'/blob/main/RESEARCH.md';$('#lnkPrereg').href=C.repo+'/blob/main/prereg/tests_v1.json';
/* theme */
$('#themeBtn').addEventListener('click',()=>{const d=document.documentElement,t=d.getAttribute('data-theme')==='dawn'?'night':'dawn';d.setAttribute('data-theme',t);try{localStorage.setItem('pa-realt-theme',t)}catch(e){}});
/* toast */
let tt;function toast(html,ms){const t=$('#toast');t.innerHTML=html;t.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>t.classList.remove('show'),ms||5200);}
/* family strip */
$('#paFamily').innerHTML=`<svg class="pa-mark" aria-hidden="true"><use href="#i-pa"/></svg><span><i lang="ga">Teaghlach PA</i> · The PA family</span>`+C.family.map(f=>`<a href="${f.url}" ${f.self?'aria-current="page"':''}><svg aria-hidden="true"><use href="#i-${f.icon==='dolphin'?'dolphin':'realt'}" stroke-width="${f.icon==='dolphin'?2.6:2.6}"/></svg>${f.name}</a>`).join('');
/* reveal */
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.08});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
/* spiral gem */
$('#m1').addEventListener('click',()=>toast('Stone C10 at Newgrange is a <i>three-spiral</i> stone, “often wrongly called a triple spiral” (NMS 2024 report, note 12). This line art is original.'));

const fmtT=(d)=>d?new Intl.DateTimeFormat('en-IE',{timeZone:TZ,hour:'2-digit',minute:'2-digit'}).format(d):'—';
const fmtD=(d)=>new Intl.DateTimeFormat('en-IE',{timeZone:TZ,weekday:'short',day:'numeric',month:'short',year:'numeric'}).format(d);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

Promise.all(['data/sites.json','data/horizons.json','data/sky.json','data/newgrange_obs.json'].map(u=>fetch(u).then(r=>r.json()))).then(([s,h,k,n])=>{
  SITES=s.sites;META=s.meta;HOR=h;SKY=k;NG=n;
  drawSkyline();heroSky();initMap();initNG();initDome();renderToday();renderClaims();renderSources();
  window.addEventListener('resize',()=>{drawSkyline();heroSky();drawNG();drawDome();});
}).catch(e=>{console.error(e);$('#card').innerHTML='<p class="empty">Could not load data.</p>';});

/* ---------- hero: real horizon skyline + real pre-dawn stars over Newgrange ---------- */
function drawSkyline(){
  const p=HOR.newgrange.alt,svg=$('#skyline'),a0=60,a1=240,ex=25,base=62,Wd=Math.max(320,svg.clientWidth||1000);svg.setAttribute('viewBox',`0 0 ${Wd} 70`);svg.setAttribute('preserveAspectRatio','none');
  const X=az=>(az-a0)/(a1-a0)*Wd,Y=alt=>base-alt*ex;
  let d=`M0 70 L0 ${Y(A.horAt(p,a0)).toFixed(1)}`;
  for(let az=a0;az<=a1;az+=0.5)d+=` L${X(az).toFixed(1)} ${Y(A.horAt(p,az)).toFixed(1)}`;
  d+=` L${Wd} 70 Z`;
  const ev=A.events(HOR.newgrange.lat,p,-3199),ws=ev.find(e=>e.k==='WS rise').az,eq=ev.find(e=>e.k==='EQ rise').az;
  svg.innerHTML=`<path class="land" d="${d}"/>`+[[ws,'grianstad'],[eq,'cónocht']].map(([az,l])=>`<line class="tick" x1="${X(az)}" x2="${X(az)}" y1="${Y(A.horAt(p,az))-2}" y2="${Y(A.horAt(p,az))-16}"/><text x="${X(az)+4}" y="${Y(A.horAt(p,az))-10}" lang="ga">${l}</text>`).join('');
}
function altaz(raDeg,decDeg,lstDeg,lat){const H=(lstDeg-raDeg)*D,d=decDeg*D,p=lat*D;const sa=Math.sin(p)*Math.sin(d)+Math.cos(p)*Math.cos(d)*Math.cos(H);const alt=Math.asin(sa);const az=Math.atan2(-Math.sin(H)*Math.cos(d),Math.cos(p)*Math.sin(d)-Math.sin(p)*Math.cos(d)*Math.cos(H));return [alt/D,((az/D)+360)%360];}
function lstDeg(date,lon){return ((Astronomy.SiderealTime(date)*15+lon)%360+360)%360;}
function bvColor(bv){const t=Math.max(-.3,Math.min(2,bv));if(t<0.3)return [214,226,255];if(t<0.6)return [255,246,226];if(t<1.0)return [255,226,178];return [255,196,140];}
function heroSky(){
  const cv=$('#heroSky'),r=cv.getBoundingClientRect(),dpr=Math.min(2,window.devicePixelRatio||1);cv.width=r.width*dpr;cv.height=r.height*dpr;
  const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,r.width,r.height);
  const date=new Date(Date.UTC(2026,11,21,7,10)),lat=C.home.lat,lst=lstDeg(date,C.home.lon); // pre-dawn, winter solstice 2026
  const a0=60,a1=240,H=r.height-70;
  for(const s of SKY.stars){const [alt,az]=altaz(s[0],s[1],lst,lat);if(alt<0||az<a0||az>a1)continue;const x=(az-a0)/(a1-a0)*r.width,y=H-(alt/55)*H;if(y<0)continue;const m=s[2],rad=Math.max(.35,1.9-m*.32),c=bvColor(s[3]);g.fillStyle=`rgba(${c[0]},${c[1]},${c[2]},${Math.min(1,.95-m*.12)})`;g.beginPath();g.arc(x,y,rad,0,7);g.fill();}
  const sun=Astronomy.Equator('Sun',date,new Astronomy.Observer(lat,C.home.lon,C.home.elev),true,true);const [sa,saz]=altaz(sun.ra*15,sun.dec,lst,lat);
  const sx=(saz-a0)/(a1-a0)*r.width,gr=g.createRadialGradient(sx,H+10,0,sx,H+10,r.width*.35);gr.addColorStop(0,'rgba(243,200,120,.35)');gr.addColorStop(1,'rgba(243,200,120,0)');g.fillStyle=gr;g.fillRect(0,0,r.width,r.height);
  cv.title='Real stars over Newgrange’s south-eastern sky before dawn on the winter solstice, 21 Dec 2026, 07:10 GMT';
}

/* ---------- map ---------- */
function initMap(){
  map=L.map('map',{preferCanvas:true,zoomControl:true,minZoom:6,maxZoom:17,worldCopyJump:false}).setView([53.45,-7.9],innerWidth<600?6:7);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'Monuments: <a href="https://data.gov.ie/dataset/national-monuments-service-archaeological-survey-of-ireland">National Monuments Service SMR</a> (CC BY 4.0) · <a href="https://www.data.gov.uk/dataset/46240fa5-db15-469e-b1c8-0460504b951c/northern-ireland-sites-and-monuments-record">NI SMR</a> (OGL v3) · Irish townland names: Tailte Éireann · Map © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
  layer=L.layerGroup().addTo(map);rayLayer=L.layerGroup().addTo(map);featLayer=L.layerGroup().addTo(map);
  renderChips();drawSites();drawFeatured();
  map.on('zoomend',()=>{if(selected)drawRays(selected);drawSites();});
  $('#eraOld').onclick=()=>setEra(-3199);$('#eraNow').onclick=()=>setEra(new Date().getFullYear());
  const q=$('#q');q.addEventListener('keydown',e=>{if(e.key==='Enter'){const v=q.value.trim().toUpperCase();if(!v)return;const all=SITES.concat(standing||[]);const hit=all.find(s=>s[0].toUpperCase().startsWith(v))||all.find(s=>(s[4]||'').toUpperCase().startsWith(v))||all.find(s=>(s[5]||'').toUpperCase().startsWith(v))||all.find(s=>META.counties[s[6]].startsWith(v));if(hit){map.flyTo([hit[2],hit[3]],13);select(hit);}else toast('No monument found for “'+esc(q.value)+'”.');}});
  const m=/site=([^&]+)/.exec(location.hash),mz=/[&?]z=(\d+)/.exec(location.hash);if(m){const s=SITES.find(x=>x[0]===decodeURIComponent(m[1]));if(s){if(!mz)map.setView([s[2],s[3]],12);select(s);}}
}
function setEra(y){era=y;$('#eraOld').setAttribute('aria-pressed',y<0);$('#eraNow').setAttribute('aria-pressed',y>0);if(selected){drawRays(selected);renderCard(selected);}}
function renderChips(){
  const n={};SITES.forEach(s=>n[s[1]]=(n[s[1]]||0)+1);n.ss=META.n_standing;
  $('#chips').innerHTML=Object.keys(GCOL).map(g=>{const G=META.groups[g];return `<button class="chip" data-g="${g}" aria-pressed="${active.has(g)}" title="${esc(G.classes.join(', '))}"><i style="background:${GCOL[g]}"></i>${esc(G.en)}${G.ga?` <em lang="ga" style="font-family:var(--serif);color:var(--gold-soft)">${esc(G.ga)}</em>`:''} <span>${n[g].toLocaleString()}</span></button>`}).join('');
  $('#chips').querySelectorAll('.chip').forEach(b=>b.onclick=async()=>{const g=b.dataset.g;if(active.has(g))active.delete(g);else{active.add(g);if(g==='ss'&&!standing){b.disabled=true;standing=(await (await fetch('data/standing.json')).json()).sites;b.disabled=false;}}b.setAttribute('aria-pressed',active.has(g));drawSites();});
}
function drawSites(){
  if(!layer)return;layer.clearLayers();const z=map.getZoom(),r=z<8?2.6:z<10?3.6:z<13?5:6.5;
  const list=SITES.concat(active.has('ss')&&standing?standing:[]);
  for(const s of list){if(!active.has(s[1]))continue;const big=s[1]==='pt';
    const m=L.circleMarker([s[2],s[3]],{radius:big?r+1.2:r,color:'rgba(20,8,12,.8)',weight:.8,fillColor:GCOL[s[1]],fillOpacity:s[1]==='ss'?.7:.92});
    m.bindTooltip(()=>`<i lang="ga">${esc(s[5]||'')}</i>${s[5]?'<br>':''}${esc(clean(s[4]))} · ${esc(META.groups[s[1]].en.replace(/s$/,''))}`,{className:'tt',direction:'top',offset:[0,-4]});
    m.on('click',()=>select(s));layer.addLayer(m);}
}
function clean(t){return String(t||'').replace(/\s*\(.*$/,'');}
const starIcon=L.divIcon?null:null;
function drawFeatured(){
  const ic=L.divIcon({className:'',html:'<svg width="22" height="22" viewBox="0 0 24 24" style="filter:drop-shadow(0 0 5px rgba(243,200,120,.9))"><path d="M12 1.5 L14 10 L22.5 12 L14 14 L12 22.5 L10 14 L1.5 12 L10 10 Z" fill="#f3d79b" stroke="#5a1420" stroke-width="1"/></svg>',iconSize:[22,22],iconAnchor:[11,11]});
  for(const f of window.PA_FEATURED){const h=HOR[f.key];const mk=L.marker([h.lat,h.lon],{icon:ic,zIndexOffset:1000,keyboard:true,title:f.en});mk.bindTooltip(`<i lang="ga">${esc(f.ga)}</i>${f.ga?'<br>':''}<b>${esc(f.en)}</b>`,{className:'tt',direction:'top',offset:[0,-10]});
    mk.on('click',()=>{const s=SITES.find(x=>x[0]===f.smrs)||[f.smrs,'pt',h.lat,h.lon,f.en,f.ga,META.counties.indexOf('SLIGO'),0,0];select(s,f);});featLayer.addLayer(mk);}
}
function featuredFor(s){return window.PA_FEATURED.find(f=>f.smrs===s[0]);}
function select(s,f){selected=s;f=f||featuredFor(s);selected._f=f;drawRays(s);renderCard(s);try{history.replaceState(null,'','#site='+encodeURIComponent(s[0]));}catch(e){}}
function rayKm(){const c=map.getCenter(),z=map.getZoom();const mpp=156543.03*Math.cos(c.lat*D)/Math.pow(2,z);return Math.max(.4,Math.min(60,140*mpp/1000));}
function siteEvents(s){const f=s._f,h=f?HOR[f.key]:null;return {ev:A.events(h?h.lat:s[2],h?h.alt:null,era),dem:!!h};}
function drawRays(s,keepOld){
  if(!keepOld)rayLayer.clearLayers();const {ev}=siteEvents(s),km=rayKm(),f=s._f,h=f?HOR[f.key]:null,lat=h?h.lat:s[2],lon=h?h.lon:s[3];
  for(const e of ev){if(e.az==null)continue;const end=A.dest(lat,lon,e.az,km*(e.body==='moon'?.82:1));const sun=e.body==='sun';const hi=f&&f.events.includes(e.k);
    rayLayer.addLayer(L.polyline([[lat,lon],end],{color:sun?'#f3c46b':'#ddd6e8',weight:sun?(hi?9:7):5,opacity:sun?.16:.10,interactive:false}));
    rayLayer.addLayer(L.polyline([[lat,lon],end],{color:sun?(hi?'#fff1c9':'#f3c46b'):'#e6e0f0',weight:hi?2.6:1.5,opacity:.95,dashArray:sun?null:'4 5',interactive:false}));
    const lab=L.tooltip({permanent:true,direction:'center',className:'raylab'+(sun?'':' moon'),interactive:false}).setLatLng(A.dest(lat,lon,e.az,km*(e.body==='moon'?.62:1.1))).setContent(shortLab(e.k));rayLayer.addLayer(lab);}
  rayLayer.addLayer(L.circleMarker([lat,lon],{radius:9,color:'#f3d79b',weight:1.5,fill:false,interactive:false}));
}
function shortLab(k){return {'WS rise':'midwinter ↑','WS set':'midwinter ↓','SS rise':'midsummer ↑','SS set':'midsummer ↓','EQ rise':'equinox ↑','EQ set':'equinox ↓','MjN rise':'major ☾↑','MjN set':'major ☾↓','MjS rise':'major ☾↑','MjS set':'major ☾↓','MnN rise':'minor ☾↑','MnS set':'minor ☾↓'}[k]||k;}
const VLAB={strong:['v-strong','Strong'],observed:['v-obs','Observed'],debated:['v-deb','Debated'],proposed:['v-prop','Proposed'],not:['v-no','Not supported']};
function srcLinks(keys){return keys.map(k=>{const s=window.PA_SRC[k];return s[1]?`<a href="${s[1]}" target="_blank" rel="noopener">${esc(s[0].split('.')[0])}</a>`:esc(s[0].split('.')[0]);}).join(' · ');}
function renderCard(s){
  const f=s._f,G=META.groups[s[1]],cty=META.counties[s[6]]||'',ctyGa=META.counties_ga[s[6]]||'',{ev,dem}=siteEvents(s);
  const link=META.hev_link_prefix+encodeURIComponent(s[0]);
  let h='';
  if(f){h+=`<p class="sc-ga" lang="ga">${esc(f.ga||'')}</p><p class="sc-en">${esc(f.en)}</p><p class="note" style="margin:-4px 0 6px">${esc(f.place)}${f.gaNote?' · '+esc(f.gaNote):''}</p>`;}
  else{h+=s[5]?`<p class="sc-ga" lang="ga">${esc(s[5])}</p>`:'';h+=`<p class="sc-en">${esc(clean(s[4]))}</p>`;}
  h+=`<span class="sc-cls">${esc(G.en.replace(/s$/,'').replace(/tombs \(/,'tomb ('))}${G.ga?` · <em lang="ga">${esc(G.ga)}</em>`:''}</span>`;
  h+=`<dl class="kv"><dt>County</dt><dd>${esc(cty.toLowerCase().replace(/\b\w/g,c=>c.toUpperCase()))}${ctyGa?` · <i lang="ga">${esc(ctyGa)}</i>`:''}</dd><dt>SMR no.</dt><dd>${f&&f.key==='carrowmore'?'SL014-209 (cemetery)':s[0].startsWith('NI:')?`${esc(s[0].slice(3))} · <a href="${META.ni_url}" target="_blank" rel="noopener">NI SMR (OGL) ↗</a>`:`<a href="${link}" target="_blank" rel="noopener">${esc(s[0])} ↗</a>`}</dd>${s[7]?`<dt>ITM</dt><dd>${s[7]} E, ${s[8]} N</dd>`:''}</dl>`;
  if(f){const v=VLAB[f.verdict];h+=`<p style="margin:6px 0"><span class="verdict ${v[0]}">${v[1]}</span></p><p style="font-size:14px;margin:4px 0"><b>Claim.</b> ${esc(f.claim)}</p><p style="font-size:14px;margin:4px 0"><b>Evidence.</b> ${esc(f.evidence)}</p><p class="note">${esc(f.caveat)}</p><p class="note">Sources: ${srcLinks(f.src)}</p><canvas class="hz" id="hzc"></canvas><p class="note">Local horizon (DSM, height ×6), with sunrise and sunset points (gold) and the Moon’s major standstills (lilac).</p>`;}
  h+=`<table class="rays"><tbody>${ev.filter(e=>e.az!=null).map(e=>`<tr class="${e.body}"><td>${esc(e.en)}${e.ga?`<div class="gl" lang="ga">${esc(e.ga)}</div>`:''}</td><td>${e.az.toFixed(1)}°</td></tr>`).join('')}</tbody></table>`;
  h+=`<p class="note">Azimuths from true north for ${era<0?'c. 3200 BC (tilt 24.04°)':'today (tilt 23.44°)'}, Sun’s centre with refraction, Moon with parallax. ${dem?'Horizon from the Copernicus 30 m surface model (it includes trees and buildings).':'This assumes a <b>flat horizon</b>; real hills shift these points.'}</p>`;
  $('#card').innerHTML=h;$('#card').scrollTop=0;
  if(f)drawHz(HOR[f.key],ev);
}
function drawHz(h,ev){
  const cv=$('#hzc');if(!cv)return;const r=cv.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);cv.width=r.width*dpr;cv.height=r.height*dpr;const g=cv.getContext('2d');g.scale(dpr,dpr);
  const W=r.width,H=r.height,base=H-22,ex=6,X=az=>az/360*W,Y=a=>base-a*ex*(H/120)*2.2;
  g.beginPath();g.moveTo(0,H);for(let i=0;i<h.alt.length;i++)g.lineTo(X(i*h.step),Y(h.alt[i]));g.lineTo(W,H);g.closePath();
  const gr=g.createLinearGradient(0,base-30,0,H);gr.addColorStop(0,'#5a1a26');gr.addColorStop(1,'#1b0a10');g.fillStyle=gr;g.fill();g.strokeStyle='rgba(243,200,120,.8)';g.lineWidth=1;g.stroke();
  g.font='10px system-ui';g.fillStyle='rgba(247,236,214,.7)';['N','E','S','W','N'].forEach((t,i)=>g.fillText(t,Math.min(W-8,X(i*90)+2),H-6));
  for(const e of ev){if(e.az==null)continue;const x=X(e.az),y=Y(A.horAt(h.alt,e.az));g.strokeStyle=e.body==='sun'?'#f3c46b':'#c9bdf0';g.lineWidth=1.4;g.beginPath();g.moveTo(x,y-2);g.lineTo(x,y-16);g.stroke();g.fillStyle=e.body==='sun'?'#f3c46b':'#c9bdf0';g.beginPath();g.arc(x,y-18,2.4,0,7);g.fill();}
}
/* hidden gem: G = grian: solstice sunrise rays from every passage tomb in view */
document.addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('input,textarea'))return;if((e.key==='g'||e.key==='G')&&map){rayLayer.clearLayers();const b=map.getBounds(),km=rayKm();let n=0;for(const s of SITES){if(s[1]!=='pt'||!b.contains([s[2],s[3]]))continue;const az=A.eventAz(-A.obliquity(era),s[2],null,true,'sun');rayLayer.addLayer(L.polyline([[s[2],s[3]],A.dest(s[2],s[3],az,km*.8)],{color:'#f3c46b',weight:1.6,opacity:.9,interactive:false}));n++;if(n>400)break;}
  toast(`<i lang="ga">Grian</i>: midwinter sunrise rays (flat horizon, ${era<0?'c. 3200 BC':'today'}) drawn from the ${n} passage tombs in view. Do they all point that way? <b>No.</b> That is what the pre-registered tests are for.`,7000);document.getElementById('map').scrollIntoView({behavior:'smooth',block:'center'});}});

/* ---------- Newgrange light simulator ---------- */
let ngNeo=false,ngTimer=null;
const NGOBS=()=>new Astronomy.Observer(HOR.newgrange.lat,HOR.newgrange.lon,HOR.newgrange.ground_m);
function sunAt(date,neo){const lat=HOR.newgrange.lat,lon=HOR.newgrange.lon;const eq=Astronomy.Equator('Sun',date,NGOBS(),true,true);let dec=eq.dec;
  if(neo){const e0=A.obliquity(date.getUTCFullYear()),e1=A.obliquity(-3199);dec=Math.asin(Math.sin(dec*D)*Math.sin(e1*D)/Math.sin(e0*D))/D;}
  const [alt,az]=altaz(eq.ra*15,dec,lstDeg(date,lon),lat);return {alt,az,dec};}
function inHull(az,alt){const P=NG.hull;let inside=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const [xi,yi]=P[i],[xj,yj]=P[j];if(((yi>alt)!==(yj>alt))&&(az<(xj-xi)*(alt-yi)/(yj-yi)+xi))inside=!inside;}return inside;}
function ngDate(){const day=+$('#ngDay').value,min=+$('#ngTime').value;const d=new Date(Date.UTC(2026,11,21)+day*864e5);d.setUTCMinutes(min);return d;}
function initNG(){
  ['ngDay','ngTime'].forEach(id=>$('#'+id).addEventListener('input',drawNG));
  $('#ngEra').onclick=()=>{ngNeo=!ngNeo;$('#ngEra').classList.toggle('on',ngNeo);drawNG();};
  $('#ngPlay').onclick=()=>{if(ngTimer){clearInterval(ngTimer);ngTimer=null;$('#ngPlay').textContent='▶ Play dawn';return;}$('#ngTime').value=528;$('#ngPlay').textContent='❚❚ Pause';ngTimer=setInterval(()=>{const t=$('#ngTime');t.value=+t.value+0.25;drawNG();if(+t.value>=575){clearInterval(ngTimer);ngTimer=null;$('#ngPlay').textContent='▶ Play dawn';}},60);};
  drawNG();
}
function drawNG(){
  if(!NG)return;const d=ngDate(),s=sunAt(d,ngNeo),on=s.alt>-1&&inHull(s.az,s.alt);
  $('#ngDayOut').textContent=fmtD(d)+(+$('#ngDay').value===0?' · grianstad':'');
  $('#ngOut').innerHTML=`<b>${d.toISOString().slice(11,16)} GMT</b> · Sun azimuth <b>${s.az.toFixed(2)}°</b>, altitude <b>${s.alt.toFixed(2)}°</b>, declination <b>${s.dec.toFixed(2)}°</b>${ngNeo?' (Neolithic tilt)':''} · <span class="beamstate ${on?'on':''}">${on?'Beam in the chamber':'No direct light'}</span>`;
  /* chart */
  const cv=$('#ngChart'),r=cv.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);cv.width=r.width*dpr;cv.height=r.height*dpr;const g=cv.getContext('2d');g.scale(dpr,dpr);
  const W=r.width,H=r.height,az0=128.5,az1=141.5,al0=-1,al1=4.5,X=a=>(a-az0)/(az1-az0)*W,Y=a=>H-(a-al0)/(al1-al0)*H;
  const sky=g.createLinearGradient(0,0,0,H);sky.addColorStop(0,'#14101f');sky.addColorStop(1,s.alt>0?'#5a2a20':'#2a1220');g.fillStyle=sky;g.fillRect(0,0,W,H);
  g.strokeStyle='rgba(247,236,214,.08)';g.fillStyle='rgba(247,236,214,.5)';g.font='10.5px system-ui';
  for(let a=129;a<=141;a++){g.beginPath();g.moveTo(X(a),0);g.lineTo(X(a),H);g.stroke();if(a%2===1)g.fillText(a+'°',X(a)+2,12);}
  for(let a=0;a<=4;a++){g.beginPath();g.moveTo(0,Y(a));g.lineTo(W,Y(a));g.stroke();g.fillText(a+'°',3,Y(a)-3);}
  /* window polygon */
  g.beginPath();NG.hull.forEach(([a,b],i)=>i?g.lineTo(X(a),Y(b)):g.moveTo(X(a),Y(b)));g.closePath();g.fillStyle=on?'rgba(243,200,120,.38)':'rgba(243,200,120,.16)';g.fill();g.strokeStyle='#f3c46b';g.lineWidth=1.2;g.stroke();
  NG.obs.forEach(o=>{g.fillStyle='rgba(255,236,190,.85)';g.beginPath();g.arc(X(o.az),Y(o.alt),1.8,0,7);g.fill();});
  /* sun path for the day (both eras if neo) */
  const path=(neo,col,dash)=>{g.beginPath();let st=false;for(let m=500;m<=600;m+=1){const dd=new Date(Date.UTC(2026,11,21)+(+$('#ngDay').value)*864e5);dd.setUTCMinutes(m);const p=sunAt(dd,neo);if(p.az<az0||p.az>az1)continue;st?g.lineTo(X(p.az),Y(p.alt)):g.moveTo(X(p.az),Y(p.alt));st=true;}g.setLineDash(dash||[]);g.strokeStyle=col;g.lineWidth=1.4;g.stroke();g.setLineDash([]);};
  path(false,'rgba(243,215,155,.75)');if(ngNeo)path(true,'rgba(243,170,110,.95)',[5,4]);
  /* horizon */
  const p=HOR.newgrange.alt;g.beginPath();g.moveTo(0,H);for(let a=az0;a<=az1;a+=0.5)g.lineTo(X(a),Y(A.horAt(p,a)));g.lineTo(W,H);g.closePath();const gr=g.createLinearGradient(0,Y(1.2),0,H);gr.addColorStop(0,'#4a1520');gr.addColorStop(1,'#14070b');g.fillStyle=gr;g.fill();g.strokeStyle='rgba(243,200,120,.6)';g.stroke();
  /* sun disk, true size */
  const rad=Math.max(4,(0.265/(az1-az0))*W);const sg=g.createRadialGradient(X(s.az),Y(s.alt),0,X(s.az),Y(s.alt),rad*4);sg.addColorStop(0,'rgba(255,230,170,.9)');sg.addColorStop(1,'rgba(255,200,120,0)');g.fillStyle=sg;g.beginPath();g.arc(X(s.az),Y(s.alt),rad*4,0,7);g.fill();g.fillStyle='#fff2cf';g.beginPath();g.arc(X(s.az),Y(s.alt),rad,0,7);g.fill();
  g.fillStyle='rgba(247,236,214,.75)';g.fillText('Measured window (NMS 2020–21)',X(133.6)+2,Y(2.95));g.fillText('Horizon from DSM',X(139.2),Y(A.horAt(p,139.5))+14);
  drawSection(on,s);
}
function drawSection(on,s){
  const deep=ngNeo, W=520,Hh=260, ground=196;
  const beamEnd=deep?[62,150]:[96,154];
  $('#ngSec').innerHTML=`
  <defs><linearGradient id="bm" x1="1" x2="0"><stop offset="0" stop-color="#fff1c9" stop-opacity=".95"/><stop offset="1" stop-color="#f3c46b" stop-opacity=".55"/></linearGradient>
  <radialGradient id="sg"><stop offset="0" stop-color="#fff1c9"/><stop offset="1" stop-color="#f3c46b" stop-opacity="0"/></radialGradient></defs>
  <rect width="${W}" height="${Hh}" fill="transparent"/>
  <path d="M0 ${ground} H${W}" stroke="#b98a35" stroke-opacity=".6"/>
  <path d="M20 ${ground} C60 70 190 34 280 34 C350 34 410 70 440 ${ground} Z" fill="#3a141d" stroke="#e8b860" stroke-opacity=".55"/>
  <path d="M40 ${ground} C80 98 190 62 280 62" fill="none" stroke="#e8b860" stroke-opacity=".18"/>
  <path d="M58 150 L58 118 L96 104 L404 168 L404 186 L96 160 L58 160 Z" fill="#160a10" stroke="#e8b860" stroke-opacity=".6"/>
  <text x="60" y="100" fill="#e6d3b3" font-size="11" font-family="Iowan Old Style,Palatino,Georgia,serif" font-style="italic">chamber</text>
  <text x="200" y="196" fill="#e6d3b3" font-size="11" font-family="Iowan Old Style,Palatino,Georgia,serif" font-style="italic">passage · c. 19 m</text>
  <rect x="396" y="152" width="18" height="8" fill="${on?'#fff1c9':'#2a0f16'}" stroke="#e8b860"/>
  <text x="372" y="146" fill="#e6d3b3" font-size="11" font-family="Iowan Old Style,Palatino,Georgia,serif" font-style="italic">roof-box</text>
  <rect x="402" y="168" width="12" height="20" fill="#2a0f16" stroke="#e8b860" stroke-opacity=".7"/>
  ${on?`<path d="M414 154 L414 159 L${beamEnd[0]} ${beamEnd[1]+6} L${beamEnd[0]} ${beamEnd[1]} Z" fill="url(#bm)" style="filter:drop-shadow(0 0 6px #f3c46b)"/>`:''}
  <circle cx="${492}" cy="${ground-6-Math.max(-8,Math.min(30,s.alt*10))}" r="16" fill="url(#sg)" opacity="${s.alt>-0.6?1:.25}"/>
  <circle cx="${492}" cy="${ground-6-Math.max(-8,Math.min(30,s.alt*10))}" r="6" fill="#fff1c9" opacity="${s.alt>-0.6?1:.25}"/>
  <text x="440" y="${ground+18}" fill="#b89c82" font-size="10.5" font-family="system-ui">SE horizon ${s.az.toFixed(1)}°</text>`;
}

/* ---------- sky dome ---------- */
let domeLines=false,domeBase=new Date();
function initDome(){
  $('#domeT').addEventListener('input',()=>{['domeNow','domeTonight','domeWS'].forEach(i=>$('#'+i).classList.remove('on'));drawDome();});
  $('#domeNow').onclick=()=>{domeBase=new Date();$('#domeT').value=0;act('domeNow');drawDome();};
  $('#domeTonight').onclick=()=>{const n=new Date();const s=new Intl.DateTimeFormat('en-CA',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'}).format(n);const off=-new Date(new Date(s+'T12:00:00Z').toLocaleString('en-US',{timeZone:'UTC'})).getTime()+new Date(new Date(s+'T12:00:00Z').toLocaleString('en-US',{timeZone:TZ})).getTime();domeBase=new Date(Date.parse(s+'T23:00:00Z')-off);$('#domeT').value=0;act('domeTonight');drawDome();};
  $('#domeWS').onclick=()=>{const y=new Date().getFullYear();const ws=Astronomy.Seasons(y).dec_solstice.date;const d=new Date(Date.UTC(ws.getUTCFullYear(),ws.getUTCMonth(),ws.getUTCDate(),8,15));domeBase=d<new Date()?new Date(Date.UTC(y+1,11,21,8,15)):d;$('#domeT').value=0;act('domeWS');drawDome();};
  $('#domeLines').onclick=()=>{domeLines=!domeLines;$('#domeLines').classList.toggle('on',domeLines);drawDome();};
  drawDome();setInterval(()=>{if($('#domeNow').classList.contains('on')){domeBase=new Date();drawDome();}},60000);
}
function act(id){['domeNow','domeTonight','domeWS'].forEach(i=>$('#'+i).classList.toggle('on',i===id));}
function drawDome(){
  if(!SKY)return;const cv=$('#dome'),r=cv.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);cv.width=r.width*dpr;cv.height=r.width*dpr;const g=cv.getContext('2d');g.scale(dpr,dpr);
  const W=r.width,cx=W/2,cy=W/2,R=W/2-14,date=new Date(domeBase.getTime()+(+$('#domeT').value)*36e5),lat=C.home.lat,lon=C.home.lon,lst=lstDeg(date,lon),ob=new Astronomy.Observer(lat,lon,C.home.elev);
  const P=(alt,az)=>{const rr=R*(90-alt)/90;return [cx-rr*Math.sin(az*D),cy-rr*Math.cos(az*D)];};
  const sunE=Astronomy.Equator('Sun',date,ob,true,true),[sAlt,sAz]=altaz(sunE.ra*15,sunE.dec,lst,lat);
  /* sky colour by Sun altitude */
  const t=Math.max(0,Math.min(1,(sAlt+12)/18)),tt2=t*t;const top=[Math.round(18+70*tt2),Math.round(14+90*tt2),Math.round(40+120*tt2)],bot=[Math.round(30+190*tt2),Math.round(14+120*tt2),Math.round(34+60*tt2)];
  const bg=g.createRadialGradient(cx,cy,0,cx,cy,R);bg.addColorStop(0,`rgb(${top})`);bg.addColorStop(1,`rgb(${bot})`);g.fillStyle=bg;g.beginPath();g.arc(cx,cy,R,0,7);g.fill();
  if(sAlt>-12){const [x,y]=P(Math.max(sAlt,-2),sAz);const gl=g.createRadialGradient(x,y,0,x,y,R*.8);gl.addColorStop(0,`rgba(255,200,130,${.5*t})`);gl.addColorStop(1,'rgba(255,200,130,0)');g.fillStyle=gl;g.beginPath();g.arc(cx,cy,R,0,7);g.fill();}
  g.save();g.beginPath();g.arc(cx,cy,R,0,7);g.clip();
  /* alt rings */
  g.strokeStyle='rgba(243,200,120,.10)';g.lineWidth=1;[30,60].forEach(a=>{g.beginPath();g.arc(cx,cy,R*(90-a)/90,0,7);g.stroke();});
  const starA=Math.max(0,Math.min(1,(-sAlt-4)/10));
  if(domeLines&&starA>0){g.strokeStyle=`rgba(243,200,120,${.28*starA+.05})`;g.lineWidth=.8;for(const ln of SKY.lines){g.beginPath();let st=false;for(const [ra,de] of ln){const [al,az]=altaz(ra,de,lst,lat);if(al<-5){st=false;continue;}const [x,y]=P(al,az);st?g.lineTo(x,y):g.moveTo(x,y);st=true;}g.stroke();}}
  if(starA>0){for(const s of SKY.stars){const [al,az]=altaz(s[0],s[1],lst,lat);if(al<0)continue;const [x,y]=P(al,az);const m=s[2],rad=Math.max(.45,2.6-m*.42),c=bvColor(s[3]);const ext=al<8?.55:1;g.fillStyle=`rgba(${c},${Math.min(1,(1.05-m*.14))*starA*ext})`;g.beginPath();g.arc(x,y,rad,0,7);g.fill();if(s[4]&&m<1.2&&al>4){g.fillStyle=`rgba(247,236,214,${.6*starA})`;g.font='10px system-ui';g.fillText(s[4],x+4,y-3);}}}
  /* bodies */
  const bodies=[['Moon','#f7ecd6'],['Venus','#fff4d6'],['Jupiter','#f3d79b'],['Mars','#ff9a6a'],['Saturn','#e9d58a'],['Mercury','#d8c8b0']];const vis=[];
  for(const [b,col] of bodies){const e=Astronomy.Equator(b,date,ob,true,true),[al,az]=altaz(e.ra*15,e.dec,lst,lat);if(al<-1)continue;const [x,y]=P(al,az);
    if(b==='Moon'){const fr=Astronomy.Illumination('Moon',date).phase_fraction;g.fillStyle='rgba(30,22,40,.9)';g.beginPath();g.arc(x,y,7,0,7);g.fill();const ph=Astronomy.MoonPhase(date);g.save();g.beginPath();g.arc(x,y,7,0,7);g.clip();g.fillStyle=col;g.beginPath();const k=Math.cos(ph*D);/* terminator */const waxing=ph<180;g.arc(x,y,7,-Math.PI/2,Math.PI/2,!waxing);g.ellipse(x,y,7*Math.abs(k),7,0,Math.PI/2,-Math.PI/2,(k>0)!==waxing?true:false);g.fill();g.restore();g.fillStyle='rgba(247,236,214,.85)';g.font='italic 11px Iowan Old Style,Palatino,Georgia,serif';g.fillText('Gealach',x+10,y+4);vis.push('Moon '+Math.round(fr*100)+'%');}
    else{g.fillStyle=col;g.beginPath();g.arc(x,y,2.6,0,7);g.fill();g.fillStyle='rgba(243,215,155,.85)';g.font='10.5px system-ui';g.fillText(b,x+5,y+3);vis.push(b);}}
  if(sAlt>-1){const [x,y]=P(sAlt,sAz);g.fillStyle='#fff1c9';g.beginPath();g.arc(x,y,8,0,7);g.fill();}
  g.restore();
  /* real horizon rim (×5) */
  const pr=HOR.newgrange.alt;g.beginPath();for(let i=0;i<=720;i++){const az=i*.5,al=A.horAt(pr,az%360)*5;const [x,y]=P(al,az);i?g.lineTo(x,y):g.moveTo(x,y);}g.closePath();g.moveTo(cx+R+14,cy);g.arc(cx,cy,R+14,0,Math.PI*2,true);g.fillStyle='#1a080c';g.fill('evenodd');
  g.strokeStyle='rgba(243,200,120,.55)';g.lineWidth=1;g.beginPath();for(let i=0;i<=720;i++){const az=i*.5,al=A.horAt(pr,az%360)*5;const [x,y]=P(al,az);i?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();
  const ev=A.events(lat,pr,new Date().getFullYear()).filter(e=>e.body==='sun');g.strokeStyle='#f3c46b';g.lineWidth=1.6;for(const e of ev){const [x1,y1]=P(0,e.az),[x2,y2]=P(-12,e.az);g.beginPath();g.moveTo(x1,y1);g.lineTo(x2,y2);g.stroke();}
  g.fillStyle='rgba(247,236,214,.8)';g.font='600 11px system-ui';[['N',0],['E',90],['S',180],['W',270]].forEach(([l,az])=>{const [x,y]=P(-9.5,az);g.fillText(l,x-4,y+4);});
  $('#domeOut').innerHTML=`${fmtD(date)} · <b>${fmtT(date)}</b> Irish time · Sun ${sAlt.toFixed(1)}°${vis.length?' · above the horizon: '+vis.join(', '):''}`;
}

/* ---------- today's sky ---------- */
function renderToday(){
  const ob=new Astronomy.Observer(C.home.lat,C.home.lon,C.home.elev),now=new Date(),dayStart=new Date(now);dayStart.setHours(0,0,0,0);
  const rs=(b,dir)=>{try{const t=Astronomy.SearchRiseSet(b,ob,dir,dayStart,1);return t?t.date:null;}catch(e){return null;}};
  const sr=rs('Sun',1),ss=rs('Sun',-1),mr=rs('Moon',1),ms=rs('Moon',-1);
  const len=sr&&ss?(ss-sr)/36e5:null;const ph=Astronomy.MoonPhase(now),fr=Astronomy.Illumination('Moon',now).phase_fraction;
  const names=['New Moon','Waxing crescent','First quarter','Waxing gibbous','Full Moon','Waning gibbous','Last quarter','Waning crescent'];const pn=names[Math.round(ph/45)%8];
  const y=now.getFullYear();const S=[Astronomy.Seasons(y),Astronomy.Seasons(y+1)];const evs=[];S.forEach(s=>{evs.push(['March equinox','Cónocht an earraigh',s.mar_equinox.date],['June solstice','Grianstad an tsamhraidh',s.jun_solstice.date],['September equinox','Cónocht',s.sep_equinox.date],['December solstice','Grianstad an gheimhridh',s.dec_solstice.date]);});
  const nx=evs.filter(e=>e[2]>now).sort((a,b)=>a[2]-b[2])[0];const days=Math.ceil((nx[2]-now)/864e5);
  const ws=S[0].dec_solstice.date,wsPrev=Astronomy.Seasons(y-1).dec_solstice.date;const dd=Math.min(Math.abs(now-ws),Math.abs(now-wsPrev))/864e5;const inSeason=dd<=19;
  const nextOpen=new Date(ws.getTime()-19*864e5);
  /* planets at 23:00 tonight */
  const t23=new Date(now);t23.setHours(23,0,0,0);const pl=['Venus','Mars','Jupiter','Saturn','Mercury'].filter(b=>{const e=Astronomy.Equator(b,t23,ob,true,true);return Astronomy.Horizon(t23,ob,e.ra,e.dec,'normal').altitude>8;});
  const li=(en,ga,v)=>`<li><span>${en}${ga?`<i lang="ga">${ga}</i>`:''}</span><b>${v}</b></li>`;
  $('#today').innerHTML=[li('Sunrise','Éirí na gréine',fmtT(sr)),li('Sunset','Luí na gréine',fmtT(ss)),li('Day length','',len?`${Math.floor(len)} h ${Math.round((len%1)*60)} min`:'—'),
   li('Moon','Gealach',`${pn} · ${Math.round(fr*100)}% lit`),li('Moonrise / moonset','Éirí na gealaí',`${fmtT(mr)} / ${fmtT(ms)}`),
   li('Next solstice or equinox',nx[1],`${nx[0]} · ${fmtD(nx[2])} (${days} day${days===1?'':'s'})`),
   li('Newgrange roof-box season','',inSeason?'Open now: on clear mornings direct light reaches the chamber':`Closed · light returns from c. ${new Intl.DateTimeFormat('en-IE',{timeZone:TZ,day:'numeric',month:'short'}).format(nextOpen)}`),
   li('Planets up at 23:00','',pl.length?pl.join(', '):'none above 8°')].join('');
}

/* ---------- claims & sources ---------- */
function renderClaims(){
  const card=(f,isSite)=>{const v=VLAB[f.verdict];return `<article class="claim"><span class="verdict ${v[0]}">${v[1]}</span><h3>${esc(f.en)}${f.ga?`<span class="ga" lang="ga">${esc(f.ga)}</span>`:''}</h3><dl><dt>Claim</dt><dd>${esc(f.claim)}</dd><dt>Evidence</dt><dd>${esc(f.evidence)}</dd>${f.caveat?`<dt>Caveat</dt><dd>${esc(f.caveat)}</dd>`:''}</dl><p class="src">Sources: ${srcLinks(f.src)}${isSite?` · <a href="#explore" data-go="${f.key}">Show on map →</a>`:''}</p></article>`;};
  $('#claimCards').innerHTML=window.PA_FEATURED.map(f=>card(f,true)).join('');
  $('#groupCards').innerHTML=window.PA_GROUPCLAIMS.map(f=>card(f,false)).join('');
  document.querySelectorAll('[data-go]').forEach(a=>a.addEventListener('click',e=>{const f=window.PA_FEATURED.find(x=>x.key===a.dataset.go),h=HOR[f.key];map.setView([h.lat,h.lon],12);const s=SITES.find(x=>x[0]===f.smrs)||[f.smrs,'pt',h.lat,h.lon,f.en,f.ga,META.counties.indexOf('SLIGO'),0,0];select(s,f);}));
}
function renderSources(){
  const m=META;const items=[
   `<b>Monuments.</b> National Monuments Service, Archaeological Survey of Ireland, Sites and Monuments Record (SMR) open data, snapshot 1 Dec 2025 (<a href="${m.source_url}">data.gov.ie</a>), <b>CC BY 4.0</b>. We map ${(m.n_core+m.n_standing-Object.values(m.ni_counts).reduce((a,b)=>a+b,0)).toLocaleString()} records in ${Object.keys(m.groups).length} prehistoric classes. ${m.dropped_outside_ireland_bbox.length} records in these classes have no published coordinates (ITM 0,0) and are left out. Every card links to the official Historic Environment Viewer record.`,
   `<b>Northern Ireland monuments.</b> Northern Ireland Sites and Monuments Record, Department for Communities Historic Environment Division, via <a href="${m.ni_url}">OpenDataNI</a>, snapshot 10 Sep 2026, <b>Open Government Licence v3.0</b>. It contains public sector information licensed under the OGL. We include ${Object.values(m.ni_counts).reduce((a,b)=>a+b,0).toLocaleString()} located records whose type maps exactly to one of our classes; records marked uncertain (‘?’), unlocated or destroyed are left out.`,
   `<b>Irish townland names.</b> Tailte Éireann Townlands (National Statutory Boundaries 2019), ENGLISH/GAEILGE fields, via the GSI open-data service (<a href="https://gsi.geodata.gov.ie/server/rest/services/Third_Party/IE_GSI_Tailte_Eireann_Townlands_IE26_ITM/FeatureServer/0">service</a>). Names are matched by townland + county, or by point-in-polygon with a name check. When the match is ambiguous, no Irish name is shown.`,
   `<b>Irish class terms.</b> Fingal County Council / ENFO bilingual leaflet <a href="https://www.fingal.ie/sites/default/files/2019-04/Earthen%20Banks%20and%20Broken%20Walls.pdf">Earthen Banks and Broken Walls</a>; <a href="https://www.focloir.ie/">focloir.ie</a> (Foras na Gaeilge) for heinse, grianstad, cónocht, éirí/luí na gréine, éirí na gealaí, spéir na hoíche; <a href="https://www.tearma.ie/q/tuama%20pas%C3%A1iste/ga">téarma.ie</a> for tuama pasáiste. When we found no verified term, only the English is shown.`,
   `<b>Horizons.</b> Copernicus GLO-30 DEM (a 30 m surface model) © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA. Free licence, via the AWS open-data registry. The Newgrange check: the model gives 0.83° at azimuth 135°, against Patrick’s survey value of +0°51′.`,
   `<b>Newgrange light.</b> National Monuments Service (2024), <a href="${window.PA_SRC.ng2024[1]}">Winter Solstice Phenomenon at Newgrange: Research Report</a> (F. Prendergast), Tables 3–9: 53 measured Sun positions, 12 Dec 2020 to 8 Jan 2021.`,
   `<b>Stars.</b> <a href="https://github.com/ofrohn/d3-celestial">d3-celestial</a> data © 2015 Olaf Frohn, BSD-3-Clause, derived from the Hipparcos/HYG catalogues. Sun, Moon and planets: <a href="https://github.com/cosinekitty/astronomy">Astronomy Engine</a> (MIT). Obliquity: Laskar (1986).`,
   `<b>Basemap.</b> © OpenStreetMap contributors (ODbL), standard tiles under the OSMF tile usage policy, recoloured in CSS. The map uses <a href="https://leafletjs.com">Leaflet</a> (BSD-2).`,
   `<b>Heritage Maps</b> (<a href="https://heritagemaps.ie">heritagemaps.ie</a>, Heritage Council) brings together many national datasets, but the licence varies by dataset, so check each provider’s terms before reuse. We use the NMS source directly.`,
   ...Object.entries(window.PA_SRC).map(([k,s])=>s[1]?`<a href="${s[1]}">${esc(s[0])}</a>`:esc(s[0])),
   `Ruggles, C. L. N. (1999). <i>Astronomy in Prehistoric Britain and Ireland</i>. Yale University Press.`,
   `Heggie, D. C. (1981). <i>Megalithic Science</i>. Thames & Hudson (cited in NMS 2024).`
  ];
  $('#srcList').innerHTML=items.map(i=>`<li>${i}</li>`).join('');
}
})();
