# Funkpult – Gehäuse

Pultgehäuse, 18° geneigt, 190 mm breit, 118 mm Standtiefe, vorne 17 mm und hinten 52 mm hoch.
Stand: Entwurf 0.2, 18.11.2026.

Neu in 0.2: Variante mit Schwanenhals-Mikrofon und kugelgelagertem Schwungrad-Knopf im Ordner
`variante/`. Das Standardgehäuse in `stl/` und `step/` ist unverändert.

## Dateien

| Ordner / Datei | Inhalt |
| --- | --- |
| `stl/` | Druckteile des Standardgehäuses, bereits in Drucklage ausgerichtet |
| `step/` | Dieselben Teile als STEP, dazu `funkpult_zusammenbau.step` mit Platzhaltern für Platine, Display, Akku, Lautsprecher |
| `variante/stl/`, `variante/step/` | Geänderte und zusätzliche Teile der Variante, dazu `funkpult_zusammenbau_variante.step` |
| `funkpult_cad.py` | Parametrisches Modell (CadQuery 2.x) |
| `platine_mechanik.dxf` | Platinenumriss, Bohrungen und Bauteilpositionen für das Layout (gilt für alle Ausführungen) |
| `pcb_dxf.py` | Erzeugt die DXF-Datei aus den Parametern des Modells |
| `bilder/` | Ansichten des Zusammenbaus, Schnitt durch den Schwungrad-Knopf |

## Druckteile Standard

| Datei | Stück | Drucklage |
| --- | --- | --- |
| `oberteil.stl` | 1 | Frontplatte auf dem Druckbett, keine Stützstruktur |
| `bodenplatte.stl` | 1 | Unterseite auf dem Bett |
| `vfo_knopf.stl` | 1 | Oberseite auf dem Bett, Stütze nur in der Fingermulde |
| `tastenkappe.stl` | 4 | Flansch auf dem Bett |
| `display_halter.stl` | 1 | flach |
| `lautsprecher_klemmring.stl` | 1 | Platte auf dem Bett |

PETG oder PLA, Düse 0,4 mm, Schichthöhe 0,2 mm, drei Wandlinien, 20 % Füllung.

## Variante: Schwanenhals und Schwungrad-Knopf

Beide Optionen sind unabhängig. Es wird genau ein Oberteil gedruckt; Bodenplatte, Display-Halter,
Klemmring und Tastenkappen kommen aus `stl/`.

| Datei in `variante/stl/` | Stück | Wofür | Drucklage |
| --- | --- | --- | --- |
| `oberteil_schwanenhals_schwungrad.stl` | 1 | beide Optionen | Frontplatte auf dem Bett |
| `oberteil_schwanenhals.stl` | 1 | nur Schwanenhals, Knopf und Drehgeber wie Standard | Frontplatte auf dem Bett |
| `oberteil_schwungrad.stl` | 1 | nur Schwungrad-Knopf | Frontplatte auf dem Bett |
| `schwungknopf.stl` | 1 | Schwungrad | Oberseite auf dem Bett, Stütze nur in der Fingermulde |
| `lagerbock.stl` | 1 | Schwungrad | Flansch auf dem Bett |
| `haltering.stl` | 1 | Schwungrad | flach |
| `magnethalter.stl` | 1 | Schwungrad | Magnetseite auf dem Bett |
| `mikrofonkapsel.stl` | 1 | Schwanenhals | Gewindeseite auf dem Bett |
| `mikrofonkappe.stl` | 1 | Schwanenhals | Außenseite auf dem Bett |
| `stl/tastenkappe.stl` | 5 statt 4 | Schwungrad | fünfte Kappe für die Taste SEL |

Der Knopf `vfo_knopf.stl` entfällt beim Schwungrad. Den Knopf dicht drucken (vier Wandlinien,
40 % Füllung), damit der Presssitz der Achse hält.

### Kaufteile Schwungrad

- 3 Stahlscheiben DIN 125 für M24 (25 × 44 × 4 mm), zusammen 97 g
- 2 Kugellager 688 (8 × 16 × 5 mm); für langen Auslauf entfetten und dünn ölen
- 1 Zylinderstift 8 × 26 mm als Achse
- 1 Magnet Ø 8 × 2,5 mm, diametral magnetisiert
- 3 Senkschrauben M3 × 10 und 3 Einschmelzmuttern M3
- Elektronik: MT6701CT und ein Taster 6 × 6 mm (U6 und SW9, siehe [`../elektronik/`](../elektronik/))

Zusammenbau: Scheiben in den Knopf legen, Haltering einkleben. Lager in den Lagerbock drücken
(Sitz Ø 16,1 mm), Lagerbock von außen auf die Frontplatte schrauben. Stift in den Knopf pressen
(Bohrung Ø 7,95 mm), durch die Lager stecken, von innen den Magnethalter mit eingeklebtem Magnet
aufschieben, bis kein Axialspiel mehr da ist, und mit einem Tropfen Kleber sichern. Der Magnet
steht dann 1 mm über dem Sensor.

### Kaufteile Schwanenhals

- 1 Schwanenhals mit Gewinde M10 × 1 an beiden Enden, etwa 300 mm, leichte Ausführung, mit Mutter
  und Scheibe. Mikrofon-Schwanenhälse mit 3/8-Zoll-Gewinde brauchen ein Reduziergewinde auf M10.
- 1 rundes INMP441-Modul (Ø 14 mm)
- fünfadrige Litze, Ringöse M10, Stecker JST-PH 5-polig

Zusammenbau: Adern durch den Hals ziehen und am Modul anlöten, L/R mit 3,3 V verbinden. Modul in
die Kapsel legen, Deckel aufdrücken, Kapsel auf das Gewinde drehen (Kernloch Ø 9,3 mm, das
Gewinde schneidet sich selbst). Hals in die Bohrung Ø 10,3 mm stecken, innen Ringöse, Scheibe
und Mutter aufsetzen. Nötige Gewindelänge: rund 10 mm, mit zusätzlicher Außenmutter 15 mm.

## Vor dem Druck nachmessen

Diese Parameter stehen oben in `funkpult_cad.py` und beruhen auf Annahmen:

- `DISP_AA_OFF`, `DISP_T`: Lage der aktiven Fläche und Dicke des Waveshare-2,42-Zoll-OLED-Moduls
- `SPK_D`, `SPK_RIM_T`: Randdurchmesser und Randdicke des Lautsprechers
- `SW_X`, `SW_Z`: Lage des Schiebeschalters in der Rückwand
- `PTT_U`: Breite der PTT-Tastenkappe (2u, bei Verkanten 1,5u)
- `FW_WASHER`, `BRG`, `MAG`: Maße von Stahlscheiben, Lagern und Magnet
- `MAG_GAP`: Luftspalt zwischen Magnet und Sensor (1 mm, zulässig bis 2 mm)
- `GN_HOLE_D`, `GN_TAP_D`: Bohrung für das Halsgewinde und Kernloch der Kapsel
- `MICMOD_D`, `MICMOD_T`: Durchmesser und Dicke des Mikrofonmoduls

Nicht erprobt sind der Presssitz der Achse, die Lagersitze, das selbstschneidende Gewinde der
Kapsel und die Standsicherheit mit weit ausgebogenem Hals. Ein schwerer Mikrofon-Schwanenhals aus
Stahl kann das Pult zum Kippen bringen; dann Gewicht in die Bodenplatte kleben.

## Modell neu erzeugen

```
pip install cadquery
python3 funkpult_cad.py ausgabe/                               # Standard
python3 funkpult_cad.py ausgabe/ --schwanenhals --schwungrad   # Variante, Optionen einzeln wählbar
python3 pcb_dxf.py ausgabe/
```

Das Skript prüft dabei alle Teile auf Durchdringung mit Platine, Display, Akku und Lautsprecher
und schreibt das Ergebnis nach `ausgabe/report.json`. Standard, beide Einzeloptionen und die
Kombination sind so geprüft: keine Durchdringung, alle STL-Netze geschlossen.
