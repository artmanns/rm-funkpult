#!/usr/bin/env python3
"""Generates kicad/funkpult.kicad_sch (KiCad 7 format) for the Funkpult control unit.
The NETS table is the design intent; the drawing code must reproduce it and
check_netlist.py compares KiCad's exported netlist against it."""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from schgen import Sch

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'

NETS = {
    'GND': ['J1.A1', 'J1.A12', 'J1.B1', 'J1.B12', 'J1.S1', 'R1.2', 'R2.2', 'U1.2', 'C1.2', 'U2.2', 'R3.2',
            'C2.2', 'J2.2', 'Q1.1', 'R5.2', 'C3.2', 'R7.2', 'C4.2', 'R9.2', 'U3.2', 'C5.2', 'C6.2', 'SW1.3',
            'R10.2', 'U4.1', 'U4.40', 'U4.41', 'C7.2', 'SW2.1', 'SW3.1', 'C8.2', 'C9.2', 'J6.3', 'MK1.3',
            'MK1.2', 'C10.2', 'R12.2', 'U5.3', 'U5.11', 'U5.15', 'U5.17', 'R14.2', 'C11.2', 'C12.2', 'C13.2',
            'C14.2', 'SW4.1', 'J5.2', 'C15.2', 'ENC1.C', 'ENC1.S2', 'C16.2', 'C17.2', 'C18.2', 'SW5.2',
            'SW6.2', 'SW7.2', 'SW8.2', 'D2.2', 'J4.2', 'C19.2', 'C20.2',
            'U6.4', 'C21.2', 'JP1.1', 'SW9.2', 'J7.2', 'J8.1'],
    'VBUS_CONN': ['J1.A4', 'J1.A9', 'J1.B4', 'J1.B9', 'F1.1'],
    'VBUS': ['F1.2', 'U1.5', 'C1.1', 'U2.4', 'D1.2', 'Q2.1', 'R5.1', 'R8.1'],
    'CC1': ['J1.A5', 'R1.1'],
    'CC2': ['J1.B5', 'R2.1'],
    'USB_CONN_DP': ['J1.A6', 'J1.B6', 'U1.1'],
    'USB_CONN_DM': ['J1.A7', 'J1.B7', 'U1.3'],
    'USB_DP': ['U1.6', 'U4.14'],
    'USB_DM': ['U1.4', 'U4.13'],
    'CHG_PROG': ['U2.5', 'R3.1'],
    'CHG_STAT': ['U2.1', 'R4.2', 'U4.23'],
    '+BATT': ['U2.3', 'C2.1', 'Q1.2', 'Q2.3', 'R6.1'],
    'BAT_RAW': ['J2.1', 'Q1.3'],
    'VSYS': ['D1.1', 'Q2.2', 'C3.1', 'U3.1', 'C5.1', 'SW1.1', 'U5.7', 'U5.8', 'C11.1', 'C12.1'],
    'LDO_EN': ['SW1.2', 'R10.1', 'U3.3'],
    '+3V3': ['U3.5', 'C6.1', 'U4.2', 'C8.1', 'C9.1', 'R11.1', 'R4.1', 'MK1.5', 'C10.1', 'R16.1', 'R17.1',
             'R18.1', 'R19.1', 'J4.1', 'C19.1', 'C20.1', 'U6.1', 'C21.1', 'JP1.3', 'J7.1'],
    'VBAT_SENSE': ['R6.2', 'R7.1', 'C4.1', 'U4.39'],
    'VBUS_SENSE': ['R8.2', 'R9.1', 'U4.38'],
    'ESP_EN': ['U4.3', 'R11.2', 'C7.1', 'SW2.2'],
    'BOOT': ['U4.27', 'SW3.2'],
    'PTT': ['U4.4', 'R15.2', 'R16.2', 'C15.1'],
    'PTT_RAW': ['SW4.2', 'J5.1', 'R15.1'],
    'ENC_SW': ['U4.5', 'ENC1.S1', 'R19.2', 'C18.1', 'SW9.1'],
    'ENC_A': ['U4.6', 'ENC1.A', 'R17.2', 'C16.1', 'U6.6'],
    'ENC_B': ['U4.7', 'ENC1.B', 'R18.2', 'C17.1', 'U6.7'],
    'ENC_MODE': ['U6.2', 'JP1.2'],
    'KEY1': ['U4.8', 'SW5.1'], 'KEY2': ['U4.9', 'SW6.1'], 'KEY3': ['U4.10', 'SW7.1'], 'KEY4': ['U4.11', 'SW8.1'],
    'DISP_RST': ['U4.12', 'J4.7'], 'DISP_DC': ['U4.17', 'J4.6'], 'DISP_CS': ['U4.18', 'J4.5'],
    'DISP_MOSI': ['U4.19', 'J4.3'], 'DISP_SCK': ['U4.20', 'J4.4'],
    'LED_TX': ['U4.21', 'R20.1'], 'LED_BUSY': ['U4.22', 'R21.1'],
    'LED_R_A': ['R20.2', 'D2.1'], 'LED_G_A': ['R21.2', 'D2.3'],
    'AMP_DIN': ['U4.24', 'U5.1'], 'AMP_SD': ['U4.25', 'U5.4'],
    'AMP_BCLK': ['U4.34', 'U5.16'], 'AMP_LRCLK': ['U4.35', 'U5.14'],
    'MIC_WS': ['U4.31', 'MK1.1', 'R23.1'], 'MIC_SCK': ['U4.32', 'MK1.4', 'R22.1'], 'MIC_SD': ['U4.33', 'MK1.6', 'R12.1', 'R24.1'],
    'GN_SCK': ['R22.2', 'J7.3'], 'GN_WS': ['R23.2', 'J7.4'], 'GN_SD': ['R24.2', 'J7.5'],
    'UART_RX': ['U4.36', 'J6.2'], 'UART_TX': ['U4.37', 'J6.1'],
    'AMP_GAIN': ['U5.2', 'R14.1'],
    'AMP_OUTP': ['U5.9', 'FB1.1'], 'AMP_OUTN': ['U5.10', 'FB2.1'],
    'SPK_P': ['FB1.2', 'C13.1', 'J3.1'], 'SPK_N': ['FB2.2', 'C14.1', 'J3.2'],
}
NC = ['J1.A8', 'J1.B8', 'U4.15', 'U4.16', 'U4.26', 'U4.28', 'U4.29', 'U4.30', 'U6.3', 'U6.5', 'U6.8']

# GPIO map (pin number on the module -> function), used for the doc table too
GPIO = [
    ('IO1', 39, 'VBAT_SENSE', 'Akkuspannung über Teiler 1:2 (ADC1_CH0)'),
    ('IO2', 38, 'VBUS_SENSE', 'USB-Spannung vorhanden (Teiler 68k/100k)'),
    ('IO4', 4, 'PTT', 'PTT-Taste und externer PTT-Eingang, low-aktiv, RTC-fähig (Wake-up)'),
    ('IO5', 5, 'ENC_SW', 'Taster im Drehgeber, low-aktiv, RTC-fähig'),
    ('IO6', 6, 'ENC_A', 'Drehgeber Spur A (PCNT)'),
    ('IO7', 7, 'ENC_B', 'Drehgeber Spur B (PCNT)'),
    ('IO8', 12, 'DISP_RST', 'Display Reset'),
    ('IO9', 17, 'DISP_DC', 'Display Data/Command'),
    ('IO10', 18, 'DISP_CS', 'Display Chip Select (FSPICS0)'),
    ('IO11', 19, 'DISP_MOSI', 'Display Daten (FSPID)'),
    ('IO12', 20, 'DISP_SCK', 'Display Takt (FSPICLK)'),
    ('IO13', 21, 'LED_TX', 'LED rot: Sender aktiv'),
    ('IO14', 22, 'LED_BUSY', 'LED grün: Squelch offen / verbunden'),
    ('IO15', 8, 'KEY1', 'Softkey F1, low-aktiv, interner Pull-up'),
    ('IO16', 9, 'KEY2', 'Softkey F2'),
    ('IO17', 10, 'KEY3', 'Softkey F3'),
    ('IO18', 11, 'KEY4', 'Softkey F4'),
    ('IO19', 13, 'USB_DM', 'USB D− (natives USB-Serial/JTAG)'),
    ('IO20', 14, 'USB_DP', 'USB D+'),
    ('IO21', 23, 'CHG_STAT', 'Laderegler-Status, low = lädt'),
    ('IO38', 31, 'MIC_WS', 'Mikrofon I2S Word Select'),
    ('IO39', 32, 'MIC_SCK', 'Mikrofon I2S Bit Clock'),
    ('IO40', 33, 'MIC_SD', 'Mikrofon I2S Daten'),
    ('IO41', 34, 'AMP_BCLK', 'Verstärker I2S Bit Clock'),
    ('IO42', 35, 'AMP_LRCLK', 'Verstärker I2S Word Select'),
    ('IO47', 24, 'AMP_DIN', 'Verstärker I2S Daten'),
    ('IO48', 25, 'AMP_SD', 'Verstärker Enable (low = Shutdown)'),
    ('IO0', 27, 'BOOT', 'Boot-Taster'),
    ('TXD0', 37, 'UART_TX', 'Debug-UART'),
    ('RXD0', 36, 'UART_RX', 'Debug-UART'),
]


def build():
    s = Sch('funkpult', 'Funkpult – WLAN-Bedieneinheit für Funkgeräte-Server', '0.2', '2026-11-18',
            company='Entwurf', comments=['Eine Platine für alle Ausführungen, siehe Block Varianten',
                                         'Vor der Fertigung: ERC in KiCad, Footprints und Bezugsquellen prüfen'])
    s.netlist(NETS, NC)

    def vR(ref, x, ytop, value, **kw):
        return s.add(ref, 'Device:R', x, ytop + 3, value=value, fp=kw.pop('fp', R0603), **kw)

    def vC(ref, x, ytop, value, **kw):
        return s.add(ref, 'Device:C', x, ytop + 3, value=value, fp=kw.pop('fp', C0603), **kw)

    def hR(ref, xleft, y, value, **kw):
        return s.add(ref, 'Device:R', xleft + 3, y, rot=90, value=value, fp=kw.pop('fp', R0603), **kw)

    def gnd(pt, drop=0, d='D'):
        p = s._pt(pt)
        if drop:
            q = (p[0], p[1] + drop)
            s.wire(p, q)
            p = q
        s.power('GND', p, d)

    # ------------------------------------------------------------------ USB
    s.rect(10, 14, 84, 70, 'USB-C, ESD-Schutz')
    s.add('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 22, 42, value='USB-C 16P',
          fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', ref_at=(-8, -15.5, 'left'), val_at=(-3, -15.5, 'left'),
          fields={'MPN': 'HRO TYPE-C-31-M-12'})
    s.add('F1', 'Device:Polyfuse_Small', 44, 30, rot=90, value='1.1A', fp='Fuse:Fuse_1206_3216Metric')
    s.wire('J1.A4', 'F1.1')
    s.wire('F1.2', (60, 30))
    s.power('VBUS', (52, 30))
    s.flag((60, 30))
    s.wire('J1.A5', (66, 34))
    vR('R1', 66, 34, '5.1k')
    gnd('R1.2')
    s.wire('J1.B5', (56, 36))
    vR('R2', 56, 36, '5.1k')
    gnd('R2.2')
    a, b = s.P('J1', 'A7'), s.P('J1', 'B7')
    s.wire(a, b)
    s.wire(a, (38, a[1]))
    s.label('USB_CONN_DM', (38, a[1]), 'R')
    a, b = s.P('J1', 'A6'), s.P('J1', 'B6')
    s.wire(a, b)
    s.wire(a, (38, a[1]))
    s.label('USB_CONN_DP', (38, a[1]), 'R')
    s.nc('J1.A8')
    s.nc('J1.B8')
    s.wire('J1.A1', (22, 62))
    s.wire('J1.S1', (16, 62), (22, 62))
    gnd((22, 62))
    s.wire((22, 62), (28, 62))
    s.flag((28, 62))
    s.add('U1', 'Power_Protection:USBLC6-2SC6', 64, 54, ref_at=(-4, -4.2, 'left'), val_at=(1.5, 7.2, 'left'))
    s.stub('U1.1')
    s.stub('U1.3')
    s.stub('U1.6')
    s.stub('U1.4')
    s.wire('U1.5', (64, 48))
    s.power('VBUS', (64, 48))
    gnd('U1.2')

    # -------------------------------------------------------------- charger
    s.rect(86, 14, 188, 70, 'Laden, Akku, Lastumschaltung')
    s.add('D1', 'Device:D_Schottky', 146, 26, rot=180, value='B5819W', fp='Diode_SMD:D_SOD-123',
          ref_at=(-4, -2.2), val_at=(3.5, -2.2))
    s.power('VBUS', (92, 26))
    s.wire((92, 26), 'D1.2')
    vC('C1', 96, 26, '4.7µ')
    gnd('C1.2')
    s.add('U2', 'Battery_Management:MCP73832-2-OT', 112, 36, value='MCP73832T-2ACI/OT',
          ref_at=(-6, -5.2, 'left'), val_at=(1.5, -5.2, 'left'))
    s.wire('U2.4', (112, 26))
    gnd('U2.2')
    s.wire('U2.5', (100, 38))
    vR('R3', 100, 38, '3.3k', ref_at=(-4.5, 2), val_at=(-4.5, 3.8))
    gnd('R3.2')
    s.stub('U2.1')
    s.wire('U2.3', (138, 34), (138, 44))
    s.power('+BATT', (138, 34))
    s.wire((130, 44), (158, 44))
    vC('C2', 130, 44, '4.7µ', ref_at=(-4.5, -1), val_at=(-4.5, 1))
    gnd('C2.2')
    s.add('Q2', 'Device:Q_PMOS_GSD', 160, 32, rot=180, value='DMG3415U', fp='Package_TO_SOT_SMD:SOT-23',
          ref_at=(-9, -1), val_at=(-9, 1))
    s.wire('Q2.2', (158, 26))
    s.wire('Q2.3', (158, 44))
    s.wire('Q2.1', (168, 32))
    s.power('VBUS', (168, 32))
    vR('R5', 168, 32, '100k', ref_at=(-4.5, -0.5), val_at=(-4.5, 1.3))
    gnd('R5.2')
    s.wire('D1.1', (182, 26))
    vC('C3', 176, 26, '10µ', fp=C0805)
    gnd('C3.2')
    s.flag((164, 26))
    s.label('VSYS', (182, 26), 'R')
    s.add('Q1', 'Device:Q_PMOS_GSD', 146, 50, rot=180, value='DMG3415U', fp='Package_TO_SOT_SMD:SOT-23',
          ref_at=(-8, 0), val_at=(-8, 1.8))
    s.wire('Q1.2', (144, 44))
    s.add('J2', 'Connector_Generic:Conn_01x02', 154, 62, value='Akku JST-PH',
          fp='Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal', ref_at=(0, -2.2, 'left'), val_at=(0, 4.2, 'left'))
    s.wire('Q1.3', (144, 62), 'J2.1')
    s.label('BAT_RAW', (144, 58), 'L')
    s.wire('Q1.1', (154, 50), (154, 52))
    gnd((154, 52))
    s.wire('J2.2', (146, 64), (146, 66))
    gnd((146, 66))
    s.text('Akku: LiPo 1S mit Schutzschaltung. Pin 1 = Plus.', 88, 67.5, 1.27)
    s.text('Ladestrom: R3 = 3,3 k → 300 mA (2 k → 500 mA)', 88, 58, 1.27)

    # ------------------------------------------------------------ regulator
    s.rect(190, 14, 318, 70, '3,3-V-Regler, Ein/Aus, Messung')
    s.add('U3', 'Regulator_Linear:AP2112K-3.3', 232, 28, ref_at=(-4, -5.2, 'left'), val_at=(-1, -5.2, 'left'))
    s.wire((198, 26), 'U3.1')
    s.label('VSYS', (198, 26), 'L')
    vC('C5', 204, 26, '1µ', ref_at=(-4, -1), val_at=(-4, 1))
    gnd('C5.2')
    s.add('SW1', 'Switch:SW_SPDT', 214, 38, mirror='y', value='Ein/Aus', fp='Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q',
          ref_at=(0, -3.6), val_at=(0, 4.2))
    s.wire('SW1.1', (208, 36), (208, 26))
    s.wire('SW1.3', (208, 40), (208, 44))
    gnd((208, 44))
    s.wire('SW1.2', (222, 38), (222, 28), 'U3.3')
    vR('R10', 222, 38, '1M')
    gnd('R10.2')
    s.wire('U3.5', (258, 26))
    vC('C6', 244, 26, '10µ', fp=C0805)
    gnd('C6.2')
    s.power('+3V3', (252, 26))
    gnd('U3.2')
    # battery divider
    s.power('+BATT', (272, 20))
    vR('R6', 272, 20, '1M')
    vR('R7', 272, 26, '1M')
    gnd('R7.2')
    vC('C4', 280, 26, '100n')
    s.wire('R6.2', 'C4.1')
    s.wire('C4.2', 'R7.2')
    s.wire('C4.1', (284, 26))
    s.label('VBAT_SENSE', (284, 26), 'R')
    # VBUS divider
    s.power('VBUS', (300, 20))
    vR('R8', 300, 20, '68k', ref_at=(-4, -1), val_at=(-4, 1))
    vR('R9', 300, 26, '100k', ref_at=(-4, -1), val_at=(-4, 1))
    gnd('R9.2')
    s.wire('R8.2', (304, 26))
    s.label('VBUS_SENSE', (304, 26), 'R')
    s.text('SW1 aus: EN = 0 V, Regler aus (< 10 µA aus dem Akku). Laden funktioniert auch ausgeschaltet.', 192, 58, 1.27)

    # ------------------------------------------------------------------ MCU
    s.rect(10, 84, 104, 156, 'ESP32-S3')
    s.add('U4', 'RF_Module:ESP32-S3-WROOM-1', 64, 126, value='ESP32-S3-WROOM-1-N8R2',
          ref_at=(-10, -21.2, 'left'), val_at=(2, 21.6, 'left'))
    for pin in ['39', '38', '4', '5', '6', '7', '12', '17', '18', '19', '20', '21', '22', '8', '9', '27',
                '37', '36', '10', '11', '13', '14', '23', '31', '32', '33', '34', '35', '24', '25']:
        s.stub('U4.' + pin)
    for pin in ['15', '16', '26', '28', '29', '30']:
        s.nc('U4.' + pin)
    s.add('SW2', 'Switch:SW_Push', 24, 108, value='RESET', fp='Button_Switch_SMD:SW_SPST_TL3342',
          ref_at=(0, -3.2), val_at=(0, 2.2))
    s.wire('U4.3', 'SW2.2')
    vR('R11', 40, 102, '10k')
    s.power('+3V3', 'R11.1')
    vC('C7', 34, 108, '1µ')
    gnd('C7.2')
    s.wire('SW2.1', (20, 110))
    gnd((20, 110))
    s.label('ESP_EN', (46, 108), 'R')
    s.add('SW3', 'Switch:SW_Push', 24, 120, value='BOOT', fp='Button_Switch_SMD:SW_SPST_TL3342',
          ref_at=(0, -3.2), val_at=(0, 2.2))
    s.stub('SW3.2')
    s.wire('SW3.1', (20, 122))
    gnd((20, 122))
    hR('R4', 24, 150, '100k')
    s.wire('R4.1', (20, 150))
    s.power('+3V3', (20, 150))
    s.stub('R4.2')
    s.wire('U4.2', (64, 96), (84, 96))
    s.power('+3V3', (64, 96))
    vC('C8', 76, 96, '10µ', fp=C0805)
    gnd('C8.2')
    vC('C9', 84, 96, '100n')
    gnd('C9.2')
    gnd('U4.1', drop=1)

    # -------------------------------------------------------------- display
    s.rect(10, 160, 104, 204, 'Display (SPI), Debug-UART')
    s.add('J4', 'Connector_Generic:Conn_01x07', 20, 190, mirror='y', value='OLED 2.42" SSD1309',
          fp='Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Horizontal', ref_at=(-2, -9.3), val_at=(6, 9.6))
    s.wire('J4.1', (54, 184))
    s.power('+3V3', (38, 184))
    vC('C19', 44, 184, '10µ', fp=C0805)
    gnd('C19.2')
    vC('C20', 54, 184, '100n')
    gnd('C20.2')
    s.wire('J4.2', (40, 186))
    gnd((40, 186))
    for pin in ['3', '4', '5', '6', '7']:
        s.stub('J4.' + pin)
    s.add('J6', 'Connector_Generic:Conn_01x03', 70, 190, mirror='y', value='Debug',
          fp='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', ref_at=(-2, -4.2), val_at=(-1, 4.6))
    s.stub('J6.1')
    s.stub('J6.2')
    s.wire('J6.3', (76, 192), (76, 194))
    gnd((76, 194))
    s.text('J4 Pinfolge wie Waveshare-Kabel: VCC, GND, DIN, CLK, CS, DC, RST', 12, 202.5, 1.27)

    # ---------------------------------------------------------------- audio
    s.rect(108, 84, 230, 156, 'Audio: I2S-Mikrofon, I2S-Verstärker')
    s.add('MK1', 'Sensor_Audio:ICS-43434', 130, 108, ref_at=(-6, 7.4, 'left'), val_at=(2, 7.4, 'left'))
    s.wire('MK1.5', (130, 100), (118, 100))
    s.power('+3V3', (130, 100))
    vC('C10', 118, 100, '100n', ref_at=(-5, -1), val_at=(-5, 1))
    s.wire('MK1.2', 'C10.2')
    gnd('C10.2')
    gnd('MK1.3', drop=1)
    s.stub('MK1.1')
    s.stub('MK1.4')
    s.wire('MK1.6', (148, 110))
    vR('R12', 146, 110, '100k')
    gnd('R12.2')
    s.label('MIC_SD', (148, 110), 'R')
    s.add('U5', 'Audio:MAX98357A', 176, 126, ref_at=(-8, -9.2, 'left'), val_at=(4, 11.4, 'left'),
          value='MAX98357AETE+')
    s.wire('U5.7', (176, 108))
    s.wire((160, 108), (180, 108))
    s.label('VSYS', (180, 108), 'R')
    vC('C11', 166, 108, '10µ', fp=C0805)
    gnd('C11.2')
    vC('C12', 160, 108, '100n', ref_at=(-5, -1), val_at=(-5, 1))
    gnd('C12.2')
    s.wire('U5.3', (174, 138), (178, 138), 'U5.17')
    gnd((176, 138))
    for pin in ['1', '16', '14', '4']:
        s.stub('U5.' + pin)
    s.wire('U5.2', (158, 130))
    vR('R14', 158, 130, 'n.b.', dnp=True, ref_at=(-4.5, 0.5), val_at=(-4.5, 2.2))
    gnd('R14.2')
    s.add('FB1', 'Device:FerriteBead_Small', 196, 116, rot=90, value='220R/2A', fp='Inductor_SMD:L_0603_1608Metric',
          ref_at=(-2.5, -1.7), val_at=(3, -1.7), fields={'MPN': 'MPZ1608S221A'})
    s.add('FB2', 'Device:FerriteBead_Small', 196, 128, rot=90, value='220R/2A', fp='Inductor_SMD:L_0603_1608Metric',
          ref_at=(-2.5, -1.7), val_at=(3, -1.7), fields={'MPN': 'MPZ1608S221A'})
    s.add('J3', 'Connector_Generic:Conn_01x02', 220, 116, value='LS 4 Ω',
          fp='Connector_JST:JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal', ref_at=(0, -2.2, 'left'), val_at=(0, 4.4, 'left'))
    s.wire('U5.9', (188, 120), (188, 116), 'FB1.1')
    s.wire('FB1.2', 'J3.1')
    vC('C13', 204, 116, '220p')
    gnd('C13.2')
    s.wire('U5.10', (190, 122), (190, 128), 'FB2.1')
    s.wire('FB2.2', (212, 128), (212, 118), 'J3.2')
    vC('C14', 204, 128, '220p')
    gnd('C14.2')
    s.text('R14 (GAIN): offen = 9 dB, 0 Ω = 12 dB, 100 k = 15 dB', 110, 150, 1.27)
    s.text('MK1 Bottom-Port: Schallloch Ø 1 mm durch die Platine', 110, 153, 1.27)

    # ------------------------------------------------------------- controls
    s.rect(234, 84, 318, 184, 'Bedienelemente')
    s.add('SW4', 'Switch:SW_Push', 246, 100, value='PTT (MX)', fp='Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB',
          ref_at=(0, -3.2), val_at=(0, 2.2))
    s.wire('SW4.1', (240, 100), (240, 102))
    gnd((240, 102))
    hR('R15', 261, 100, '1k')
    s.wire('SW4.2', 'R15.1')
    s.wire('R15.2', (284, 100))
    vR('R16', 274, 94, '10k')
    s.power('+3V3', 'R16.1')
    vC('C15', 280, 100, '100n')
    gnd('C15.2')
    s.label('PTT', (284, 100), 'R')
    s.add('J5', 'Connector_Generic:Conn_01x02', 262, 108, value='PTT ext.',
          fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', ref_at=(2.5, 0, 'left'), val_at=(2.5, 1.8, 'left'))
    s.wire('J5.1', (258, 100))
    s.wire('J5.2', (254, 110), (254, 112))
    gnd((254, 112))
    s.label('PTT_RAW', (251, 100), 'R')

    s.add('ENC1', 'Device:RotaryEncoder_Switch', 262, 132, value='PEC11R-4220F-S0024',
          fp='Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm', ref_at=(0, -5.6), val_at=(-2, 6.4))
    s.stub('ENC1.A', 6)
    s.stub('ENC1.B', 6)
    s.wire('ENC1.C', (242, 132), (242, 138))
    gnd((242, 138))
    s.stub('ENC1.S1')
    s.wire('ENC1.S2', (274, 134), (274, 136))
    gnd((274, 136))
    for x, rr, cc, cv in [(280, 'R17', 'C16', '10n'), (294, 'R18', 'C17', '10n'), (308, 'R19', 'C18', '100n')]:
        vR(rr, x, 124, '10k', ref_at=(2, -1.8, 'left'), val_at=(2, -0.2, 'left'))
        s.power('+3V3', rr + '.1')
        vC(cc, x, 130, cv, ref_at=(2, 0.6, 'left'), val_at=(2, 2.2, 'left'))
        gnd(cc + '.2')
        s.wire(rr + '.2', (x + 2, 130))
        s.label(s.net_of(rr, '2'), (x + 2, 130), 'R')

    for i, ref in enumerate(['SW5', 'SW6', 'SW7', 'SW8']):
        y = 150 + 8 * i
        s.add(ref, 'Switch:SW_Push', 250, y, value='F%d' % (i + 1), fp='Button_Switch_THT:SW_PUSH_6mm_H5mm',
              ref_at=(-2.5, -3.2), val_at=(2.5, -3.2))
        s.stub(ref + '.1')
        s.wire(ref + '.2', (260, y))
    s.wire((260, 150), (260, 176))
    gnd((260, 176))

    s.add('D2', 'Device:LED_Dual_AKA', 300, 160, mirror='y', value='Duo-LED rt/gn', fp='LED_THT:LED_D3.0mm-3',
          ref_at=(0, -5), val_at=(-3, 5.4))
    hR('R20', 283, 158, '330', ref_at=(-2.2, -1.6), val_at=(2.2, -1.6))
    hR('R21', 283, 162, '330', ref_at=(-2.2, 1.8), val_at=(2.2, 1.8))
    s.wire('R20.2', 'D2.1')
    s.wire('R21.2', 'D2.3')
    s.stub('R20.1')
    s.stub('R21.1')
    s.wire('D2.2', (310, 160), (310, 162))
    gnd((310, 162))
    s.text('D2: Pin 1 = rot (TX), Pin 3 = grün (BUSY), Pin 2 = Kathode', 264, 171, 1.27)
    s.text('SW4: MX-kompatibler Tastaturschalter, 2u-Kappe', 236, 119, 1.27)
    s.text('Schwungrad-Variante: ENC1 entfällt, U6 und SW9 bestücken', 236, 144, 1.27)
    s.text('F1–F4: interne Pull-ups des ESP32', 264, 182, 1.27)

    # ------------------------------------------------------------ mechanics
    s.rect(234, 186, 318, 197, None)
    for i in range(6):
        s.add('H%d' % (i + 1), 'Mechanical:MountingHole', 240 + 13 * i, 191, value='M3',
              fp='MountingHole:MountingHole_3.2mm_M3', ref_at=(2.5, -0.8, 'left'), val_at=(2.5, 1, 'left'), in_bom=False)

    # ------------------------------------------------------------- variants
    s.rect(108, 160, 230, 204, 'Varianten: Magnetsensor, Taste SEL, Schwanenhals-Mikro')
    s.add('U6', 'Sensor_Magnetic:MT6701CT', 150, 184, value='MT6701CT', fp='Package_SO:SOP-8_3.9x4.9mm_P1.27mm',
          ref_at=(2, -13.2, 'left'), val_at=(5.5, -13.2, 'left'), fields={'MPN': 'MT6701CT-STD'})
    s.wire('U6.1', (142, 170))
    s.power('+3V3', (146, 170))
    vC('C21', 142, 170, '100n', ref_at=(-4.5, -1), val_at=(-4.5, 1))
    gnd('C21.2')
    gnd('U6.4')
    s.stub('U6.6')
    s.stub('U6.7')
    for pin in ['8', '3', '5']:
        s.nc('U6.' + pin)
    s.add('JP1', 'Jumper:SolderJumper_3_Open', 126, 184, rot=90, value='MODE',
          fp='Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm', ref_at=(-5, -1), val_at=(-5, 1))
    s.wire('JP1.2', 'U6.2')
    s.label('ENC_MODE', (131, 184), 'R')
    s.power('+3V3', 'JP1.3')
    gnd('JP1.1')
    for y, ref, val in [(168, 'R22', '33'), (172, 'R23', '33'), (176, 'R24', '100')]:
        hR(ref, 190, y, val, ref_at=(-2.2, -1.6), val_at=(2.2, -1.6))
        s.stub(ref + '.1')
        s.stub(ref + '.2')
    s.add('SW9', 'Switch:SW_Push', 184, 190, value='SEL', fp='Button_Switch_THT:SW_PUSH_6mm_H5mm',
          ref_at=(0, -3.2), val_at=(0, 2.2))
    s.stub('SW9.1')
    s.wire('SW9.2', (192, 190), (192, 198))
    s.add('J8', 'Connector_Generic:Conn_01x01', 200, 198, value='GND Schwanenhals',
          fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm', ref_at=(0, -2.2, 'left'), val_at=(2.5, 0, 'left'))
    s.wire('J8.1', (192, 198))
    gnd((192, 198))
    s.add('J7', 'Connector_Generic:Conn_01x05', 224, 186, value='Mikro ext.',
          fp='Connector_JST:JST_PH_S5B-PH-SM4-TB_1x05-1MP_P2.00mm_Horizontal', ref_at=(1, -6.6), val_at=(0, 7.2))
    s.wire('J7.1', (212, 182), (212, 180))
    s.power('+3V3', (212, 180))
    s.wire('J7.2', (208, 184), (208, 190))
    gnd((208, 190))
    for pin in ['3', '4', '5']:
        s.stub('J7.' + pin)
    s.text('Schwungrad: U6 statt ENC1, C16/C17 offen', 110, 200.5, 1.27)
    s.text('JP1: MODE nach Datenblatt (ABZ oder I2C)', 110, 203, 1.27)
    s.text('Modul: L/R an 3V3 (rechter Kanal)', 196, 203, 1.27)
    return s


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/funkpult/kicad'
    s = build()
    s.write(os.path.join(out, 'funkpult.kicad_sch'))
    with open(os.path.join(out, 'funkpult.kicad_pro'), 'w') as f:
        json.dump({'board': {}, 'meta': {'filename': 'funkpult.kicad_pro', 'version': 1}, 'schematic': {},
                   'sheets': [[s.root_uuid, '']], 'text_variables': {}}, f, indent=2)
    with open(os.path.join(out, 'intent.json'), 'w') as f:
        json.dump({'nets': NETS, 'nc': NC, 'gpio': GPIO,
                   'parts': {r: {'value': c.value, 'fp': c.fp, 'lib': c.lib_id, 'dnp': c.dnp, 'fields': c.fields}
                             for r, c in s.comps.items()}}, f, indent=1, ensure_ascii=False)
    print('written', len(s.comps), 'parts,', len(NETS), 'nets')
