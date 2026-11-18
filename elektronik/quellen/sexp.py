"""Minimal S-expression reader/writer for KiCad files."""
import re

class Sym(str):
    """Unquoted atom."""
    pass

_tok = re.compile(r'''\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))''')

def parse(text):
    pos = 0
    stack = [[]]
    n = len(text)
    while True:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            done = stack.pop()
            stack[-1].append(done)
        elif m.group(3) is not None:
            s = m.group(3).replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
            stack[-1].append(s)
        else:
            stack[-1].append(Sym(m.group(4)))
    assert len(stack) == 1, "unbalanced"
    return stack[0]

def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

def dump(x, indent=0):
    if isinstance(x, list):
        simple = all(not isinstance(i, list) for i in x)
        if simple or len(dump_flat(x)) < 100:
            return dump_flat(x)
        out = '(' + dump(x[0])
        for i in x[1:]:
            if isinstance(i, list):
                out += '\n' + '  ' * (indent + 1) + dump(i, indent + 1)
            else:
                out += ' ' + dump(i)
        out += '\n' + '  ' * indent + ')'
        return out
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, str):
        return q(x)
    if isinstance(x, float):
        s = ('%.4f' % x).rstrip('0').rstrip('.')
        return s if s not in ('-0', '') else '0'
    return str(x)

def dump_flat(x):
    if isinstance(x, list):
        return '(' + ' '.join(dump_flat(i) for i in x) + ')'
    return dump(x)

def find(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def first(node, name):
    r = find(node, name)
    return r[0] if r else None
