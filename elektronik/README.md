# Funkpult – Schaltplan

WLAN-Bedieneinheit für einen Funkgeräte-Server: ESP32-S3, I2S-Mikrofon, I2S-Verstärker,
OLED, Drehgeber, PTT, vier Softkeys, LiPo mit USB-C-Ladung. Stand: Entwurf 0.2, 18.11.2026.

Neu in 0.2: Block „Varianten“ mit Magnetsensor U6 für den Schwungrad-Knopf, Taste SEL (SW9)
und Stecker J7 für ein zweites Mikrofon am Schwanenhals. Die Platine ist für alle Ausführungen
dieselbe; unterschieden wird nur bei der Bestückung.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `funkpult.kicad_sch`, `funkpult.kicad_pro` | KiCad-Projekt, Dateiformat KiCad 7 (öffnet auch in neueren Versionen) |
| `funkpult_schaltplan.pdf` | Schaltplan als PDF, ein A3-Blatt |
| `funkpult_stueckliste.csv` | Stückliste, Semikolon-getrennt, UTF-8; Spalte „Variante“ nennt die Ausführung, Typen sind Vorschläge |
| `funkpult.net` | Von KiCad exportierte Netzliste |
| `quellen/` | Python-Generator, aus dem Schaltplan und Stückliste erzeugt wurden |

## Stand der Prüfung

- Geprüft: Die von KiCad exportierte Netzliste stimmt Pin für Pin mit der Soll-Netzliste
  (Tabelle `NETS` in `quellen/gen_funkpult.py`) überein: 83 Positionen, 56 Netze.
- Offen: ERC in KiCad, Footprint des Drehgebers (eingetragen ist der pin-kompatible Alps EC11E),
  Pegel am MODE-Pin des MT6701 (siehe unten), Bezugsquellen.

## Bestückung

- Alle SMD-Teile auf der Platinenunterseite (eine Bestückungsseite beim Fertiger).
- THT-Teile zur Frontplatte hin auf der Oberseite, von Hand: ENC1, SW4 bis SW8, D2.
- THT-Teile auf der Unterseite, von Hand: J3 bis J6, SW1.
- R14 bleibt unbestückt (Verstärkung 9 dB); 0 Ω ergibt 12 dB, 100 kΩ ergibt 15 dB.

### Ausführungen

| Ausführung | bestücken | weglassen |
| --- | --- | --- |
| Rast-Drehgeber (Standard) | ENC1, C16, C17 | U6, C21, JP1, SW9 |
| Schwungrad-Knopf | U6, C21, JP1, SW9 | ENC1, C16, C17 |
| Schwanenhals-Mikrofon (zusätzlich) | J7, J8, R22, R23, R24 | – |

- U6 (MT6701CT, SOP-8) sitzt als einziges SMD-Teil auf der Oberseite, mittig unter der Knopfachse,
  und wird von Hand gelötet. Der Magnet dreht 1 mm darüber.
- JP1 legt den MODE-Pin von U6 an 3,3 V oder Masse und wählt damit zwischen A/B-Ausgabe und
  I2C/SSI. Welcher Pegel welche Betriebsart wählt, steht in der verwendeten Datenblattkopie
  nicht; vor dem Schließen im Herstellerdatenblatt nachlesen. Die Auflösung der A/B-Ausgabe
  lässt sich nur mit mehr als 4,5 V Versorgung umprogrammieren, also nicht auf dieser Platine.
  Ausweg ohne Programmierung: I2C wählen und den Winkel lesen (Adresse 0x06, IO6 = SDA,
  IO7 = SCL, Pull-ups R17 und R18 sind vorhanden).
- SW9 (Taste SEL) liegt an ENC_SW und ersetzt den Taster des Drehgebers.
- J7 führt 3,3 V, Masse, SCK, WS und SD zum Mikrofonmodul am Schwanenhals. Das Modul wird mit
  L/R an 3,3 V angeschlossen und sendet damit im rechten Kanal; das Einbaumikrofon MK1 bleibt
  im linken. J8 ist das Lötpad für das Massekabel zum Schwanenhals.

## Hinweise zum Layout

- I2S-Leitungen kurz halten, Mikrofon mindestens 20 mm von der Antenne entfernt.
- Antennenbereich des ESP32-Moduls kupferfrei halten.
- USB D+ und D− als 90-Ω-Paar über U1 führen, Schirm der Buchse an Masse.
- Q1 ist der Verpolschutz des Akkus, Q2 und D1 schalten zwischen Akku und USB um.
- IO3, IO45, IO46 sowie IO35 bis IO37 bleiben unbeschaltet.

Die mechanischen Positionen der Bedienelemente stehen in [`../gehaeuse/platine_mechanik.dxf`](../gehaeuse/platine_mechanik.dxf).

## Generator (optional)

Wer im KiCad-Editor weiterarbeitet, braucht den Generator nicht. Zum Neuerzeugen:

```
python3 quellen/gen_funkpult.py <zielordner>
kicad-cli sch export netlist --format kicadsexpr -o <zielordner>/funkpult.net <zielordner>/funkpult.kicad_sch
python3 quellen/check_netlist.py <zielordner>
python3 quellen/make_bom.py <zielordner>
```

Der Generator liest die KiCad-Symbolbibliotheken aus `/usr/share/kicad/symbols`.
