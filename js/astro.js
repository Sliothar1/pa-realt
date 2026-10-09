/* Rise/set azimuths against a horizon profile. Mirrors scripts/astro.py. */
(function(){
const D=Math.PI/180;
function refr(a){return (1/Math.tan((a+7.31/(a+4.4))*D))/60;}           // Bennett (deg)
function obliquity(year){const U=(year-2000)/10000,c=[84381.448,-4680.93,-1.55,1999.25,-51.38,-249.67,-39.05,7.12,27.87,5.79,2.45];let s=0;for(let i=0;i<c.length;i++)s+=c[i]*Math.pow(U,i);return s/3600;} // Laskar 1986
function azFor(dec,lat,h,rising){const p=lat*D,d=dec*D,hh=h*D;const c=(Math.sin(hh)-Math.sin(p)*Math.sin(d))/(Math.cos(p)*Math.cos(d));if(Math.abs(c)>1)return null;let H=Math.acos(c);if(rising)H=-H;let A=Math.atan2(Math.sin(H),Math.cos(H)*Math.sin(p)-Math.tan(d)*Math.cos(p))/D+180;return (A%360+360)%360;}
function horAt(prof,az,step){if(!prof)return 0;step=step||0.5;const n=prof.length,i=az/step,i0=Math.floor(i)%n,i1=(i0+1)%n,f=i-Math.floor(i);return prof[i0]*(1-f)+prof[i1]*f;}
function eventAz(dec,lat,prof,rising,body){const par=body==='moon'?0.95:0;let A=rising?90:270;for(let k=0;k<8;k++){const ha=horAt(prof,A);const hg=ha-refr(ha)+par*Math.cos(ha*D);const A2=azFor(dec,lat,hg,rising);if(A2==null)return null;A=A2;}return A;}
const I_MOON=5.145;
function events(lat,prof,year){const e=obliquity(year);return [
 {k:'WS rise',en:'Winter solstice sunrise',ga:'Éirí na gréine, grianstad an gheimhridh',dec:-e,rise:true,body:'sun'},
 {k:'WS set',en:'Winter solstice sunset',ga:'Luí na gréine, grianstad an gheimhridh',dec:-e,rise:false,body:'sun'},
 {k:'SS rise',en:'Summer solstice sunrise',ga:'Éirí na gréine, grianstad an tsamhraidh',dec:e,rise:true,body:'sun'},
 {k:'SS set',en:'Summer solstice sunset',ga:'Luí na gréine, grianstad an tsamhraidh',dec:e,rise:false,body:'sun'},
 {k:'EQ rise',en:'Equinox sunrise (δ = 0°)',ga:'Éirí na gréine, cónocht',dec:0,rise:true,body:'sun'},
 {k:'EQ set',en:'Equinox sunset (δ = 0°)',ga:'Luí na gréine, cónocht',dec:0,rise:false,body:'sun'},
 {k:'MjN rise',en:'Moonrise, major standstill N',ga:'Éirí na gealaí',dec:e+I_MOON,rise:true,body:'moon'},
 {k:'MjN set',en:'Moonset, major standstill N',ga:'',dec:e+I_MOON,rise:false,body:'moon'},
 {k:'MjS rise',en:'Moonrise, major standstill S',ga:'Éirí na gealaí',dec:-(e+I_MOON),rise:true,body:'moon'},
 {k:'MjS set',en:'Moonset, major standstill S',ga:'',dec:-(e+I_MOON),rise:false,body:'moon'},
 {k:'MnN rise',en:'Moonrise, minor standstill N',ga:'Éirí na gealaí',dec:e-I_MOON,rise:true,body:'moon'},
 {k:'MnS set',en:'Moonset, minor standstill S',ga:'',dec:-(e-I_MOON),rise:false,body:'moon'}
].map(ev=>Object.assign(ev,{az:eventAz(ev.dec,lat,prof,ev.rise,ev.body)}));}
/* destination point for a ray of length L km on a sphere */
function dest(lat,lon,az,km){const R=6371,d=km/R,b=az*D,p1=lat*D,l1=lon*D;const p2=Math.asin(Math.sin(p1)*Math.cos(d)+Math.cos(p1)*Math.sin(d)*Math.cos(b));const l2=l1+Math.atan2(Math.sin(b)*Math.sin(d)*Math.cos(p1),Math.cos(d)-Math.sin(p1)*Math.sin(p2));return [p2/D,l2/D];}
window.PAAstro={refr,obliquity,azFor,horAt,eventAz,events,dest,I_MOON};
})();
