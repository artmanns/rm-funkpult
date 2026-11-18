"""Load KiCad library symbols, flatten 'extends', expose pins."""
import copy, os
from sexp import parse, Sym, find, first

LIBDIR = '/usr/share/kicad/symbols'
_cache = {}

def _lib(lib):
    if lib not in _cache:
        with open(os.path.join(LIBDIR, lib + '.kicad_sym')) as f:
            root = parse(f.read())[0]
        _cache[lib] = {s[1]: s for s in find(root, 'symbol')}
    return _cache[lib]

def load(lib_id):
    """Return flattened symbol s-expr named 'Lib:Name' ready for lib_symbols."""
    lib, name = lib_id.split(':')
    syms = _lib(lib)
    s = copy.deepcopy(syms[name])
    ext = first(s, 'extends')
    if ext:
        parent = copy.deepcopy(syms[ext[1]])
        pname = parent[1]
        # child properties override parent's
        props = {p[1]: p for p in find(parent, 'property')}
        for p in find(s, 'property'):
            props[p[1]] = p
        body = [c for c in parent[2:] if not (isinstance(c, list) and c[0] == 'property')]
        units = []
        rest = []
        for c in body:
            if isinstance(c, list) and c[0] == 'symbol':
                c[1] = name + c[1][len(pname):]
                units.append(c)
            else:
                rest.append(c)
        s = [Sym('symbol'), name] + rest + list(props.values()) + units
    s[1] = lib_id
    return s

def pins(symdef):
    """List of dict(name, number, x, y, angle, length, etype, unit)."""
    out = []
    for u in find(symdef, 'symbol'):
        unit = int(u[1].rsplit('_', 2)[-2])
        for p in find(u, 'pin'):
            at = first(p, 'at')
            out.append(dict(name=first(p, 'name')[1], number=first(p, 'number')[1],
                            x=float(at[1]), y=float(at[2]), angle=float(at[3]) if len(at) > 3 else 0.0,
                            length=float(first(p, 'length')[1]), etype=str(p[1]), unit=unit,
                            hidden=any(c == 'hide' for c in p if not isinstance(c, list))))
    return out

if __name__ == '__main__':
    import sys
    for lid in sys.argv[1:]:
        d = load(lid)
        print('==', lid)
        for p in pins(d):
            print('  %-10s #%-4s at(%7.2f,%7.2f) a=%3d len=%.2f %s u%d%s' % (p['name'], p['number'], p['x'], p['y'], p['angle'], p['length'], p['etype'], p['unit'], ' HIDDEN' if p['hidden'] else ''))
