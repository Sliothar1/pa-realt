/* Real-horizon profiles for every mapped monument (Copernicus GLO-30 DSM, scripts/horizon_all.py + hz_shard.py).
   Loaded lazily in ~100 KB county buckets; 1 deg steps, alt = byte/20 - 1 deg. */
window.PAHz=(function(){
const cache={};let idxP=null,ptP=null;
const idx=()=>idxP||(idxP=fetch('data/hz/index.json').then(r=>r.json()).catch(()=>({})));
function dec(b64){const s=atob(b64),a=new Array(s.length);for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i)/20-1;return a;}
async function get(s){
  if(s._hz!==undefined)return s._hz;
  const n=(await idx())[s[6]];if(!n){s._hz=null;return null;}
  let b=0;for(const ch of s[0])b+=ch.charCodeAt(0);b%=n;const key=s[6]+'-'+b;
  if(!cache[key])cache[key]=fetch('data/hz/c'+key+'.json').then(r=>r.json()).catch(()=>({}));
  const v=(await cache[key])[s[0]];s._hz=v?{ground:v[0],alt:dec(v[1]),step:1,lat:s[2],lon:s[3]}:null;return s._hz;}
function pts(){return ptP||(ptP=fetch('data/hz/pt.json').then(r=>r.json()).then(o=>{const m={};for(const k in o)m[k]=dec(o[k][2]);return m;}).catch(()=>({})));}
return {get,pts,dec};
})();
