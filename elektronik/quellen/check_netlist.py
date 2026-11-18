#!/usr/bin/env python3
"""Compare KiCad's exported netlist with the design intent (intent.json)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, find, first

d = sys.argv[1]
intent = json.load(open(os.path.join(d, 'intent.json')))
root = parse(open(os.path.join(d, 'funkpult.net')).read())[0]
actual = {}
for net in find(first(root, 'nets'), 'net'):
    name = first(net, 'name')[1]
    pins = frozenset('%s.%s' % (first(n, 'ref')[1], first(n, 'pin')[1]) for n in find(net, 'node'))
    actual[name] = pins
# drop power-symbol / flag pseudo refs
def clean(ps): return frozenset(p for p in ps if not p.startswith('#'))
actual = {k: clean(v) for k, v in actual.items()}
want = {k: frozenset(v) for k, v in intent['nets'].items()}
ok = True
act_by_pins = {v: k for k, v in actual.items()}
for name, pins in sorted(want.items()):
    if pins in act_by_pins:
        an = act_by_pins[pins].lstrip('/')
        if an != name and not an.startswith('Net-(') and not an.startswith('unconnected'):
            print('NAME   %-12s exported as %s' % (name, an)); ok = False
    else:
        ok = False
        print('MISMATCH', name)
        for an, ap in actual.items():
            if ap & pins:
                print('   actual %-22s missing=%s extra=%s' % (an, sorted(pins - ap), sorted(ap - pins)))
        if not any(ap & pins for ap in actual.values()):
            print('   no actual net contains any of', sorted(pins))
want_pins = set().union(*want.values())
for an, ap in sorted(actual.items()):
    stray = ap - want_pins
    if stray and not an.startswith('unconnected-'):
        ok = False; print('EXTRA pins in net', an, sorted(stray))
nc_actual = set()
for an, ap in actual.items():
    if an.startswith('unconnected-'):
        nc_actual |= ap
nc_want = set(intent['nc'])
if nc_actual - nc_want:
    # hidden no_connect-type pins are fine
    extra = sorted(nc_actual - nc_want)
    print('unconnected (not in NC list):', extra)
comps = {first(c, 'ref')[1]: c for c in find(first(root, 'components'), 'comp')}
print('components in netlist: %d, nets: %d (intent %d)' % (len(comps), len(actual), len(want)))
print('RESULT:', 'OK - exported netlist matches intent' if ok else 'DIFFERENCES FOUND')
sys.exit(0 if ok else 1)
