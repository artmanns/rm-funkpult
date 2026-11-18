#!/usr/bin/env python3
"""Mechanik-Vorgabe fuer das Platinenlayout als DXF (Ursprung = Platinenecke vorne links,
Blick auf die Oberseite, also auf die Seite zur Frontplatte)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import ezdxf
import funkpult_cad as f

def main(out):
    ox, oy = f.PCB_X0, f.PCB_Y0
    w, h, r = f.PCB_X1 - f.PCB_X0, f.PCB_Y1 - f.PCB_Y0, 2.0
    d = ezdxf.new('R2010'); d.units = ezdxf.units.MM
    for name, col in [('Edge.Cuts', 7), ('Bohrungen', 1), ('Bauteile_Oben', 3), ('Bauteile_Unten', 5), ('Sperrflaechen', 6), ('Text', 2)]:
        d.layers.add(name, color=col)
    m = d.modelspace()
    # Umriss mit Eckradius
    pts = [(r, 0), (w - r, 0), (w, r), (w, h - r), (w - r, h), (r, h), (0, h - r), (0, r)]
    for a, b in [(0, 1), (2, 3), (4, 5), (6, 7)]:
        m.add_line(pts[a], pts[b], dxfattribs={'layer': 'Edge.Cuts'})
    for c, a0 in [((w - r, r), 270), ((w - r, h - r), 0), ((r, h - r), 90), ((r, r), 180)]:
        m.add_arc(c, r, a0, a0 + 90, dxfattribs={'layer': 'Edge.Cuts'})
    def txt(s, x, y, layer='Text', hgt=1.6):
        m.add_text(s, dxfattribs={'layer': layer, 'height': hgt}).set_placement((x, y))
    def cross(x, y, layer, n=2.0):
        m.add_line((x - n, y), (x + n, y), dxfattribs={'layer': layer}); m.add_line((x, y - n), (x, y + n), dxfattribs={'layer': layer})
    rows = []
    for i, (x, y) in enumerate(f.STANDOFFS, 1):
        m.add_circle((x - ox, y - oy), 1.6, dxfattribs={'layer': 'Bohrungen'})
        txt('H%d' % i, x - ox + 2.2, y - oy - 0.8); rows.append(('H%d' % i, 'Befestigungsloch Ø 3,2', x - ox, y - oy, 'durchgehend'))
    def top(name, desc, c, size=None):
        x, y = c[0] - ox, c[1] - oy
        cross(x, y, 'Bauteile_Oben')
        if size:
            m.add_lwpolyline([(x - size[0] / 2, y - size[1] / 2), (x + size[0] / 2, y - size[1] / 2), (x + size[0] / 2, y + size[1] / 2), (x - size[0] / 2, y + size[1] / 2)], close=True, dxfattribs={'layer': 'Bauteile_Oben'})
        txt(name, x + 2.5, y + 2.5); rows.append((name, desc, x, y, 'oben'))
    top('SW4', 'PTT, MX-Schalter', f.PTT_C, (14, 14))
    for i, x in enumerate(f.KEY_X):
        top('SW%d' % (5 + i), 'Softkey F%d, Taster 6x6' % (i + 1), (x, f.KEY_Y), (6, 6))
    top('ENC1', 'Drehgeber ENC1 oder Magnetsensor U6 (SOP-8, Oberseite), Knopfachse', f.ENC_C, (12.5, 13.4))
    top('SW9', 'Taste SEL (Schwungrad-Variante), Taster 6x6', f.SEL_C, (6, 6))
    top('D2', 'Duo-LED 3 mm', f.LED_C)
    def bot(name, desc, c, size):
        x, y = c[0] - ox, c[1] - oy
        m.add_lwpolyline([(x - size[0] / 2, y - size[1] / 2), (x + size[0] / 2, y - size[1] / 2), (x + size[0] / 2, y + size[1] / 2), (x - size[0] / 2, y + size[1] / 2)], close=True, dxfattribs={'layer': 'Bauteile_Unten'})
        txt(name, x - size[0] / 2, y - size[1] / 2 - 2.4, 'Bauteile_Unten'); rows.append((name, desc, x, y, 'unten'))
    m.add_circle((f.MIC_C[0] - ox, f.MIC_C[1] - oy), 0.5, dxfattribs={'layer': 'Bohrungen'})
    bot('MK1', 'Mikrofon, Schallloch Ø 1,0 durch die Platine', f.MIC_C, (3.5, 2.65))
    bot('J1', 'USB-C, Vorderkante bündig mit Platinenrand hinten', (f.USB_X, f.PCB_Y1 - 3.65), (8.94, 7.3))
    bot('SW1', 'Schiebeschalter, Hebel nach hinten', (f.SW_X, f.PCB_Y1 - 2.2), (8.6, 4.4))
    bot('U4', 'ESP32-S3-WROOM-1, Antenne zum hinteren Rand', (155, 96.25), (18, 25.5))
    cx, cy = f.DISP_C
    x0, y0 = cx - f.DISP_W / 2 - 1.5 - ox, cy - f.DISP_H / 2 - 1.5 - oy
    m.add_lwpolyline([(x0, y0), (x0 + f.DISP_W + 3, y0), (x0 + f.DISP_W + 3, y0 + f.DISP_H + 3), (x0, y0 + f.DISP_H + 3)], close=True, dxfattribs={'layer': 'Sperrflaechen'})
    txt('Display darüber: Oberseite frei, keine THT-Lötstellen', x0 + 2, y0 + 2, 'Sperrflaechen')
    rows.append(('Display', 'Sperrfläche Oberseite %.1f x %.1f' % (f.DISP_W + 3, f.DISP_H + 3), cx - ox, cy - oy, 'oben'))
    d.saveas(os.path.join(out, 'platine_mechanik.dxf'))
    import json
    json.dump({'size': [w, h], 'rows': rows}, open(os.path.join(out, 'platine_mechanik.json'), 'w'), indent=1, ensure_ascii=False)
    print('PCB %.0f x %.0f mm' % (w, h))
    for r_ in rows: print('  %-8s x=%7.3f y=%7.3f  %-6s %s' % (r_[0], r_[2], r_[3], r_[4], r_[1]))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'ausgabe')
