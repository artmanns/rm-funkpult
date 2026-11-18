#!/usr/bin/env python3
"""Funkpult - parametrisches Pultgehaeuse (CadQuery).

Koordinaten "Frontplatte lokal": x nach rechts, y von der Vorderkante nach hinten (bergauf),
z senkrecht aus der Frontplatte heraus. z = 0 ist die Aussenflaeche der Frontplatte,
das Innere liegt bei z < 0.  Alle Masse in mm.

Aufruf:  python3 funkpult_cad.py <ausgabeordner> [--schwanenhals] [--schwungrad]
"""
import math, os, sys, json
import cadquery as cq

# ----------------------------------------------------------------------------
# Parameter
# ----------------------------------------------------------------------------
W, D = 190.0, 112.0        # Aussenmass Frontplatte: Breite, Tiefe entlang der Schraege
TP = 3.0                   # Dicke Frontplatte
TW = 2.4                   # Wandstaerke
RC = 8.0                   # Eckradius aussen
TILT = 18.0                # Neigung der Frontplatte in Grad
HF = 18.0                  # Hoehe der Vorderwand, senkrecht zur Frontplatte gemessen
BASE_T = 2.4               # Dicke Bodenplatte
GAP = 7.0                  # Abstand Frontplatte innen -> Platinenoberseite
PCB_T = 1.6
PCB_X0, PCB_X1, PCB_Y0, PCB_Y1 = 58.0, 176.0, 8.0, 109.0
STANDOFFS = [(62, 12), (172, 12), (62, 105), (108, 105), (172, 70), (126, 34)]   # hinten rechts frei: WLAN-Antenne
INSERT_D, INSERT_L = 4.0, 5.5          # Bohrung fuer M3-Einschmelzmutter

# Display: Waveshare 2.42inch OLED Module (61,5 x 39,5 mm, aktive Flaeche 55,01 x 27,49 mm)
DISP_C = (92.0, 77.75)     # Mitte des Moduls
DISP_W, DISP_H = 61.5, 39.5
DISP_T = 3.6               # Glas + Modulplatine (Annahme, am Modul nachmessen)
DISP_AA = (55.01, 27.49)
DISP_AA_OFF = (0.0, 3.4)   # Versatz aktive Flaeche gegen Modulmitte (Annahme, nachmessen)
DISP_WIN_MARGIN = 1.0

KEY_Y = 43.0
KEY_X = [DISP_C[0] + (i - 1.5) * DISP_AA[0] / 4 for i in range(4)]
KEY_HOLE_D = 8.4
TACT_H = 5.0               # Bauhoehe der 6x6-Taster ueber der Platine

PTT_C = (92.0, 21.0)
PTT_U = 2.0                # Breite der Tastenkappe in "u" (1u = 19,05 mm)
PTT_CAP = (PTT_U * 19.05 - 0.6, 18.1)
PTT_CLR = 0.6

ENC_C = (154.0, 52.0)
ENC_HOLE_D = 7.4
ENC_BODY_H = 6.5
KNOB_D, KNOB_H = 38.0, 15.0

LED_C = (134.0, 92.0)       # rechts oben neben dem Display, vom Knopf nicht verdeckt
LED_HOLE_D = 3.2
MIC_C = (92.0, 103.5)
MIC_BORE = 2.0

SPK_C = (30.0, 58.0)
SPK_D = 40.0
SPK_RIM_T = 2.0
SPK_BOSS = 19.5            # halber Lochabstand des Klemmrings
SPK_BOSS_H = 6.0

USB_X, SW_X = 122.0, 140.0  # Mitte USB-C-Buchse / Schiebeschalter an der Rueckwand
USB_Z = -(TP + GAP + PCB_T + 1.6)
SW_Z = -(TP + GAP + PCB_T + 2.4)

POST = (10.0, 12.0)        # Querschnitt der Eckpfosten fuer die Bodenschrauben
BATT = (50.0, 34.0, 10.0)  # LiPo 103450
BATT_C = (89.5, 66.0)      # Mitte der Akkuwanne in Weltkoordinaten (X, Y)

# ---- Varianten ---------------------------------------------------------------
GOOSENECK = False          # Schwanenhals-Mikrofon hinten links (Gewinde M10x1)
JOG = 'ec11'               # 'ec11' = Rast-Drehgeber, 'flywheel' = Schwungrad-Knopf auf Kugellagern

GN_C = (30.0, 97.0)        # Schwanenhals: Mitte der Bohrung
GN_HOLE_D = 10.3           # Durchgang fuer M10x1
GN_SEAT_D, GN_RIM_D = 26.0, 32.0
GN_TAP_D = 9.3             # Kernloch der Kapsel, in das sich das M10x1-Gewinde selbst schneidet
MICCAP_D = 20.0            # Aussendurchmesser der Mikrofonkapsel an der Spitze
MICMOD_D, MICMOD_T = 14.0, 2.2     # rundes INMP441-Modul

SEL_C = (154.0, 14.0)      # Taste SEL, ersetzt den Taster des Rast-Drehgebers
FW_KNOB_D = 50.0
FW_WASHER = (25.0, 44.0, 4.0)      # Stahlscheibe DIN 125 M24: innen, aussen, Dicke
FW_N = 3                   # Anzahl Scheiben, je rund 32 g
BRG = (8.0, 16.0, 5.0)     # Kugellager 688: innen, aussen, Breite
FW_FLANGE_D, FW_FLANGE_T = 38.0, 3.0
FW_TOWER_D, FW_TOWER_H = 22.0, 14.0
FW_SCREW_R = 15.0
FW_BOSS_H = 5.0
FW_HOLE_D = 14.5           # Durchgang in der Frontplatte fuer den Magnethalter
MAG = (8.0, 2.5)           # Magnet diametral magnetisiert: Durchmesser, Dicke
SENSOR_H = 1.6             # Bauhoehe des MT6701 (SOP-8) auf der Platinenoberseite
MAG_GAP = 1.0              # Luftspalt Magnet - Sensor (Datenblatt: hoechstens 2 mm)
COLLAR_D = 13.0
PIN_LENGTHS = [20, 22, 24, 26, 28, 30, 32, 36, 40]    # Zylinderstift 8 mm, handelsuebliche Laengen

A = math.radians(TILT)
HR = HF + D * math.tan(A)
Z0 = HF * math.cos(A)
HMAX = HR + 6.0
ZI = -TP                   # Innenflaeche der Frontplatte
ZPCB = -(TP + GAP)         # Oberseite Platine


# ----------------------------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------------------------
def box(x0, y0, x1, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(c, d, z0, z1):
    lo, hi = min(z0, z1), max(z0, z1)
    return cq.Workplane('XY').workplane(offset=lo).center(c[0], c[1]).circle(d / 2.0).extrude(hi - lo)


def rrect(c, w, h, r, z0, z1):
    lo, hi = min(z0, z1), max(z0, z1)
    s = cq.Workplane('XY').workplane(offset=lo).center(c[0], c[1]).rect(w, h).extrude(hi - lo)
    return s.edges('|Z').fillet(r) if r > 0 else s


def to_world(o):
    return o.rotate((0, 0, 0), (1, 0, 0), TILT).translate((0, 0, Z0))


def world_pt(x, y, z):
    return (x, y * math.cos(A) - z * math.sin(A), y * math.sin(A) + z * math.cos(A) + Z0)


def below(zlim):
    return cq.Workplane('XY').box(2000, 2000, 500, centered=(True, True, False)).translate((0, 0, zlim - 500))


def union_all(objs):
    r = objs[0]
    for o in objs[1:]:
        r = r.union(o)
    return r


# ----------------------------------------------------------------------------
# Oberteil (Frontplatte + Waende), lokal
# ----------------------------------------------------------------------------
def post_boxes():
    px, py = POST
    return [box(TW - 0.2, TW - 0.2, TW + px, TW + py, -HMAX, ZI + 0.01),
            box(W - TW - px, TW - 0.2, W - TW + 0.2, TW + py, -HMAX, ZI + 0.01),
            box(TW - 0.2, D - TW - py, TW + px, D - TW + 0.2, -HMAX, ZI + 0.01),
            box(W - TW - px, D - TW - py, W - TW + 0.2, D - TW + 0.2, -HMAX, ZI + 0.01)]


def post_centers():
    px, py = POST
    return [(TW + px / 2, TW + py / 2 - 1.0), (W - TW - px / 2, TW + py / 2 - 1.0),
            (TW + px / 2, D - TW - py / 2 - 1.0), (W - TW - px / 2, D - TW - py / 2 - 1.0)]


def post_screw_world():
    """XY der Bodenschrauben in Weltkoordinaten (Schraubenachse senkrecht zum Tisch)."""
    out = []
    for (x, y) in post_centers():
        z = (BASE_T - Z0 - y * math.sin(A)) / math.cos(A)      # lokales z, bei dem der Pfosten auf Z=BASE_T trifft
        X, Y, Z = world_pt(x, y, z)
        out.append((X, Y))
    return out


def speaker_holes():
    pts, pitch = [], 4.2
    for j in range(-6, 7):
        for i in range(-6, 7):
            x = i * pitch + (pitch / 2 if j % 2 else 0)
            y = j * pitch * math.sin(math.radians(60))
            if math.hypot(x, y) <= 16.6:
                pts.append((SPK_C[0] + x, SPK_C[1] + y))
    return pts


def disp_window():
    return (DISP_C[0] + DISP_AA_OFF[0], DISP_C[1] + DISP_AA_OFF[1],
            DISP_AA[0] + 2 * DISP_WIN_MARGIN, DISP_AA[1] + 2 * DISP_WIN_MARGIN)


def fw_screws():
    return [(ENC_C[0] + FW_SCREW_R * math.cos(math.radians(a)), ENC_C[1] + FW_SCREW_R * math.sin(math.radians(a)))
            for a in (90, 210, 330)]


def fw_geo():
    """Hoehen der Schwungrad-Mechanik, gemessen ab Aussenflaeche der Frontplatte (z)."""
    g = {'zb': 1.2}                                          # Unterkante Knopf
    g['zw0'] = FW_FLANGE_T + 1.5                             # Unterkante Scheibenstapel
    g['zw1'] = g['zw0'] + FW_N * FW_WASHER[2]
    g['zslab'] = max(g['zw1'], FW_TOWER_H + 0.5)             # Unterseite des Knopfdeckels
    g['ztop'] = g['zslab'] + 7.0
    g['zmag0'] = ZPCB + SENSOR_H + MAG_GAP                   # Unterkante Magnet
    g['zmag1'] = g['zmag0'] + MAG[1]
    g['zsh0'] = g['zmag1'] + 0.5                             # unteres Ende der Achse
    g['pin'] = max(L for L in PIN_LENGTHS if g['zsh0'] + L <= g['ztop'] - 1.2)
    g['zsh1'] = g['zsh0'] + g['pin']
    return g


def outer_local():
    return (cq.Workplane('XY').box(W, D, HMAX, centered=False).translate((0, 0, -HMAX))
            .edges('|Z').fillet(RC).faces('>Z').edges().chamfer(1.2))


def shell_local():
    outer = outer_local()
    inner = (cq.Workplane('XY').box(W - 2 * TW, D - 2 * TW, HMAX + 2, centered=False)
             .translate((TW, TW, -HMAX - 2 - TP)).edges('|Z').fillet(RC - TW))
    s = outer.cut(inner)

    adds = []
    for p in STANDOFFS:                                   # Platinen-Abstandsbolzen
        adds.append(cyl(p, 8.0, ZPCB, ZI + 0.01))
    if JOG == 'ec11':
        adds.append(cyl(ENC_C, 15.0, ZI - (GAP - ENC_BODY_H), ZI + 0.01))  # Sitzring Drehgeber
    else:
        for p in fw_screws():
            adds.append(cyl(p, 8.0, ZI - FW_BOSS_H, ZI + 0.01))            # Dome fuer die Schrauben des Lagerbocks
    if GOOSENECK:                                                          # Sitz der Mutter, aussen herum ein Versteifungsring
        seat = cyl(GN_C, GN_SEAT_D, ZI - 1.0, ZI + 0.01)
        rim = cyl(GN_C, GN_RIM_D, ZI - 4.0, ZI + 0.01).cut(cyl(GN_C, GN_SEAT_D, ZI - 5, ZI + 1))
        adds.append(seat.union(rim).intersect(outer_local()))
    adds.append(cyl(MIC_C, 7.0, ZPCB + 1.0, ZI + 0.01))                    # Schallkanal Mikrofon
    ring = cyl(SPK_C, SPK_D + 3.6, ZI - SPK_RIM_T, ZI + 0.01).cut(cyl(SPK_C, SPK_D + 0.6, ZI - SPK_RIM_T - 1, ZI + 1))
    adds.append(ring)                                                        # Zentrierring Lautsprecher
    for sx in (-1, 1):
        for sy in (-1, 1):
            adds.append(cyl((SPK_C[0] + sx * SPK_BOSS, SPK_C[1] + sy * SPK_BOSS), 8.0, ZI - SPK_BOSS_H, ZI + 0.01))
    # Display-Anschlagwinkel an den vier Modulecken
    cx, cy = DISP_C
    hw, hh, c, t, leg, h = DISP_W / 2 + 0.3, DISP_H / 2 + 0.3, 0.0, 1.2, 7.0, 3.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            x_in, y_in = cx + sx * hw, cy + sy * hh
            x_out, y_out = x_in + sx * t, y_in + sy * t
            adds.append(box(min(x_in, x_out), min(y_out, y_in - sy * leg), max(x_in, x_out), max(y_out, y_in - sy * leg),
                            ZI - h, ZI + 0.01))
            adds.append(box(min(x_out, x_in - sx * leg), min(y_in, y_out), max(x_out, x_in - sx * leg), max(y_in, y_out),
                            ZI - h, ZI + 0.01))
    s = s.union(union_all(adds))

    cuts = []
    wx, wy, ww, wh = disp_window()
    cuts.append(rrect((wx, wy), ww, wh, 1.0, ZI - 0.1, 0.1))               # Displayfenster
    cuts.append(cq.Workplane('XY').workplane(offset=-1.2).center(wx, wy).sketch().rect(ww, wh).vertices().fillet(1.0)
                .finalize().extrude(1.21, taper=-45))                           # Fase aussen, Ecken mitgerundet
    cuts.append(cq.Workplane('XY').workplane(offset=ZI - 0.1).pushPoints(speaker_holes()).circle(1.2).extrude(TP + 0.2))
    for x in KEY_X:
        cuts.append(cyl((x, KEY_Y), KEY_HOLE_D, ZI - 0.1, 0.1))
    cuts.append(rrect(PTT_C, PTT_CAP[0] + 2 * PTT_CLR, PTT_CAP[1] + 2 * PTT_CLR, 1.5, ZI - 0.1, 0.1))
    if JOG == 'ec11':
        cuts.append(cyl(ENC_C, ENC_HOLE_D, ZI - 1.0, 0.1))
    else:
        cuts.append(cyl(ENC_C, FW_HOLE_D, ZI - 0.1, 0.1))
        for p in fw_screws():
            cuts.append(cyl(p, 3.3, ZI - FW_BOSS_H - 0.1, 0.1))
            cuts.append(cyl(p, INSERT_D, ZI - FW_BOSS_H - 0.01, ZI - FW_BOSS_H + 4.5))
        cuts.append(cyl(SEL_C, KEY_HOLE_D, ZI - 0.1, 0.1))
    if GOOSENECK:
        cuts.append(cyl(GN_C, GN_HOLE_D, ZI - 5.0, 0.1))
    cuts.append(cyl(LED_C, LED_HOLE_D, ZI - 0.1, 0.1))
    cuts.append(cyl(MIC_C, MIC_BORE, ZPCB, 0.1))
    cuts.append(cq.Workplane('XY').workplane(offset=-0.6).center(*MIC_C).circle(MIC_BORE / 2).extrude(0.61, taper=-45))
    for p in STANDOFFS:
        cuts.append(cyl(p, INSERT_D, ZPCB - 0.01, ZPCB + INSERT_L))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (SPK_C[0] + sx * SPK_BOSS, SPK_C[1] + sy * SPK_BOSS)
            cuts.append(cyl(p, INSERT_D, ZI - SPK_BOSS_H - 0.01, ZI - SPK_BOSS_H + 5.0))
    # Rueckwand: USB-C und Schiebeschalter, je mit Mulde aussen
    cuts.append(box(USB_X - 4.8, D - TW - 0.5, USB_X + 4.8, D + 0.5, USB_Z - 1.9, USB_Z + 1.9))
    cuts.append(box(USB_X - 6.6, D - 1.2, USB_X + 6.6, D + 0.5, USB_Z - 3.7, USB_Z + 3.7))
    cuts.append(box(SW_X - 3.6, D - TW - 0.5, SW_X + 3.6, D + 0.5, SW_Z - 2.0, SW_Z + 2.0))
    cuts.append(box(SW_X - 5.6, D - 1.2, SW_X + 5.6, D + 0.5, SW_Z - 3.6, SW_Z + 3.6))
    s = s.cut(union_all(cuts))
    return s


def shell_world():
    s = to_world(shell_local()).cut(below(0.0))
    posts = to_world(union_all(post_boxes()).intersect(outer_local())).cut(below(BASE_T))
    s = s.union(posts)
    holes = [cq.Workplane('XY').workplane(offset=BASE_T - 0.01).center(X, Y).circle(INSERT_D / 2).extrude(INSERT_L + 1.0)
             for (X, Y) in post_screw_world()]
    return s.cut(union_all(holes))


def shell_print(sw):
    """Oberteil in Drucklage: Frontplatte auf dem Druckbett."""
    s = sw.translate((0, 0, -Z0)).rotate((0, 0, 0), (1, 0, 0), -TILT)      # zurueck nach lokal
    s = s.rotate((0, 0, 0), (1, 0, 0), 180)                                  # Frontplatte nach unten
    bb = s.val().BoundingBox()
    return s.translate((-bb.xmin, -bb.ymin, -bb.zmin))


# ----------------------------------------------------------------------------
# Bodenplatte (Weltkoordinaten)
# ----------------------------------------------------------------------------
def plate_world():
    c = 0.25
    cav = (cq.Workplane('XY').box(W - 2 * TW - 2 * c, D - 2 * TW - 2 * c, HMAX + 2, centered=False)
           .translate((TW + c, TW + c, -HMAX - 2 - TP)).edges('|Z').fillet(RC - TW - c))
    slab = cq.Workplane('XY').box(2000, 2000, BASE_T, centered=(True, True, False))
    p = to_world(cav).intersect(slab)
    bx, by = BATT_C
    bw, bh = BATT[0] + 1.0, BATT[1] + 1.0
    t, h = 1.6, 6.0
    walls = []
    for sx in (-1, 1):                                           # kurze Seiten
        x_in = bx + sx * bw / 2
        walls.append(box(min(x_in, x_in + sx * t), by - bh / 2 + 6, max(x_in, x_in + sx * t), by + bh / 2 - 6, BASE_T - 0.01, BASE_T + h))
    for sy in (-1, 1):                                           # lange Seiten, zweiteilig
        y_in = by + sy * bh / 2
        for (xa, xb) in ((bx - bw / 2 + 4, bx - 6), (bx + 6, bx + bw / 2 - 4)):
            walls.append(box(xa, min(y_in, y_in + sy * t), xb, max(y_in, y_in + sy * t), BASE_T - 0.01, BASE_T + h))
    p = p.union(union_all(walls))
    cuts = []
    for (X, Y) in post_screw_world():
        cuts.append(cq.Workplane('XY').workplane(offset=-0.1).center(X, Y).circle(1.7).extrude(BASE_T + 0.2))
        cuts.append(cq.Workplane('XY').center(X, Y).circle(3.2).extrude(1.5, taper=45))    # Senkung fuer M3-Senkkopf
    for (X, Y) in feet_world():
        cuts.append(cq.Workplane('XY').workplane(offset=-0.1).center(X, Y).circle(5.3).extrude(0.6))
    return p.cut(union_all(cuts))


def feet_world():
    y_f = world_pt(0, 0, -HF)[1]
    y_r = world_pt(0, D, -HR)[1]
    return [(24, y_f + 18), (W - 24, y_f + 18), (24, y_r - 18), (W - 24, y_r - 18)]


# ----------------------------------------------------------------------------
# Kleinteile (eigene Koordinaten, Unterseite bei z = 0)
# ----------------------------------------------------------------------------
def knob():
    r = KNOB_D / 2
    k = cq.Workplane('XY').circle(r).extrude(KNOB_H).edges('>Z').fillet(2.0).edges('<Z').chamfer(0.6)
    flutes = cq.Workplane('XY').workplane(offset=1.5).polarArray(r + 0.45, 0, 360, 24).circle(1.15).extrude(KNOB_H)
    k = k.cut(flutes)
    k = k.cut(cq.Workplane('XY').workplane(offset=-0.01).circle(6.75).extrude(3.21))               # Platz fuer Mutter
    dshape = (cq.Workplane('XY').workplane(offset=3.19).circle(3.1).extrude(5.81)
              .intersect(box(-4, -4, 1.55, 4, 3.0, 9.1)))                                          # D-Bohrung 6 mm, Flaeche 4,5
    k = k.cut(dshape)
    k = k.cut(cq.Workplane('YZ').workplane(offset=1.4).center(0, 6.2).circle(1.3).extrude(r))      # M3-Madenschraube
    sr = (7.5 ** 2 + 1.8 ** 2) / (2 * 1.8)
    k = k.cut(cq.Workplane('XY').sphere(sr).rotate((0, 0, 0), (1, 0, 0), 90)
              .translate((-10.5, 0, KNOB_H + sr - 1.8)))                                           # Fingermulde (Kugelpol zur Seite gedreht)
    return k


def keycap():
    fl_t = (GAP - TACT_H) - 0.3
    stem = TP + 0.3 + 1.5
    c = cq.Workplane('XY').circle(5.5).extrude(fl_t)
    c = c.union(cq.Workplane('XY').workplane(offset=fl_t - 0.01).circle((KEY_HOLE_D - 0.4) / 2).extrude(stem + 0.01)
                .edges('>Z').chamfer(0.6))
    return c


def display_spacer():
    t = (GAP - DISP_T) - 1.0                      # 1 mm Schaumstoff darueber
    f = box(-DISP_W / 2, -DISP_H / 2, DISP_W / 2, DISP_H / 2, 0, t)
    f = f.cut(box(-DISP_W / 2 + 5, -DISP_H / 2 - 1, DISP_W / 2 - 5, DISP_H / 2 - 4, -1, t + 1))
    return f


def speaker_clamp():
    s = SPK_BOSS + 5.0
    p = rrect((0, 0), 2 * s, 2 * s, 4.0, 0, 2.4)
    p = p.union(cyl((0, 0), SPK_D + 0.2, 2.39, 2.4 + SPK_BOSS_H - SPK_RIM_T))
    p = p.cut(cyl((0, 0), SPK_D - 3.5, -1, 20))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p.cut(cyl((sx * SPK_BOSS, sy * SPK_BOSS), 3.4, -1, 5))
    return p


# ----------------------------------------------------------------------------
# Variante Schwungrad-Knopf
# ----------------------------------------------------------------------------
def bearing_block():
    """Lagerbock fuer zwei Kugellager 688. Der Flansch liegt aussen auf der Frontplatte; Druck mit dem Flansch nach unten."""
    do, w = BRG[1] + 0.1, BRG[2]
    bore = BRG[0] + 1.0
    b = cyl((0, 0), FW_FLANGE_D, 0, FW_FLANGE_T).union(cyl((0, 0), FW_TOWER_D, 0, FW_TOWER_H))
    b = b.cut(cyl((0, 0), do, -0.01, w))                                                    # unteres Lager
    b = b.cut(cq.Workplane('XY').workplane(offset=w - 0.01).circle(do / 2).extrude((do - bore) / 2, taper=45))   # Kegel statt Bruecke
    b = b.cut(cyl((0, 0), bore, 0, FW_TOWER_H))                                             # Durchgang der Achse
    b = b.cut(cyl((0, 0), do, FW_TOWER_H - w, FW_TOWER_H + 0.01))                           # oberes Lager
    for a in (90, 210, 330):
        p = (FW_SCREW_R * math.cos(math.radians(a)), FW_SCREW_R * math.sin(math.radians(a)))
        b = b.cut(cyl(p, 3.4, -1, FW_FLANGE_T + 1))
        b = b.cut(cq.Workplane('XY').workplane(offset=FW_FLANGE_T - 1.7).center(*p).circle(1.7).extrude(1.71, taper=-45))
    return b


def flywheel_knob():
    """Schwungrad-Knopf (Unterkante bei z = 0). Druck mit der Oberseite nach unten."""
    g = fw_geo()
    h = g['ztop'] - g['zb']
    r = FW_KNOB_D / 2
    pocket_h = g['zslab'] - g['zb']
    hub0 = FW_TOWER_H - g['zb']
    k = cq.Workplane('XY').circle(r).extrude(h).edges('>Z').fillet(2.5).edges('<Z').chamfer(0.6)
    k = k.cut(cq.Workplane('XY').workplane(offset=1.5).polarArray(r + 0.5, 0, 360, 36).circle(1.2).extrude(h))
    k = k.cut(cyl((0, 0), FW_WASHER[1] + 0.6, -0.01, pocket_h))             # Raum fuer Scheiben, Haltering und Flansch
    k = k.union(cyl((0, 0), 10.5, hub0, pocket_h + 0.01))                   # Nabe stuetzt sich auf dem Lager-Innenring ab
    k = k.cut(cyl((0, 0), BRG[0] - 0.05, hub0 - 0.01, g['zsh1'] - g['zb'] + 0.25))      # Presssitz der Achse
    sr = (8.0 ** 2 + 1.8 ** 2) / (2 * 1.8)
    k = k.cut(cq.Workplane('XY').sphere(sr).rotate((0, 0, 0), (1, 0, 0), 90).translate((-15.0, 0, h + sr - 1.8)))   # Fingermulde
    return k


def washer_ring():
    """Haltering, der die Stahlscheiben im Knopf sichert (einkleben)."""
    return cyl((0, 0), FW_WASHER[1] + 0.4, 0, 2.0).cut(cyl((0, 0), FW_FLANGE_D + 3.0, -1, 3))


def magnet_collar():
    """Magnethalter am unteren Achsende (Magnetseite bei z = 0, so auch drucken)."""
    g = fw_geo()
    hgt = -0.2 - g['zmag0']
    c = cyl((0, 0), COLLAR_D, 0, hgt - 0.6).union(cyl((0, 0), 10.5, hgt - 0.61, hgt))
    c = c.cut(cyl((0, 0), MAG[0] + 0.15, -0.01, MAG[1]))
    c = c.cut(cyl((0, 0), BRG[0] - 0.05, MAG[1] + 0.5, hgt + 0.01))
    return c


# ----------------------------------------------------------------------------
# Variante Schwanenhals
# ----------------------------------------------------------------------------
def mic_capsule():
    """Mikrofonkapsel fuer die Schwanenhalsspitze (Gewindeseite bei z = 0, so auch drucken)."""
    l_thread, l_cone, wall, ch = 10.0, (GN_TAP_D - 5.0) / 2, 2.0, MICMOD_T + 4.8
    length = l_thread + l_cone + wall + ch
    b = cq.Workplane('XY').circle(MICCAP_D / 2).extrude(length).edges('<Z').chamfer(1.2)
    b = b.cut(cyl((0, 0), GN_TAP_D, -0.01, l_thread))
    b = b.cut(cq.Workplane('XY').workplane(offset=l_thread - 0.01).circle(GN_TAP_D / 2).extrude(l_cone, taper=45))
    b = b.cut(cyl((0, 0), 5.0, 0, length))                                  # Kabelkanal
    b = b.cut(cyl((0, 0), MICMOD_D + 0.4, length - ch, length + 0.01))      # Kammer fuer das Modul
    return b


def mic_capsule_len():
    return 10.0 + (GN_TAP_D - 5.0) / 2 + 2.0 + MICMOD_T + 4.8


def mic_cap():
    """Frontdeckel der Mikrofonkapsel mit Schalloeffnungen (Aussenseite bei z = 0)."""
    c = cyl((0, 0), MICCAP_D, 0, 1.6).edges('<Z').chamfer(0.8).union(cyl((0, 0), MICMOD_D + 0.2, 1.59, 4.1))
    c = c.cut(cyl((0, 0), 3.0, -1, 5))
    holes = [(4.2 * math.cos(math.radians(a)), 4.2 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return c.cut(cq.Workplane('XY').workplane(offset=-1).pushPoints(holes).circle(1.0).extrude(6))


GN_PATH = [(0.0, 0.0), (0.0, 60.0), (-17.0, 140.0), (-57.0, 205.0), (-107.0, 235.0)]   # (y ab Bohrung, z), nur fuer die Darstellung
GN_END_T = (-0.95, 0.31)


def gooseneck_mock():
    m = {}
    pts = [(GN_C[1] + y, z) for y, z in GN_PATH]
    path = cq.Workplane('YZ', origin=(GN_C[0], 0, 0)).spline(pts, tangents=[(0, 1), GN_END_T])
    m['gn_neck'] = cq.Workplane('XY').center(GN_C[0], GN_C[1]).circle(5.5).sweep(path)
    hw = cyl(GN_C, 20.0, 0, 1.2).union(cq.Workplane('XY').workplane(offset=1.2).center(*GN_C).polygon(6, 19.6).extrude(3.8))
    hw = hw.union(cyl(GN_C, 21.0, ZI - 2.2, ZI - 1.0)).union(
        cq.Workplane('XY').workplane(offset=ZI - 6.0).center(*GN_C).polygon(6, 19.6).extrude(3.8))
    hw = hw.union(cyl(GN_C, 10.0, ZI - 7.0, 6.0))
    m['gn_hardware'] = hw
    n = math.hypot(*GN_END_T)
    ty, tz = GN_END_T[0] / n, GN_END_T[1] / n
    ang = math.degrees(math.atan2(-ty, tz))
    tip = (GN_C[0], GN_C[1] + GN_PATH[-1][0], GN_PATH[-1][1])
    base = (tip[0], tip[1] - ty * 10.0, tip[2] - tz * 10.0)
    L = mic_capsule_len()
    place = lambda o: o.rotate((0, 0, 0), (1, 0, 0), ang).translate(base)
    m['gn_capsule'] = place(mic_capsule())
    m['gn_cap'] = place(mic_cap().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, L + 1.6)))
    m['gn_module'] = place(cyl((0, 0), MICMOD_D, L - 2.5 - MICMOD_T - 0.2, L - 2.5 - 0.2))
    return m


# ----------------------------------------------------------------------------
# Dummys fuer Kollisionspruefung und Darstellung (lokal)
# ----------------------------------------------------------------------------
def mock_local():
    m = {}
    pcb = rrect(((PCB_X0 + PCB_X1) / 2, (PCB_Y0 + PCB_Y1) / 2), PCB_X1 - PCB_X0, PCB_Y1 - PCB_Y0, 2.0, ZPCB - PCB_T, ZPCB)
    for p in STANDOFFS:
        pcb = pcb.cut(cyl(p, 3.2, ZPCB - PCB_T - 1, ZPCB + 1))
    m['pcb'] = pcb
    cx, cy = DISP_C
    m['disp_pcb'] = box(cx - DISP_W / 2, cy - DISP_H / 2, cx + DISP_W / 2, cy + DISP_H / 2, ZI - DISP_T, ZI - 2.0)
    m['disp_glass'] = box(cx - 30.25, cy + DISP_H / 2 - 0.5 - 37.0, cx + 30.25, cy + DISP_H / 2 - 0.5, ZI - 2.0, ZI)
    wx, wy, ww, wh = disp_window()
    m['disp_lit'] = box(wx - DISP_AA[0] / 2, wy - DISP_AA[1] / 2, wx + DISP_AA[0] / 2, wy + DISP_AA[1] / 2, ZI - 0.05, ZI + 0.02)
    m['mx'] = box(PTT_C[0] - 7, PTT_C[1] - 7, PTT_C[0] + 7, PTT_C[1] + 7, ZPCB, ZPCB + 11.6)
    cap = (cq.Workplane('XY').workplane(offset=ZPCB + 10.3).center(*PTT_C).rect(*PTT_CAP).extrude(8.0, taper=14)
           .faces('>Z').edges().fillet(0.8))
    m['ptt_cap'] = cap
    if JOG == 'ec11':
        enc = box(ENC_C[0] - 6.25, ENC_C[1] - 6.7, ENC_C[0] + 6.25, ENC_C[1] + 6.7, ZPCB, ZPCB + ENC_BODY_H)
        shaft = cyl(ENC_C, 6.0, ZPCB, ZPCB + 20.0).cut(box(ENC_C[0] + 1.5, ENC_C[1] - 4, ENC_C[0] + 4, ENC_C[1] + 4, 0.0, 10.1))
        enc = enc.union(cyl(ENC_C, 7.0, ZPCB + ENC_BODY_H, ZPCB + ENC_BODY_H + 7.0)).union(shaft)
        m['encoder'] = enc
        m['enc_nut'] = cq.Workplane('XY').workplane(offset=0.5).center(*ENC_C).polygon(6, 11.5).extrude(2.0).cut(cyl(ENC_C, 7.0, 0, 3))
        m['knob'] = knob().translate((ENC_C[0], ENC_C[1], 1.0))
    else:
        g = fw_geo()
        at = lambda o, z: o.translate((ENC_C[0], ENC_C[1], z))
        m['fw_block'] = at(bearing_block(), 0)
        m['fw_knob'] = at(flywheel_knob(), g['zb'])
        m['fw_washers'] = union_all([cyl(ENC_C, FW_WASHER[1], g['zw0'] + i * FW_WASHER[2], g['zw0'] + (i + 1) * FW_WASHER[2] - 0.05)
                                     .cut(cyl(ENC_C, FW_WASHER[0], -50, 50)) for i in range(FW_N)])
        m['fw_ring'] = at(washer_ring(), g['zw0'] - 2.2)
        m['fw_bearings'] = union_all([cyl(ENC_C, BRG[1], z0, z0 + BRG[2]).cut(cyl(ENC_C, BRG[0], -50, 50))
                                      for z0 in (0.0, FW_TOWER_H - BRG[2])])
        m['fw_shaft'] = cyl(ENC_C, BRG[0] - 0.1, g['zsh0'], g['zsh1'])
        m['fw_collar'] = at(magnet_collar(), g['zmag0'])
        m['fw_magnet'] = cyl(ENC_C, MAG[0], g['zmag0'], g['zmag1'])
        m['fw_sensor'] = box(ENC_C[0] - 2.45, ENC_C[1] - 1.95, ENC_C[0] + 2.45, ENC_C[1] + 1.95, ZPCB, ZPCB + SENSOR_H)
        m['sel_cap'] = keycap().translate((SEL_C[0], SEL_C[1], ZPCB + TACT_H))
        m['sel_tact'] = box(SEL_C[0] - 3, SEL_C[1] - 3, SEL_C[0] + 3, SEL_C[1] + 3, ZPCB, ZPCB + 3.5).union(
            cyl(SEL_C, 3.5, ZPCB + 3.5, ZPCB + TACT_H))
    if GOOSENECK:
        m.update(gooseneck_mock())
    caps = [keycap().translate((x, KEY_Y, ZPCB + TACT_H)) for x in KEY_X]
    m['keycaps'] = union_all(caps)
    tact = [box(x - 3, KEY_Y - 3, x + 3, KEY_Y + 3, ZPCB, ZPCB + 3.5).union(cyl((x, KEY_Y), 3.5, ZPCB + 3.5, ZPCB + TACT_H))
            for x in KEY_X]
    m['tact'] = union_all(tact)
    m['led'] = cyl(LED_C, 3.0, ZPCB + 5.0, 0.2).union(cq.Workplane('XY').sphere(1.5).translate((LED_C[0], LED_C[1], 0.2)))
    spk = cyl(SPK_C, SPK_D, ZI - SPK_RIM_T, ZI).union(cyl(SPK_C, 34, ZI - 9, ZI - SPK_RIM_T)).union(cyl(SPK_C, 24, ZI - 18, ZI - 9))
    m['speaker'] = spk
    m['spk_clamp'] = speaker_clamp().translate((SPK_C[0], SPK_C[1], ZI - SPK_BOSS_H - 2.4))
    m['usb'] = box(USB_X - 4.47, PCB_Y1 - 6.8, USB_X + 4.47, PCB_Y1 + 0.9, ZPCB - PCB_T - 3.2, ZPCB - PCB_T)
    m['switch'] = box(SW_X - 4.3, PCB_Y1 - 4.4, SW_X + 4.3, PCB_Y1, ZPCB - PCB_T - 4.7, ZPCB - PCB_T).union(
        box(SW_X - 2.0, PCB_Y1, SW_X - 0.0, PCB_Y1 + 4.0, SW_Z - 1.0, SW_Z + 1.0))
    m['esp32'] = box(146, 83.5, 164, 109, ZPCB - PCB_T - 3.1, ZPCB - PCB_T)
    m['disp_spacer'] = display_spacer().translate((cx, cy, ZI - DISP_T - ((GAP - DISP_T) - 1.0)))
    return m


def battery_world():
    bx, by = BATT_C
    return box(bx - BATT[0] / 2, by - BATT[1] / 2, bx + BATT[0] / 2, by + BATT[1] / 2, BASE_T + 0.5, BASE_T + 0.5 + BATT[2])


# ----------------------------------------------------------------------------
def vol(o):
    return o.val().Volume()


def bbs(o):
    b = o.val().BoundingBox()
    return '%.1f x %.1f x %.1f' % (b.xlen, b.ylen, b.zlen)


def main(out):
    os.makedirs(out, exist_ok=True)
    stl = os.path.join(out, 'stl')
    viz = os.path.join(out, 'viz')
    os.makedirs(stl, exist_ok=True)
    os.makedirs(viz, exist_ok=True)
    report = {'params': {'W': W, 'D': D, 'TILT': TILT, 'HF': HF, 'HR': round(HR, 2), 'height_front': round(Z0, 1),
                         'height_rear': round(HR * math.cos(A), 1),
                         'footprint_depth': round(world_pt(0, D, -HR)[1] - world_pt(0, 0, -HF)[1], 1)}}

    sw = shell_world()
    pw = plate_world()
    kc, ds, sc = keycap(), display_spacer(), speaker_clamp()
    parts_print = {
        'oberteil': shell_print(sw),
        'bodenplatte': pw.translate((0, -pw.val().BoundingBox().ymin, 0)),
        'tastenkappe': kc,
        'display_halter': ds,
        'lautsprecher_klemmring': sc,
    }
    if JOG == 'ec11':
        parts_print['vfo_knopf'] = knob().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, KNOB_H))
    else:
        g = fw_geo()
        fk = flywheel_knob()
        parts_print['schwungknopf'] = fk.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, g['ztop'] - g['zb']))
        parts_print['lagerbock'] = bearing_block()
        parts_print['haltering'] = washer_ring()
        parts_print['magnethalter'] = magnet_collar()
        report['flywheel'] = {'pin_length_mm': g['pin'], 'knob_height_mm': round(g['ztop'] - g['zb'], 1),
                              'knob_top_above_panel_mm': round(g['ztop'], 1),
                              'steel_mass_g': round(FW_N * math.pi / 4 * (FW_WASHER[1] ** 2 - FW_WASHER[0] ** 2) * FW_WASHER[2] * 7.85e-3, 1),
                              'shaft_in_knob_mm': round(g['zsh1'] - FW_TOWER_H, 1),
                              'shaft_in_collar_mm': round(-0.2 - g['zsh0'], 1)}
    if GOOSENECK:
        parts_print['mikrofonkapsel'] = mic_capsule()
        parts_print['mikrofonkappe'] = mic_cap()
    report['parts'] = {}
    for name, o in parts_print.items():
        v = o.val()
        report['parts'][name] = {'valid': bool(v.isValid()), 'volume_cm3': round(v.Volume() / 1000, 2), 'bbox': bbs(o),
                                 'solids': len(o.solids().vals())}
        cq.exporters.export(o, os.path.join(stl, name + '.stl'), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(o, os.path.join(stl, name + '.step'))

    # Zusammenbau in Weltkoordinaten
    mock = {k: to_world(v) for k, v in mock_local().items()}
    mock['battery'] = battery_world()
    world = {'shell': sw, 'plate': pw}
    world.update(mock)
    for name, o in world.items():
        cq.exporters.export(o, os.path.join(viz, name + '.stl'), tolerance=0.03, angularTolerance=0.15)

    colors = {'shell': (0.20, 0.22, 0.25), 'plate': (0.13, 0.14, 0.16), 'knob': (0.85, 0.47, 0.15), 'keycaps': (0.75, 0.76, 0.78),
              'ptt_cap': (0.80, 0.16, 0.14), 'pcb': (0.05, 0.35, 0.18), 'battery': (0.55, 0.60, 0.68)}
    assy = cq.Assembly(name='funkpult')
    for name, o in world.items():
        col = colors.get(name, (0.45, 0.45, 0.48))
        assy.add(o, name=name, color=cq.Color(*col))
    assy.save(os.path.join(out, 'funkpult_zusammenbau.step'))

    # Kollisionspruefung: Schnittvolumen muss ~0 sein
    def inter(a, b):
        try:
            return round(world[a].intersect(world[b]).val().Volume(), 3)
        except Exception:
            return 0.0
    pairs = [('shell', 'plate'), ('shell', 'pcb'), ('shell', 'disp_pcb'), ('shell', 'disp_glass'), ('shell', 'mx'),
             ('shell', 'ptt_cap'), ('shell', 'encoder'), ('shell', 'knob'), ('shell', 'keycaps'), ('shell', 'tact'),
             ('shell', 'led'), ('shell', 'speaker'), ('shell', 'spk_clamp'), ('shell', 'usb'), ('shell', 'switch'),
             ('shell', 'esp32'), ('shell', 'battery'), ('plate', 'pcb'), ('plate', 'esp32'), ('plate', 'usb'),
             ('plate', 'switch'), ('battery', 'pcb'), ('battery', 'esp32'), ('battery', 'speaker'), ('pcb', 'disp_pcb'),
             ('pcb', 'speaker'), ('pcb', 'spk_clamp'), ('disp_spacer', 'pcb'), ('disp_spacer', 'disp_pcb'),
             ('speaker', 'spk_clamp'), ('knob', 'encoder'), ('knob', 'enc_nut'), ('plate', 'speaker'), ('keycaps', 'tact'),
             ('shell', 'disp_spacer'), ('shell', 'enc_nut')]
    if JOG != 'ec11':
        pairs += [('shell', 'fw_block'), ('shell', 'fw_knob'), ('shell', 'fw_collar'), ('shell', 'fw_shaft'), ('shell', 'sel_cap'),
                  ('shell', 'sel_tact'), ('fw_block', 'fw_knob'), ('fw_block', 'fw_washers'), ('fw_block', 'fw_ring'),
                  ('fw_block', 'fw_bearings'), ('fw_block', 'fw_shaft'), ('fw_block', 'fw_collar'), ('fw_knob', 'fw_washers'),
                  ('fw_knob', 'fw_ring'), ('fw_knob', 'fw_bearings'), ('fw_knob', 'fw_shaft'), ('fw_collar', 'fw_shaft'),
                  ('fw_collar', 'fw_magnet'), ('fw_collar', 'fw_bearings'), ('fw_collar', 'pcb'), ('fw_collar', 'fw_sensor'),
                  ('fw_magnet', 'fw_sensor'), ('fw_shaft', 'fw_bearings'), ('fw_shaft', 'fw_magnet'), ('pcb', 'fw_sensor'),
                  ('sel_cap', 'sel_tact'), ('fw_knob', 'sel_cap'), ('fw_knob', 'keycaps'), ('fw_knob', 'led'), ('fw_knob', 'ptt_cap')]
    if GOOSENECK:
        pairs += [('shell', 'gn_hardware'), ('shell', 'gn_neck'), ('gn_hardware', 'spk_clamp'), ('gn_hardware', 'speaker'),
                  ('gn_hardware', 'pcb'), ('gn_hardware', 'plate'), ('gn_capsule', 'gn_module'), ('gn_capsule', 'gn_cap'),
                  ('gn_cap', 'gn_module'), ('gn_neck', 'fw_knob' if JOG != 'ec11' else 'knob')]
    pairs = [p for p in pairs if p[0] in world and p[1] in world]
    report['interference_mm3'] = {'%s/%s' % p: inter(*p) for p in pairs}
    # Abstaende, die fuer die Montage wichtig sind
    report['clearances'] = {
        'pcb_bottom_to_plate_front_mm': round(world_pt(0, PCB_Y0, ZPCB - PCB_T)[2] - BASE_T, 2),
        'pcb_bottom_to_plate_rear_mm': round(world_pt(0, PCB_Y1, ZPCB - PCB_T)[2] - BASE_T, 2),
        'battery_top_to_pcb_bottom_min_mm': round(world_pt(0, (BATT_C[1] - BATT[1] / 2 - 3.6) / math.cos(A), ZPCB - PCB_T)[2] - (BASE_T + 0.5 + BATT[2]), 2),
        'display_back_to_pcb_mm': round(GAP - DISP_T, 2),
        'knob_bottom_above_panel_mm': 1.0,
    }
    report['screws_world_xy'] = [(round(x, 2), round(y, 2)) for x, y in post_screw_world()]
    with open(os.path.join(out, 'report.json'), 'w') as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    GOOSENECK = '--schwanenhals' in sys.argv
    JOG = 'flywheel' if '--schwungrad' in sys.argv else 'ec11'
    main(args[0] if args else 'ausgabe')
