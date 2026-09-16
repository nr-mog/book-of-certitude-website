# -*- coding: utf-8 -*-
"""Draw Nabíl-i-Akbar's journey as a minimal SVG map.

Geometry: Natural Earth 1:50m admin-0 countries, fetched once to
tools/sources/ne_50m_admin_0_countries.geojson (3 MB, not committed - the
script re-fetches it if absent).

Every country in view is drawn so that the gaps between them read as water:
the Caspian and the Persian Gulf are the shape of what is *not* drawn. Iran
and Iraq are a shade warmer than their neighbours.

Run from the site directory:  python3 tools/gen_journey_map.py
"""
import json
import math
import os
import urllib.request

SRC = 'tools/sources/ne_50m_admin_0_countries.geojson'
URL = ('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/'
       'master/geojson/ne_50m_admin_0_countries.geojson')
OUT = 'images/nabil-journey.svg'

# The window, in degrees: eastern Iraq through all of Iran.
LON0, LON1 = 41.6, 63.6
LAT0, LAT1 = 24.6, 40.4
WIDTH = 900.0
PAD = 28

FOCUS = {'Iran', 'Iraq'}
CONTEXT = {'Turkey', 'Syria', 'Jordan', 'Saudi Arabia', 'Kuwait', 'Qatar',
           'United Arab Emirates', 'Oman', 'Armenia', 'Azerbaijan', 'Georgia',
           'Russia', 'Turkmenistan', 'Uzbekistan', 'Afghanistan', 'Pakistan',
           'Kazakhstan', 'Bahrain'}

# Approximate city centres.
STOPS = [
    ('Qáʼin',     33.7267, 59.1844, 'below'),
    ('Sabzevár',  36.2126, 57.6819, 'above'),
    ('Ṭihrán', 35.6892, 51.3890, 'above'),
    ('Najaf',          31.9959, 44.3148, 'below'),
    ('Baghdád',   33.3152, 44.3661, 'left'),
]
# The order travelled: Qá'in to Sabzevár to Ṭihrán, on to Najaf, then Baghdád.
ROUTE = [0, 1, 2, 3, 4]

PARCHMENT = '#faf7f0'
WATER = '#edf1f0'   # barely blue: the map sits on parchment
LAND = '#f1ece1'
LAND_FOCUS = '#e6dcc4'
BORDER = '#d9cfb8'
GOLD = '#9a7b32'
INK = '#1c2331'
INK_FAINT = '#6f7889'

LAT_MID = (LAT0 + LAT1) / 2
KX = math.cos(math.radians(LAT_MID))
SCALE = (WIDTH - 2 * PAD) / ((LON1 - LON0) * KX)
HEIGHT = (LAT1 - LAT0) * SCALE + 2 * PAD


def project(lon, lat):
    x = PAD + (lon - LON0) * KX * SCALE
    y = PAD + (LAT1 - lat) * SCALE
    return x, y


def rings(geometry):
    if geometry['type'] == 'Polygon':
        return geometry['coordinates']
    out = []
    for poly in geometry['coordinates']:
        out.extend(poly)
    return out


def clip(points, edge, value, keep_greater):
    """Sutherland-Hodgman against one edge of the viewport.

    Without this the file carries the whole of Russia and Kazakhstan off the
    side of the canvas - 167 KB of coordinates nobody can see.
    """
    out = []
    n = len(points)
    for i in range(n):
        cur, prv = points[i], points[i - 1]
        c_in = (cur[edge] >= value) if keep_greater else (cur[edge] <= value)
        p_in = (prv[edge] >= value) if keep_greater else (prv[edge] <= value)
        if c_in != p_in:
            span = cur[edge] - prv[edge]
            t = 0 if span == 0 else (value - prv[edge]) / span
            out.append((prv[0] + (cur[0] - prv[0]) * t,
                        prv[1] + (cur[1] - prv[1]) * t))
        if c_in:
            out.append(cur)
    return out


def path_for(geometry):
    parts = []
    margin = 6
    for ring in rings(geometry):
        pts = [project(lon, lat) for lon, lat in ring]
        for edge, value, keep in ((0, -margin, True), (0, WIDTH + margin, False),
                                  (1, -margin, True), (1, HEIGHT + margin, False)):
            if not pts:
                break
            pts = clip(pts, edge, value, keep)
        if len(pts) < 3:
            continue
        d = 'M ' + ' L '.join('%.1f,%.1f' % p for p in pts) + ' Z'
        parts.append(d)
    return ' '.join(parts)


def main():
    if not os.path.exists(SRC):
        os.makedirs(os.path.dirname(SRC), exist_ok=True)
        print('fetching Natural Earth 50m countries...')
        urllib.request.urlretrieve(URL, SRC)

    data = json.load(open(SRC))
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" '
           'width="%.0f" height="%.0f" font-family="Inter, sans-serif">'
           % (WIDTH, HEIGHT, WIDTH, HEIGHT),
           '<rect width="100%%" height="100%%" fill="%s"/>' % WATER]

    focus_paths = []
    for feature in data['features']:
        name = feature['properties'].get('NAME')
        if name in CONTEXT:
            d = path_for(feature['geometry'])
            if d:
                svg.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.7"/>'
                           % (d, LAND, BORDER))
        elif name in FOCUS:
            focus_paths.append((name, path_for(feature['geometry'])))

    for name, d in focus_paths:
        svg.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.1"/>'
                   % (d, LAND_FOCUS, BORDER))

    # Country names, set quietly.
    for name, lon, lat in (('IRAN', 55.0, 30.6), ('IRAQ', 42.9, 34.4)):
        x, y = project(lon, lat)
        svg.append('<text x="%.1f" y="%.1f" fill="%s" font-size="16" '
                   'letter-spacing="3.4" opacity="0.75">%s</text>'
                   % (x, y, INK_FAINT, name))

    # The journey.
    pts = [project(STOPS[i][2], STOPS[i][1]) for i in ROUTE]
    svg.append('<path d="M %s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>'
               % (' L '.join('%.1f,%.1f' % p for p in pts), GOLD))

    for order, i in enumerate(ROUTE, start=1):
        label, lat, lon, place = STOPS[i]
        x, y = project(lon, lat)
        svg.append('<circle cx="%.1f" cy="%.1f" r="6.6" fill="%s" stroke="%s" '
                   'stroke-width="2.4"/>' % (x, y, PARCHMENT, GOLD))
        svg.append('<circle cx="%.1f" cy="%.1f" r="2.7" fill="%s"/>' % (x, y, GOLD))
        dx, dy, anchor = {
            'above': (0, -18, 'middle'),
            'below': (0, 30, 'middle'),
            'left':  (-15, 7, 'end'),
            'right': (12, 5, 'start'),
        }[place]
        svg.append('<text x="%.1f" y="%.1f" fill="%s" font-size="21" '
                   'font-weight="500" text-anchor="%s">%d. %s</text>'
                   % (x + dx, y + dy, INK, anchor, order, label))

    svg.append('</svg>')
    open(OUT, 'w').write('\n'.join(svg))
    print('wrote %s  (%.0f x %.0f)' % (OUT, WIDTH, HEIGHT))


if __name__ == '__main__':
    main()
