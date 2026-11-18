# Funkpult – WLAN-Bedieneinheit für den Funkgeräte-Server

Stand: Entwurf 0.2, 18.11.2026. Nichts davon ist gebaut oder gedruckt.

Vollständiges Dokument mit Schaltplan, Gehäuse, Variante und Protokoll:
https://claude.ai/artifact/7FqkJCM84GRLLaC8ZpAeKA

## Was es ist

Pultgerät mit PTT-Taste, Mikrofon, VFO-Drehknopf, vier Softkeys, Lautsprecher und OLED, das per
WLAN am Funkgeräte-Server hängt. Die Bedieneinheit ist ein dünner Client: Der Server entscheidet,
was Softkeys und Drehknopf gerade tun.

## Festgelegt

- Bauform: Pultgehäuse, 18° geneigt, 190 × 118 mm Standfläche, 3D-Druck, Frontplatte auf dem Druckbett
- Controller: ESP32-S3-WROOM-1-N8R2, natives USB zum Flashen; Firmware in Rust geplant, existiert noch nicht
- Strom: LiPo 103450 mit 2000 mAh, Laden über USB-C (MCP73832, 300 mA), Lastumschaltung, AP2112K-3.3
- Audio: I2S-MEMS-Mikrofon ICS-43434, Verstärker MAX98357A, Lautsprecher Ø 40 mm
- Anzeige: Waveshare 2,42-Zoll-OLED, SSD1309, SPI
- Bedienung: MX-Schalter mit 2u-Kappe als PTT, Bourns PEC11R als Drehgeber, vier Taster, Duo-LED
- Platine: eigene Platine in KiCad, 118 × 101 mm, SMD unten, Bedienelemente oben; eine Platine für alle Ausführungen

## Variante (0.2)

- Schwanenhals: zweites I2S-Mikrofon (INMP441-Modul) in gedruckter Kapsel an einem Hals mit
  M10 × 1; Stecker J7. Einbaumikrofon im linken, Schwanenhals im rechten Kanal desselben I2S-Busses.
- Schwungrad-Knopf: Ø 50 mm mit drei Stahlscheiben M24 (97 g) auf zwei Kugellagern 688, läuft
  nach einem Schubs aus. Kein Motor. Abtastung berührungslos mit Magnet Ø 8 × 2,5 mm und MT6701
  (U6) statt des Rast-Drehgebers; Taste SEL (SW9) ersetzt dessen Taster.
- Ein Motor (BLDC mit Feldregelung) wäre nur für per Software schaltbare Rastung nötig und ist
  nicht eingeplant.

## GPIO-Belegung (Kurzfassung)

| Funktion | GPIO |
| --- | --- |
| PTT, Taste SEL bzw. Drehgeber-Taster | IO4, IO5 |
| Drehgeber A/B bzw. MT6701 A/B oder I2C | IO6, IO7 |
| Display RST, DC, CS, MOSI, SCK | IO8 bis IO12 |
| LED TX, LED BUSY | IO13, IO14 |
| Softkeys F1 bis F4 | IO15 bis IO18 |
| USB D−/D+ | IO19, IO20 |
| Mikrofon WS, SCK, SD | IO38, IO39, IO40 |
| Verstärker BCLK, LRCLK, DIN, Enable | IO41, IO42, IO47, IO48 |
| Akkuspannung, USB-Erkennung, Ladestatus | IO1, IO2, IO21 |

## Protokoll FPP/1 (Kurzfassung)

- Eine WebSocket-Verbindung `ws://<server>:<port>/funkpult/v1`, Subprotokoll `fpp.v1`, Dienst per mDNS `_funkpult._tcp`
- JSON-Textframes: `hello`, `enc`, `key`, `ptt`, `stat` von der Bedieneinheit; `welcome`, `state`, `ui`, `menu`, `err` vom Server
- Binärframes mit 8 Byte Kopf (type, flags, seq, ts) für Audio; Standard PCM 16 Bit, 16 kHz, 20 ms, Opus optional
- PTT-Sicherheit: Der Server tastet ab, wenn Audioframes länger als `ptt_timeout_ms` (300) ausbleiben, bei Verbindungsabbruch und nach `tot_s` (180)

## Geprüft und offen

- Geprüft: Netzliste aus KiCad stimmt Pin für Pin mit der Soll-Netzliste überein (83 Positionen,
  56 Netze). Gehäuse in vier Ausführungen ohne Durchdringung, alle STL-Netze geschlossen.
- Offen: ERC in KiCad, Layout der Platine, Firmware, Serverseite des Protokolls.
- Nachmessen: Display (Lage der aktiven Fläche, Dicke), Lautsprecherrand, Schiebeschalter.
- Variante: Pegel am MODE-Pin des MT6701 und Auflösung ab Werk im Herstellerdatenblatt klären;
  Presssitz der Achse, Lagersitze, Gewinde der Mikrofonkapsel und Standsicherheit mit Hals erproben.

## Dateien

`funkpult_kicad.zip` (Schaltplan, PDF, Stückliste, Netzliste, Generator), `funkpult_gehaeuse.zip`
(STL, STEP, CadQuery-Modell, DXF mit Platinenmaßen, Ordner `variante/`), `funkpult_pitch.mp4`.
