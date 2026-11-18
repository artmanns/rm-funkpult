#!/usr/bin/env python3
"""Stückliste aus intent.json (vom Generator geschrieben) als CSV."""
import json, csv, re, collections, sys, os
d = sys.argv[1] if len(sys.argv) > 1 else '.'
parts = json.load(open(os.path.join(d, 'intent.json')))['parts']
mpn = {
    'U1': 'USBLC6-2SC6 (ST)', 'U2': 'MCP73832T-2ACI/OT (Microchip)', 'U3': 'AP2112K-3.3TRG1 (Diodes)',
    'U4': 'ESP32-S3-WROOM-1-N8R2 (Espressif)', 'U5': 'MAX98357AETE+T (Analog Devices)', 'U6': 'MT6701CT-STD (MagnTek)',
    'MK1': 'ICS-43434 (TDK InvenSense)', 'Q1': 'DMG3415U-7 (Diodes)', 'Q2': 'DMG3415U-7 (Diodes)', 'D1': 'B5819W, SOD-123',
    'F1': 'PTC-Sicherung 1,1 A Haltestrom, 1206', 'FB1': 'MPZ1608S221A (TDK)', 'FB2': 'MPZ1608S221A (TDK)',
    'J1': 'TYPE-C-31-M-12 (Korean Hroparts)', 'J2': 'S2B-PH-SM4-TB (JST)', 'J3': 'S2B-XH-A (JST)',
    'J4': 'Stiftleiste 1x7, 2,54 mm, gewinkelt', 'J5': 'Stiftleiste 1x2, 2,54 mm', 'J6': 'Stiftleiste 1x3, 2,54 mm',
    'J7': 'S5B-PH-SM4-TB (JST)', 'J8': 'Lötpad für Massekabel', 'JP1': 'Lötbrücke, 3 Pads',
    'ENC1': 'PEC11R-4220F-S0024 (Bourns)', 'SW1': 'OS102011MA1QN1 (C&K)', 'SW2': 'TL3342 (E-Switch)', 'SW3': 'TL3342 (E-Switch)',
    'SW4': 'MX-kompatibler Tastaturschalter, linear', 'D2': 'Duo-LED 3 mm rot/grün, gemeinsame Kathode',
}
for i in range(5, 10):
    mpn['SW%d' % i] = 'Taster 6x6 mm, Höhe 5 mm, THT'
tht_top = {'ENC1', 'SW4', 'SW5', 'SW6', 'SW7', 'SW8', 'SW9', 'D2'}
tht_bot = {'J3', 'J4', 'J5', 'J6', 'SW1'}
variant = {'ENC1': 'nur Rast-Drehgeber', 'C16': 'nur Rast-Drehgeber', 'C17': 'nur Rast-Drehgeber',
           'U6': 'nur Schwungrad', 'C21': 'nur Schwungrad', 'JP1': 'nur Schwungrad', 'SW9': 'nur Schwungrad',
           'J7': 'nur Schwanenhals', 'J8': 'nur Schwanenhals', 'R22': 'nur Schwanenhals', 'R23': 'nur Schwanenhals', 'R24': 'nur Schwanenhals'}

def side(ref):
    if ref.startswith('H'):
        return 'Bohrung'
    if ref == 'U6':
        return 'SMD, Oberseite unter der Knopfachse, von Hand'
    if ref in ('J8', 'JP1'):
        return 'Lötstelle, Unterseite'
    if ref in tht_top:
        return 'THT, Oberseite, von Hand'
    if ref in tht_bot:
        return 'THT, Unterseite, von Hand'
    return 'SMD, Unterseite'

def key(ref):
    m = re.match(r'([A-Z]+)(\d+)', ref)
    return (m.group(1), int(m.group(2)))

groups = collections.OrderedDict()
for ref in sorted(parts, key=key):
    p = parts[ref]
    k = (p['value'], p['fp'], mpn.get(ref, ''), side(ref), p['dnp'], variant.get(ref, 'alle'))
    groups.setdefault(k, []).append(ref)
rows = [[', '.join(refs), len(refs), val, fp.split(':')[-1], s, v, 'nicht bestücken' if dnp else '', m]
        for (val, fp, m, s, dnp, v), refs in groups.items()]
with open(os.path.join(d, 'funkpult_stueckliste.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Referenz', 'Anzahl', 'Wert', 'Footprint', 'Bestückung', 'Variante', 'Hinweis', 'Typvorschlag'])
    w.writerows(rows)
print(len(rows), 'Zeilen,', sum(r[1] for r in rows), 'Positionen')
