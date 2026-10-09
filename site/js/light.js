/* Light this week · Solas na seachtaine, plus real-horizon rise/set times (shared with visit.html).
   Windows: Newgrange = direct light photographed in the chamber 12 Dec - 8 Jan (NMS 2024). Other solar events use our own
   indicative windows: solstice +/- 7 days, equinox +/- 3 days. Moon: a monthly lunar extreme within 1.5 deg of the major-standstill declination. */
window.PALight=(function(){
const TZ='Europe/Dublin',DAY=864e5;
const fT=d=>d?new Intl.DateTimeFormat('en-IE',{timeZone:TZ,hour:'2-digit',minute:'2-digit'}).format(d):'—';
const fD=d=>new Intl.DateTimeFormat('en-IE',{timeZone:TZ,weekday:'short',day:'numeric',month:'short'}).format(d);
const fDY=d=>new Intl.DateTimeFormat('en-IE',{timeZone:TZ,day:'numeric',month:'short',year:'numeric'}).format(d);
function dublinMidnight(d){const p=new Intl.DateTimeFormat('en-CA',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'}).format(d);const t=new Date(p+'T00:00:00Z');const off=new Date(t.toLocaleString('en-US',{timeZone:TZ}))-new Date(t.toLocaleString('en-US',{timeZone:'UTC'}));return new Date(t.getTime()-off);}
/* flat (Astronomy Engine, upper limb, sea-level horizon) and real-horizon rise/set for a given local day */
function riseSet(lat,lon,prof,day,dir){
  const ob=new Astronomy.Observer(lat,lon,0),d0=dublinMidnight(day);let flat=null;
  try{const r=Astronomy.SearchRiseSet('Sun',ob,dir,d0,1);flat=r?r.date:null;}catch(e){}
  if(!flat||!prof)return {flat,real:null,az:null};
  const horAt=PAAstro.horAt,f=t=>{const eq=Astronomy.Equator('Sun',t,ob,true,true),h=Astronomy.Horizon(t,ob,eq.ra,eq.dec,'normal');return [h.altitude+0.267-horAt(prof,h.azimuth),h.azimuth];};
  if(dir>0){for(let m=-30;m<=240;m++){const t=new Date(flat.getTime()+m*6e4),[v,az]=f(t);if(v>=0)return {flat,real:t,az};}}
  else{for(let m=30;m>=-240;m--){const t=new Date(flat.getTime()+m*6e4),[v,az]=f(t);if(v>=0)return {flat,real:t,az};}}
  return {flat,real:null,az:null};}
function seasons(from){const y=from.getUTCFullYear(),o=[];[y,y+1].forEach(Y=>{const s=Astronomy.Seasons(Y);o.push(['EQ','March equinox','Cónocht an earraigh',s.mar_equinox.date],['SS','June solstice','Grianstad an tsamhraidh',s.jun_solstice.date],['EQ','September equinox','Cónocht an fhómhair',s.sep_equinox.date],['WS','December solstice','Grianstad an gheimhridh',s.dec_solstice.date]);});return o.sort((a,b)=>a[3]-b[3]);}
function windows(f,now,horizonDays){
  const out=[],end=new Date(now.getTime()+horizonDays*DAY),S=seasons(new Date(now.getTime()-40*DAY));
  for(const k of f.events){const kind=k.slice(0,2),rise=/rise/.test(k);
    if(kind==='Mj'||kind==='Mn')continue;
    for(const s of S){if(s[0]!==kind)continue;let a,b,lab;
      if(f.key==='newgrange'&&kind==='WS'){const y=s[3].getUTCFullYear();a=new Date(Date.UTC(y,11,12,0));b=new Date(Date.UTC(y+1,0,8,23));lab='Direct light in the chamber, 12 Dec – 8 Jan (photographed by NMS, 2020–21)';}
      else{const w=kind==='EQ'?3:7;a=new Date(s[3].getTime()-w*DAY);b=new Date(s[3].getTime()+w*DAY);lab=`${s[1]} ${rise?'sunrise':'sunset'}, ${fD(s[3])} (our window ±${w} days)`;}
      if(b>=now)out.push({f,k,rise,a,b,lab,ga:s[2],inWeek:a<=end&&b>=now});}}
  return out;}
function moonExtreme(now,days){let best=null;for(let h=0;h<=days*24;h+=2){const t=new Date(now.getTime()+h*36e5),eq=Astronomy.Equator('Moon',t,new Astronomy.Observer(54,-7,0),true,true);if(!best||eq.dec>best.dec)best={t,dec:eq.dec};}return best;}
function render(el,HOR){
  const now=new Date(),F=window.PA_FEATURED.filter(f=>f.events.length&&HOR[f.key]);let items=[];
  F.forEach(f=>items.push(...windows(f,now,14)));items.sort((a,b)=>a.a-b.a);
  const week=items.filter(x=>x.inWeek),next=[];const seen=new Set(week.map(x=>x.f.key));for(const x of items){if(!x.inWeek&&!seen.has(x.f.key)){seen.add(x.f.key);next.push(x);}}
  const eps=PAAstro.obliquity(now.getUTCFullYear()),mx=moonExtreme(now,14),mj=F.filter(f=>f.events.includes('MjN set'));
  const moonOn=mx&&mx.dec>=eps+PAAstro.I_MOON-1.5;
  const row=(x,extra)=>{const h=HOR[x.f.key],day=x.a>now?x.a:now,rs=riseSet(h.lat,h.lon,h.alt,day,x.rise?1:-1);
    return `<li><a href="#site=${encodeURIComponent(x.f.smrs)}" data-lw="${x.f.key}"><b>${x.f.en}</b> <i lang="ga">${x.f.ga||''}</i></a><span class="lw-ev">${x.lab}</span><span class="lw-t">${x.rise?'Sunrise':'Sunset'} ${fD(day)}: <b>${fT(rs.real)}</b> over the real horizon${rs.az!=null?` at ${rs.az.toFixed(0)}°`:''} · ${fT(rs.flat)} flat${extra||''}</span></li>`;};
  let h='';
  if(week.length)h+=`<ul class="lw">${week.map(x=>row(x,x.a<=now?' · <em>on now</em>':` · from ${fD(x.a)}`)).join('')}</ul>`;
  else h+=`<p class="lw-none">No featured alignment falls in the next 14 days. <span class="muted">The light is resting.</span></p>`;
  if(moonOn&&mj.length)h+=`<ul class="lw">${mj.map(f=>`<li><b>${f.en}</b><span class="lw-ev">The Moon reaches declination +${mx.dec.toFixed(1)}° on ${fD(mx.t)}, within 1.5° of the major-standstill limit (+${(eps+PAAstro.I_MOON).toFixed(1)}°)</span></li>`).join('')}</ul>`;
  h+=`<h4 class="lw-h">Coming up · <i lang="ga">Ar na bacáin</i></h4><ul class="lw lw-next">${next.slice(0,4).map(x=>`<li><a href="#site=${encodeURIComponent(x.f.smrs)}" data-lw="${x.f.key}"><b>${x.f.en}</b></a><span class="lw-ev">${x.lab}</span><span class="lw-t">window opens in ${Math.ceil((x.a-now)/DAY)} days</span></li>`).join('')}</ul>`;
  const today=window.PA_FEATURED.filter(f=>HOR[f.key]).map(f=>{const H=HOR[f.key],r=riseSet(H.lat,H.lon,H.alt,now,1);return `<tr><td>${f.en}</td><td><b>${fT(r.real)}</b></td><td>${fT(r.flat)}</td></tr>`;}).join('');
  h+=`<details class="lw-today"${week.length?'':' open'}><summary>Sunrise today at each featured site</summary><table class="credits"><thead><tr><th>Site</th><th>Real horizon</th><th>Flat</th></tr></thead><tbody>${today}</tbody></table></details>`;
  el.innerHTML=h;}
return {riseSet,seasons,windows,render,fT,fD,fDY,dublinMidnight};
})();
