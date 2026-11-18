"""Tiny KiCad 7 schematic writer: symbols on a 1.27 mm grid, wires, labels,
power symbols, auto-split of wires at connection points and auto-junctions.
Coordinates passed to the API are in grid units (1 g = 1.27 mm)."""
import uuid, hashlib
from sexp import Sym, dump, find, first
import symlib

G = 1.27
S = Sym


def _uuid(seed):
    """Deterministic UUIDs so regenerated files diff cleanly."""
    return str(uuid.UUID(hashlib.md5(seed.encode()).hexdigest()))


DIRS = {'R': (1, 0), 'L': (-1, 0), 'U': (0, -1), 'D': (0, 1)}


class Comp:
    def __init__(self, sch, ref, lib_id, x, y, rot=0, mirror=None, value=None, fp=None,
                 fields=None, dnp=False, ref_at=None, val_at=None, hide_value=False, in_bom=True):
        self.sch, self.ref, self.lib_id = sch, ref, lib_id
        self.x, self.y, self.rot, self.mirror = x, y, rot, mirror
        self.symdef = sch.use(lib_id)
        self.pinlist = symlib.pins(self.symdef)
        self.bynum = {p['number']: p for p in self.pinlist}
        props = {p[1]: p[2] for p in find(self.symdef, 'property')}
        self.value = value if value is not None else props.get('Value', '')
        self.fp = fp if fp is not None else props.get('Footprint', '')
        self.datasheet = props.get('Datasheet', '~')
        self.fields = fields or {}
        self.dnp = dnp
        self.ref_at, self.val_at = ref_at, val_at
        self.hide_value = hide_value
        self.in_bom = in_bom
        assert mirror is None or rot == 0, 'mirror only supported at rot 0'

    # local library coords (mm, y up) -> sheet offset in mm
    def _lin(self, px, py):
        if self.mirror == 'y':
            px = -px
        if self.mirror == 'x':
            py = -py
        r = self.rot
        if r == 0:
            return px, -py
        if r == 90:
            return -py, -px
        if r == 180:
            return -px, py
        if r == 270:
            return py, px
        raise ValueError(r)

    def pin(self, num):
        """Sheet position (grid units) of the connection point of pin `num`."""
        p = self.bynum[num]
        dx, dy = self._lin(p['x'], p['y'])
        gx, gy = self.x + dx / G, self.y + dy / G
        assert abs(gx - round(gx)) < 1e-6 and abs(gy - round(gy)) < 1e-6, (self.ref, num, gx, gy)
        return (int(round(gx)), int(round(gy)))

    def pdir(self, num):
        """Unit vector (sheet) pointing away from the body at pin `num`."""
        import math
        p = self.bynum[num]
        a = math.radians(p['angle'])
        ox, oy = -math.cos(a), -math.sin(a)
        dx, dy = self._lin(ox, oy)
        return (int(round(dx)), int(round(dy)))

    def bbox(self):
        """Approximate body bbox (grid units) from pin inner ends."""
        import math
        xs, ys = [], []
        for p in self.pinlist:
            a = math.radians(p['angle'])
            ix, iy = p['x'] + math.cos(a) * p['length'], p['y'] + math.sin(a) * p['length']
            dx, dy = self._lin(ix, iy)
            xs.append(self.x + dx / G)
            ys.append(self.y + dy / G)
        if not xs:
            return self.x, self.y, self.x, self.y
        return min(xs), min(ys), max(xs), max(ys)


class Sch:
    def __init__(self, project, title, rev, date, company='', comments=(), paper='A3'):
        self.project = project
        self.root_uuid = _uuid('root:' + project)
        self.title, self.rev, self.date, self.company, self.comments, self.paper = title, rev, date, company, comments, paper
        self.libsyms = {}
        self.comps = {}
        self.wires = []          # ((x1,y1),(x2,y2)) grid units
        self.labels = []         # (net, (x,y), dir)
        self.pwr = []            # (libid, (x,y), rot, refnum)
        self.ncs = []
        self.texts = []
        self.rects = []
        self.pin_net = {}        # (ref, pin) -> net (intent)
        self.pin_done = set()    # pins that have been drawn/connected
        self.npwr = 0
        self.nflg = 0

    # ---- library -------------------------------------------------------
    def use(self, lib_id):
        if lib_id not in self.libsyms:
            self.libsyms[lib_id] = symlib.load(lib_id)
        return self.libsyms[lib_id]

    # ---- intent ----------------------------------------------------------
    def netlist(self, nets, nc=()):
        """nets: {name: ['REF.PIN', ...]}; nc: ['REF.PIN', ...]"""
        self.nets = nets
        for net, pins in nets.items():
            for rp in pins:
                ref, pin = rp.split('.', 1)
                assert (ref, pin) not in self.pin_net, 'pin in two nets: ' + rp
                self.pin_net[(ref, pin)] = net
        self.nc_intent = set(tuple(rp.split('.', 1)) for rp in nc)

    def net_of(self, ref, pin):
        return self.pin_net[(ref, pin)]

    # ---- placement -------------------------------------------------------
    def add(self, ref, lib_id, x, y, **kw):
        assert ref not in self.comps, ref
        c = Comp(self, ref, lib_id, x, y, **kw)
        self.comps[ref] = c
        return c

    def P(self, ref, pin):
        self.pin_done.add((ref, pin))
        return self.comps[ref].pin(pin)

    def wire(self, *pts):
        pts = [self._pt(p) for p in pts]
        for a, b in zip(pts, pts[1:]):
            assert a[0] == b[0] or a[1] == b[1], ('diagonal wire', a, b)
            if a != b:
                self.wires.append((a, b))
        return pts[-1]

    def _pt(self, p):
        if isinstance(p, str):
            ref, pin = p.split('.', 1)
            return self.P(ref, pin)
        return (int(p[0]), int(p[1]))

    def label(self, net, pt, d='R'):
        self.labels.append((net, self._pt(pt), d))

    def stub(self, refpin, length=2, net=None, d=None):
        """Short wire from a pin outward, ending in a net label."""
        ref, pin = refpin.split('.', 1)
        c = self.comps[ref]
        p0 = self.P(ref, pin)
        dx, dy = DIRS[d] if d else c.pdir(pin)
        p1 = (p0[0] + dx * length, p0[1] + dy * length)
        self.wire(p0, p1)
        net = net or self.net_of(ref, pin)
        dd = {(1, 0): 'R', (-1, 0): 'L', (0, -1): 'U', (0, 1): 'D'}[(dx, dy)]
        self.label(net, p1, dd)
        return p1

    def power(self, name, pt, d=None):
        """Power symbol with its pin at pt. d = direction the graphic points."""
        pt = self._pt(pt)
        up_style = name not in ('GND',)
        if d is None:
            d = 'U' if up_style else 'D'
        if up_style:
            rot = {'U': 0, 'L': 90, 'D': 180, 'R': 270}[d]
        else:
            rot = {'D': 0, 'R': 90, 'U': 180, 'L': 270}[d]
        self.npwr += 1
        self.use('power:' + name)
        self.pwr.append(('power:' + name, pt, rot, '#PWR%03d' % self.npwr, name, d))

    def flag(self, pt, d='U'):
        pt = self._pt(pt)
        self.nflg += 1
        self.use('power:PWR_FLAG')
        rot = {'U': 0, 'L': 90, 'D': 180, 'R': 270}[d]
        self.pwr.append(('power:PWR_FLAG', pt, rot, '#FLG%02d' % self.nflg, 'PWR_FLAG', d))

    def nc(self, refpin):
        ref, pin = refpin.split('.', 1)
        assert (ref, pin) in self.nc_intent, 'not declared NC: ' + refpin
        self.ncs.append(self.P(ref, pin))

    def text(self, s, x, y, size=1.27, bold=False):
        self.texts.append((s, x, y, size, bold))

    def rect(self, x1, y1, x2, y2, title=None):
        self.rects.append((x1, y1, x2, y2))
        if title:
            self.text(title, x1 + 1.5, y1 + 3.2, size=2.0, bold=True)

    # ---- output ----------------------------------------------------------
    def _split_and_junctions(self):
        pts = set()
        for c in self.comps.values():
            for p in c.pinlist:
                pts.add(c.pin(p['number']))
        for _, pt, _d in self.labels:
            pts.add(pt)
        for it in self.pwr:
            pts.add(it[1])
        for a, b in self.wires:
            pts.add(a)
            pts.add(b)
        segs = []
        for a, b in self.wires:
            inner = []
            for p in pts:
                if p == a or p == b:
                    continue
                if a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1]):
                    inner.append(p)
                elif a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]):
                    inner.append(p)
            chain = sorted([a, b] + inner)
            for u, v in zip(chain, chain[1:]):
                segs.append((u, v))
        segs = sorted(set(tuple(sorted(s)) for s in segs))
        ends = {}
        for a, b in segs:
            ends[a] = ends.get(a, 0) + 1
            ends[b] = ends.get(b, 0) + 1
        pinpts = {}
        for c in self.comps.values():
            seen = set()
            for p in c.pinlist:
                q = c.pin(p['number'])
                if q not in seen:           # stacked pins count once
                    seen.add(q)
                    pinpts[q] = pinpts.get(q, 0) + 1
        for it in self.pwr:
            pinpts[it[1]] = pinpts.get(it[1], 0) + 1
        junctions = [p for p, n in ends.items() if n >= 3 or (n >= 2 and pinpts.get(p, 0) >= 1)]
        return segs, sorted(junctions)

    def check_complete(self):
        """Every pin must have intent (net or NC) and something attached at its end."""
        attached = set(self.ncs)
        for a, b in self.wires:
            if a[0] == b[0]:
                for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                    attached.add((a[0], y))
            else:
                for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
                    attached.add((x, a[1]))
        for _n, pt, _d in self.labels:
            attached.add(pt)
        for it in self.pwr:
            attached.add(it[1])
        missing = []
        for ref, c in self.comps.items():
            for p in c.pinlist:
                key = (ref, p['number'])
                if p['etype'] == 'no_connect':
                    continue
                if key not in self.pin_net and key not in self.nc_intent:
                    missing.append('no intent: %s.%s (%s)' % (ref, p['number'], p['name']))
                elif c.pin(p['number']) not in attached:
                    missing.append('nothing attached: %s.%s (%s)' % (ref, p['number'], p['name']))
        for (ref, pin) in list(self.pin_net) + list(self.nc_intent):
            if ref not in self.comps:
                missing.append('intent for unplaced part: %s.%s' % (ref, pin))
            elif pin not in self.comps[ref].bynum:
                missing.append('intent for unknown pin: %s.%s' % (ref, pin))
        return missing

    def _eff(self, size=1.27, justify=None, hide=False, bold=False):
        font = [S('font'), [S('size'), size, size]]
        if bold:
            font.append(S('bold'))
        e = [S('effects'), font]
        if justify:
            e.append([S('justify')] + [S(j) for j in justify.split()])
        if hide:
            e.append(S('hide'))
        return e

    def _prop(self, name, val, x, y, ang=0, **kw):
        return [S('property'), name, val, [S('at'), x * G, y * G, ang], self._eff(**kw)]

    def _field_pos(self, c):
        """Return (ref_xyaj, val_xyaj): x, y (grid), angle, justify."""
        x0, y0, x1, y1 = c.bbox()
        ang = 90 if c.rot in (90, 270) else 0
        two_pin = len({c.pin(p['number']) for p in c.pinlist}) == 2
        if c.ref_at or c.val_at:
            pass
        if two_pin and c.rot in (0, 180):
            r = (c.x + 2, c.y - 1, 0, 'left')
            v = (c.x + 2, c.y + 1, 0, 'left')
        elif two_pin:
            r = (c.x - 2.2, c.y - 1.7, ang, None)
            v = (c.x + 2.2, c.y - 1.7, ang, None)
        else:
            r = (x0, y0 - 1.2, ang, 'left' if c.rot == 0 and not c.mirror else None)
            v = (x0, y1 + 1.5, ang, 'left' if c.rot == 0 and not c.mirror else None)
        if c.ref_at:
            r = (c.x + c.ref_at[0], c.y + c.ref_at[1], ang, c.ref_at[2] if len(c.ref_at) > 2 else None)
        if c.val_at:
            v = (c.x + c.val_at[0], c.y + c.val_at[1], ang, c.val_at[2] if len(c.val_at) > 2 else None)
        return r, v

    def to_sexp(self):
        segs, junctions = self._split_and_junctions()
        out = [S('kicad_sch'), [S('version'), 20230121], [S('generator'), S('eeschema')],
               [S('uuid'), S(self.root_uuid)], [S('paper'), self.paper]]
        tb = [S('title_block'), [S('title'), self.title], [S('date'), self.date], [S('rev'), self.rev],
              [S('company'), self.company]]
        for i, cmt in enumerate(self.comments, 1):
            tb.append([S('comment'), i, cmt])
        out.append(tb)
        out.append([S('lib_symbols')] + [self.libsyms[k] for k in sorted(self.libsyms)])
        for p in junctions:
            out.append([S('junction'), [S('at'), p[0] * G, p[1] * G], [S('diameter'), 0], [S('color'), 0, 0, 0, 0],
                        [S('uuid'), S(_uuid('j%s' % (p,)))]])
        for p in self.ncs:
            out.append([S('no_connect'), [S('at'), p[0] * G, p[1] * G], [S('uuid'), S(_uuid('nc%s' % (p,)))]])
        for a, b in segs:
            out.append([S('wire'), [S('pts'), [S('xy'), a[0] * G, a[1] * G], [S('xy'), b[0] * G, b[1] * G]],
                        [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
                        [S('uuid'), S(_uuid('w%s%s' % (a, b)))]])
        for (x1, y1, x2, y2) in self.rects:
            out.append([S('rectangle'), [S('start'), x1 * G, y1 * G], [S('end'), x2 * G, y2 * G],
                        [S('stroke'), [S('width'), 0.2], [S('type'), S('dash')]],
                        [S('fill'), [S('type'), S('none')]], [S('uuid'), S(_uuid('r%s' % ((x1, y1, x2, y2),)))]])
        for (s, x, y, size, bold) in self.texts:
            out.append([S('text'), s, [S('at'), x * G, y * G, 0], self._eff(size=size, justify='left bottom', bold=bold),
                        [S('uuid'), S(_uuid('t%s%s%s' % (s, x, y)))]])
        for i, (net, pt, d) in enumerate(self.labels):
            ang, just = {'R': (0, 'left bottom'), 'L': (180, 'right bottom'), 'U': (90, 'left bottom'),
                         'D': (270, 'right bottom')}[d]
            out.append([S('label'), net, [S('at'), pt[0] * G, pt[1] * G, ang], [S('fields_autoplaced')],
                        self._eff(justify=just), [S('uuid'), S(_uuid('l%d%s%s' % (i, net, pt)))]])
        inst = lambda ref: [S('instances'), [S('project'), self.project,
                            [S('path'), '/' + self.root_uuid, [S('reference'), ref], [S('unit'), 1]]]]
        for (lib_id, pt, rot, ref, name, d) in self.pwr:
            x, y = pt
            off = {'U': (0, -3.2), 'D': (0, 3.6), 'L': (-3.2, 0), 'R': (3.2, 0)}[d]
            if name == 'GND':
                off = {'D': (0, 3.9), 'U': (0, -3.9), 'L': (-4.2, 0), 'R': (4.2, 0)}[d]
            if name == 'PWR_FLAG':
                off = {'U': (0, -4.0), 'D': (0, 4.0), 'L': (-6.5, 0), 'R': (6.5, 0)}[d]
            sdef = self.libsyms[lib_id]
            node = [S('symbol'), [S('lib_id'), lib_id], [S('at'), x * G, y * G, rot], [S('unit'), 1],
                    [S('in_bom'), S('yes')], [S('on_board'), S('yes')], [S('dnp'), S('no')],
                    [S('uuid'), S(_uuid('ps' + ref))],
                    self._prop('Reference', ref, x, y, hide=True),
                    [S('property'), 'Value', name, [S('at'), x * G + off[0], y * G + off[1], 0], self._eff()],
                    self._prop('Footprint', '', x, y, hide=True),
                    self._prop('Datasheet', '', x, y, hide=True),
                    [S('pin'), '1', [S('uuid'), S(_uuid('pp' + ref))]], inst(ref)]
            out.append(node)
        for ref, c in self.comps.items():
            at = [S('at'), c.x * G, c.y * G, c.rot]
            node = [S('symbol'), [S('lib_id'), c.lib_id], at]
            if c.mirror:
                node.append([S('mirror'), S(c.mirror)])
            node += [[S('unit'), 1], [S('in_bom'), S('yes' if c.in_bom else 'no')], [S('on_board'), S('yes')],
                     [S('dnp'), S('yes' if c.dnp else 'no')], [S('uuid'), S(_uuid('c' + ref))]]
            r, v = self._field_pos(c)
            node.append(self._prop('Reference', ref, r[0], r[1], r[2], justify=r[3]))
            node.append(self._prop('Value', c.value, v[0], v[1], v[2], justify=v[3], hide=c.hide_value))
            node.append(self._prop('Footprint', c.fp, c.x, c.y, hide=True))
            node.append(self._prop('Datasheet', c.datasheet, c.x, c.y, hide=True))
            for k, val in c.fields.items():
                node.append(self._prop(k, val, c.x, c.y, hide=True))
            for p in c.pinlist:
                node.append([S('pin'), p['number'], [S('uuid'), S(_uuid('p%s.%s' % (ref, p['number'])))]])
            node.append(inst(ref))
            out.append(node)
        out.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
        return out

    def write(self, path):
        miss = self.check_complete()
        if miss:
            raise SystemExit('INCOMPLETE:\n  ' + '\n  '.join(miss))
        with open(path, 'w') as f:
            f.write(dump(self.to_sexp()) + '\n')
