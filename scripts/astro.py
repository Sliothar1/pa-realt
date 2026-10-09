"""Rise/set azimuths for declinations against a horizon profile (mirrors site/js/astro.js)."""
import math, json
def refr(a):  # Bennett, apparent altitude a in deg -> refraction in deg
    return (1 / math.tan(math.radians(a + 7.31 / (a + 4.4)))) / 60
def az_for(dec, lat, h_geo, rising):
    p, d, h = map(math.radians, (lat, dec, h_geo))
    c = (math.sin(h) - math.sin(p) * math.sin(d)) / (math.cos(p) * math.cos(d))
    if abs(c) > 1: return None
    H = math.acos(c)  # hour angle (positive = west)
    if rising: H = -H
    A = math.degrees(math.atan2(math.sin(H), math.cos(H) * math.sin(p) - math.tan(d) * math.cos(p))) + 180
    return A % 360
def hor_at(prof, az, step=0.5):
    if prof is None: return 0.0
    i = az / step; i0 = int(i) % len(prof); i1 = (i0 + 1) % len(prof); f = i - int(i)
    return prof[i0] * (1 - f) + prof[i1] * f
def event_az(dec, lat, prof, rising, body='sun', limb='centre'):
    par = 0.95 if body == 'moon' else 0.0
    semi = 0.25 if body == 'sun' else 0.26
    A = 90 if rising else 270
    for _ in range(8):
        ha = hor_at(prof, A)
        hg = ha - refr(ha) + par * math.cos(math.radians(ha))
        if limb == 'first': hg -= semi
        A2 = az_for(dec, lat, hg, rising)
        if A2 is None: return None
        A = A2
    return A
def dec_for(az, alt_app, lat, body='sun'):
    par = 0.95 if body == 'moon' else 0.0
    h = alt_app - refr(alt_app) + par * math.cos(math.radians(alt_app))
    p, A, h = map(math.radians, (lat, az, h))
    return math.degrees(math.asin(math.sin(p) * math.sin(h) + math.cos(p) * math.cos(h) * math.cos(A)))
# obliquity (Laskar 1986) ; T in Julian millennia /10 from J2000
def obliquity(year):
    U = (year - 2000) / 10000.0
    c = [84381.448, -4680.93, -1.55, 1999.25, -51.38, -249.67, -39.05, 7.12, 27.87, 5.79, 2.45]
    return sum(ci * U ** i for i, ci in enumerate(c)) / 3600
I_MOON = 5.145
if __name__ == '__main__':
    H = json.load(open('site/data/horizons.json'))
    for era, yr in (('3200 BC', -3199), ('2026', 2026)):
        e = obliquity(yr); print(f'== {era}: obliquity {e:.3f}  major standstill {e+I_MOON:.2f}  minor {e-I_MOON:.2f}')
        for k, v in H.items():
            if k.startswith('_'): continue
            lat, prof = v['lat'], v['alt']
            row = {
              'WS rise': event_az(-e, lat, prof, True), 'WS set': event_az(-e, lat, prof, False),
              'SS rise': event_az(e, lat, prof, True), 'SS set': event_az(e, lat, prof, False),
              'EQ rise': event_az(0, lat, prof, True), 'EQ set': event_az(0, lat, prof, False),
              'MjS rise': event_az(-(e + I_MOON), lat, prof, True, 'moon'), 'MjN set': event_az(e + I_MOON, lat, prof, False, 'moon')}
            print(k.ljust(12), '  '.join(f'{a}:{(b or float("nan")):6.1f}' for a, b in row.items()))
    # Newgrange check against Patrick's roof-box azimuth window 133°42'–138°24' at +0°51'
    for az in (133.7, 138.4):
        print('Newgrange window az', az, 'dec', round(dec_for(az, 0.85, H['newgrange']['lat']), 2))
