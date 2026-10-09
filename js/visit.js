/* Printable visit sheet · Bileog cuairte (visit.html?site=SMRS) */
(async function(){
const $=q=>document.querySelector(q),A=window.PAAstro,L=window.PALight,TZ='Europe/Dublin';
const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const id=new URLSearchParams(location.search).get('site')||'ME019-045----';
const GA1={pt:'Tuama pasáiste',ct:'Tuama cúirte',po:'Tuama ursanach',wt:'Tuama dingeach',mu:'Tuama meigiliteach, neamhaicmithe',sc:'Liagchiorcal',sr:'Sraith gallán',sp:'Gallán, péire',he:'Heinse',cu:'Cursas',bb:'Adhlacadh bolláin',ss:'Gallán'};
/* access notes for featured sites: text from the Ask panel, with the date of the source */
const ACC={newgrange:'Heritage Ireland (OPW), checked Oct 2026',knowth:'Heritage Ireland (OPW), checked Oct 2026',dowth:'Heritage Ireland (OPW), checked Oct 2026',
  cairnT:'Heritage Ireland (OPW), Oct 2026; Dáil written answer, 4 Nov 2025',carrowmore:'Heritage Ireland (OPW), 2026 season',carrowkeelG:'no verified source',drombeg:'Heritage Ireland (OPW), checked Oct 2026',beltany:'no verified source'};
try{
  const [S,care]=await Promise.all([fetch('data/sites.json').then(r=>r.json()),fetch('data/care.json').then(r=>r.json()).catch(()=>[])]);
  const META=S.meta,f=window.PA_FEATURED.find(x=>x.smrs===id);let s=S.sites.find(x=>x[0]===id),prof=null,hzMeta=null;
  if(!s&&!f){const st=await fetch('data/standing.json').then(r=>r.json());s=st.sites.find(x=>x[0]===id);}
  if(f){const H=await fetch('data/horizons.json').then(r=>r.json());const h=H[f.key];prof=h.alt;hzMeta={ground:h.ground_m};if(!s)s=[f.smrs,'pt',h.lat,h.lon,f.en,f.ga,META.counties.indexOf('SLIGO'),0,0];}
  if(!s){$('#sheet').innerHTML='<p>Monument not found. <a href="./">Back to the map</a></p>';return;}
  if(!prof){const z=await PAHz.get(s);if(z){prof=z.alt;hzMeta={ground:z.ground};}}
  const G=META.groups[s[1]],cty=(META.counties[s[6]]||'').toLowerCase().replace(/\b\w/g,c=>c.toUpperCase()),ctyGa=META.counties_ga[s[6]]||'';
  const ga=f?f.ga:s[5],en=f?f.en:String(s[4]).replace(/\s*\(.*$/,''),ni=s[0].startsWith('NI:');
  document.title=`${en} · visit sheet · PA Réalt`;
  const url=`https://sliothar1.github.io/pa-realt/#site=${encodeURIComponent(s[0])}`;
  const qr=qrcode(0,'M');qr.addData(url);qr.make();
  /* access */
  let acc,accDate;
  if(f&&PAAsk.F[f.key]&&PAAsk.F[f.key].visit){acc=PAAsk.F[f.key].visit[0];accDate=ACC[f.key]||'';}
  else if(ni){acc='<p>Northern Ireland monument. Access is <b>not known</b> from our sources. Check with the Department for Communities, Historic Environment Division, and ask the landowner before you go.</p>';accDate='NI SMR (OGL v3), downloaded Oct 2026';}
  else if(care.includes(s[0])){acc='<p>Listed as a <b>National Monument in State care</b> (ownership or guardianship). Opening arrangements are <b>not known</b> from our sources, so check with the OPW / Heritage Ireland before you go.</p>';accDate='NMS State-care county lists, 2009 edition';}
  else{acc='<p><b>Not on the State-care lists.</b> Most monuments like this stand on private land: ask the landowner’s permission before you visit, close gates, and don’t disturb the stones. Monuments are protected by law.</p>';accDate='NMS State-care lists (2009) and SMR snapshot of 1 Dec 2025';}
  /* next solstices and equinoxes: sunrise flat and over the real horizon */
  const now=new Date(),ev=L.seasons(now).filter(e=>e[3]>new Date(now.getTime()-864e5)).slice(0,4);
  const rows=ev.map(e=>{const r=L.riseSet(s[2],s[3],prof,e[3],1);return {e,r};});
  const tr=rows.map(({e,r})=>`<tr><td>${e[1]}<div class="ga" lang="ga" style="display:block;margin:0">${e[2]}</div></td><td>${L.fDY(e[3])}</td><td>${L.fT(r.flat)}</td><td><b>${r.real?L.fT(r.real):'—'}</b>${r.az!=null?` · ${r.az.toFixed(0)}°`:''}</td></tr>`).join('');
  /* real-horizon note */
  let note='';
  if(prof){let mx=-9,maz=0;prof.forEach((v,i)=>{if(v>mx){mx=v;maz=i*360/prof.length;}});const ws=rows.find(x=>x.e[0]==='WS')||rows[0];
    const dm=ws&&ws.r.real&&ws.r.flat?Math.round((ws.r.real-ws.r.flat)/6e4):null;
    note=`<p>The skyline here is computed from the Copernicus 30 m surface model, which includes trees and buildings. The highest point of the horizon is <b>${mx.toFixed(1)}°</b> at ${maz.toFixed(0)}°${hzMeta&&hzMeta.ground!=null?`, and the ground is at about ${Math.round(hzMeta.ground)} m`:''}. ${dm!=null?`At the ${esc(ws.e[1])} the Sun clears the real horizon about <b>${Math.abs(dm)} min ${dm>=0?'after':'before'}</b> the textbook (flat) sunrise.`:''} Treat these times as indicative: a field survey would differ.</p>`;
    const W=720,H=90,X=a=>a/360*W,Y=v=>H-14-v*8;let d=`M0 ${H} `;for(let i=0;i<=prof.length;i++)d+=`L${X(i*360/prof.length).toFixed(1)} ${Y(prof[i%prof.length]).toFixed(1)} `;d+=`L${W} ${H} Z`;
    const ticks=rows.filter(x=>x.r.az!=null).map(x=>`<line class="sun" x1="${X(x.r.az)}" x2="${X(x.r.az)}" y1="${Y(A.horAt(prof,x.r.az))-3}" y2="${Y(A.horAt(prof,x.r.az))-18}"/>`).join('');
    note=`<svg class="hzsvg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-label="Horizon profile"><path class="land" d="${d}"/>${ticks}${['N','E','S','W','N'].map((t,i)=>`<text x="${Math.min(W-8,Math.max(2,i*W/4-3))}" y="${H-2}">${t}</text>`).join('')}</svg><p class="note" style="margin:2px 0 8px">Horizon all round (height ×8). The gold ticks are the sunrise points for the dates above.</p>`+note;}
  else note='<p>No real-horizon profile could be loaded, so the times above assume a flat horizon.</p>';
  const ref=ni?`${esc(s[0].slice(3))} (NI SMR)`:`<a href="${META.hev_link_prefix+encodeURIComponent(s[0])}">${esc(f&&f.key==='carrowmore'?'SL014-209 (cemetery)':s[0])}</a>`;
  $('#sheet').innerHTML=`
  <div class="sheet-top"><div>
    <p class="eyebrow" style="margin:0"><i lang="ga">Bileog cuairte</i> · Visit sheet</p>
    ${ga?`<h1 lang="ga">${esc(ga)}</h1><p class="en">${esc(en)}</p>`:`<h1>${esc(en)}</h1><p class="en muted">No Irish form of this townland in the Tailte Éireann data</p>`}
    <p style="margin:2px 0">${esc(G.en.replace(/s$/,'').replace(/tombs \(/,'tomb ('))}${GA1[s[1]]?` · <i lang="ga">${GA1[s[1]]}</i>`:''}</p>
    <p class="muted" style="margin:2px 0;font-size:14px">${esc(cty)}${ctyGa?` · <i lang="ga">${esc(ctyGa)}</i>`:''} · ${ref} · ${s[2].toFixed(5)}° N, ${Math.abs(s[3]).toFixed(5)}° W${s[7]?` · ITM ${s[7]} E, ${s[8]} N`:''}</p>
  </div><div><div class="qr" aria-label="QR code linking to this monument on PA Réalt">${qr.createSvgTag({cellSize:4,margin:0,scalable:true})}</div><p class="qrcap">Scan for the live map</p></div></div>
  <h3>Access<span class="ga" lang="ga">Rochtain</span></h3>${acc}<p class="note">Status as of: ${esc(accDate)}.</p>
  <h3>Next solstices and equinoxes<span class="ga" lang="ga">Grianstaid agus cónochtaí</span></h3>
  <table><thead><tr><th>Event</th><th>Date</th><th>Sunrise (flat)</th><th>Over the real horizon</th></tr></thead><tbody>${tr}</tbody></table>
  <p class="note">Irish time. Flat = Sun’s upper edge on a sea-level horizon (Astronomy Engine). Real horizon = the Sun’s upper edge clearing the computed skyline, with azimuth from true north.</p>
  <h3>The real horizon<span class="ga" lang="ga">An fhíor-léaslíne</span></h3>${note}
  ${f?`<h3>Claim and evidence<span class="ga" lang="ga">Éileamh agus fianaise</span></h3><p><b>Claim.</b> ${esc(f.claim)}</p><p><b>Evidence.</b> ${esc(f.evidence)}</p>`:''}
  <p class="note" style="margin-top:14px">Sources: NMS Sites and Monuments Record (CC BY 4.0)${ni?'; NI SMR, DfC HED (OGL v3)':''}; townland names © Tailte Éireann (CC BY 4.0); Copernicus GLO-30 DEM (© DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the EU and ESA); Astronomy Engine (MIT). Printed from PA Réalt · Designed and built by Garry Lohan · ${new Intl.DateTimeFormat('en-IE',{timeZone:TZ,day:'numeric',month:'short',year:'numeric'}).format(now)}.</p>`;
  $('#printBtn').hidden=false;
}catch(err){console.error(err);$('#sheet').innerHTML='<p>Sorry, the visit sheet could not be built. <a href="./">Back to the map</a></p>';}
})();
