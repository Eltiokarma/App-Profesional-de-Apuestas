"""P(sostener la ventaja del descanso) según la fuerza previa (cuota de cierre sin margen).
football-data.co.uk, 11 ligas europeas del padrón, 2012/13-2025/26. Sin minutos: la
ventaja es la del descanso (HT), que es lo que el CSV trae."""
import csv, glob, sys, collections, math

D = sys.argv[1]
filas = []
for p in sorted(glob.glob(D + '/*.csv')):
    liga, temp = p.rsplit('/', 1)[1][:-4].split('_')
    with open(p, encoding='latin-1') as fh:
        for r in csv.DictReader(fh):
            try:
                fh_, fa, hh, ha = (int(r[k]) for k in ('FTHG', 'FTAG', 'HTHG', 'HTAG'))
            except Exception:
                continue
            odds = None
            for c in (('PSCH', 'PSCD', 'PSCA'), ('AvgCH', 'AvgCD', 'AvgCA'), ('PSH', 'PSD', 'PSA'), ('AvgH', 'AvgD', 'AvgA'), ('B365H', 'B365D', 'B365A')):
                try:
                    o = [float(r[k]) for k in c]
                    if all(x > 1 for x in o):
                        odds = o
                        break
                except Exception:
                    pass
            if not odds:
                continue
            inv = [1 / x for x in odds]
            s = sum(inv)
            ph, pd, pa = (x / s for x in inv)
            filas.append(dict(liga=liga, temp=temp, ph=ph, pd=pd, pa=pa, fh=fh_, fa=fa, hh=hh, ha=ha))

print(f'{len(filas)} partidos con cuota y medio tiempo')
TR = [(0, .35, '< 35 %'), (.35, .48, '35-48 %'), (.48, .60, '48-60 %'), (.60, .75, '60-75 %'), (.75, 1.01, '75 %+')]


def tramo(p):
    return next(t[2] for t in TR if t[0] <= p < t[1])


def ic(k, n):
    if not n:
        return ''
    p = k / n
    e = 1.96 * math.sqrt(p * (1 - p) / n)
    return f'±{100*e:.1f}'


def tabla(cond_lado, margen, titulo):
    c = collections.defaultdict(lambda: [0, 0, 0])
    for f in filas:
        for lado in ('h', 'a'):
            if cond_lado and lado != cond_lado:
                continue
            ht = f['hh'] - f['ha'] if lado == 'h' else f['ha'] - f['hh']
            ft = f['fh'] - f['fa'] if lado == 'h' else f['fa'] - f['fh']
            if not (ht == margen if margen < 2 else ht >= 2):
                continue
            p = f['ph'] if lado == 'h' else f['pa']
            k = tramo(p)
            c[k][0] += 1
            c[k][1] += ft > 0
            c[k][2] += ft == 0
    print(f'\n### {titulo}\n')
    print('| Prob. previa del que gana al descanso | n | Gana | Empata | Pierde | No gana (se le escapa) |')
    print('|---|---:|---:|---:|---:|---:|')
    for _, _, k in TR:
        n, g, e = c[k]
        if not n:
            continue
        print(f'| {k} | {n} | {100*g/n:.1f} % | {100*e/n:.1f} % | {100*(n-g-e)/n:.1f} % | **{100*(n-g)/n:.1f} %** {ic(n-g, n)} |')


tabla(None, 1, 'Gana por 1 al descanso (local o visita)')
tabla('h', 1, 'Local que gana por 1 al descanso')
tabla('a', 1, 'Visita que gana por 1 al descanso')
tabla(None, 2, 'Gana por 2+ al descanso')

# las dos mitades: ¿se sostiene igual en 2012-18 y 2019-26?
for nombre, sel in (('2012/13-2017/18', lambda t: t < '1819'), ('2018/19-2025/26', lambda t: t >= '1819')):
    sub = [f for f in filas if sel(f['temp'])]
    c = collections.defaultdict(lambda: [0, 0])
    for f in sub:
        for lado in ('h', 'a'):
            ht = f['hh'] - f['ha'] if lado == 'h' else f['ha'] - f['hh']
            ft = f['fh'] - f['fa'] if lado == 'h' else f['fa'] - f['fh']
            if ht != 1:
                continue
            k = tramo(f['ph'] if lado == 'h' else f['pa'])
            c[k][0] += 1
            c[k][1] += ft <= 0
    print(f'\nMitad {nombre} (gana por 1 al descanso, % que no gana): ' + ' · '.join(f'{k} {100*c[k][1]/c[k][0]:.1f} % (n {c[k][0]})' for _, _, k in TR if c[k][0]))
