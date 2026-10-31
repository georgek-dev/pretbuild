import glob
import os
import re
import subprocess
import sys

CC = ["cc", "gcc", "clang", "cl"]

def tokenize(chars):
    chars = re.sub(r'#.*', '', chars)
    chars = chars.replace('(', ' ( ').replace(')',  ' ) ').replace('->', ' -> ')
    return chars.split()

def sexpr(tok):
    if len(tok) == 0:
        raise SyntaxError("unexpected EOF")

    token = tok.pop(0)
    if token == '(':
        L = []
        while tok and tok[0] != ')':
            L.append(sexpr(tok))
        tok.pop(0)
        return L
    elif token == ')':
        raise SyntaxError("unexpected closing parenthesis")
    else:
        try:
            return int(token)
        except ValueError:
            return token

def freeze(x):
    if isinstance(x, list):
        return tuple(freeze(item) for item in x)
    return x

def dsl(cont):
    tok = tokenize(cont)
    ast = []
    while tok:
        ast.append(sexpr(tok))

    conf = {}

    i = 0
    while i < len(ast):
        if i + 1 < len(ast) and ast[i+1] == "->":
            key = freeze(ast[i])
            val = ast[i+2] if i + 2 < len(ast) else None
            conf[key] = val
            i += 3
        else:
            i += 1

    return conf

def dslleg(cont):
    tok = tokenize(cont)
    ast = []
    while tok:
        ast.append(sexpr(tok))

    conf = {}
    for e in ast:
        if isinstance(e, list) and len(e) >= 3 and e[1] == "->":
            key = freeze(e[0])
            val = e[2]
            conf[key] = val

    return conf

def flat(x):
    out = []
    if isinstance(x, list):
        for i in x:
            out.extend(flat(i))
    elif x is not None:
        out.append(x)
    return out

def lookup(key, sub, conf):
    val = conf.get(key)
    if isinstance(val, list):
        for e in val:
            hit = isinstance(e, list) and len(e) >= 3 and e[0] == "set"
            if hit and e[1] == sub:
                return flat(e[2:])
        return flat(val)
    return []

def depfiles(items):
    out = []
    for p in flat(items):
        p = str(p)
        if any(c in p for c in "*?["):
            out.extend(sorted(glob.glob(p)))
        elif os.path.exists(p):
            out.append(p)
    return out

def current(tgt, ins):
    if not ins or not tgt or not os.path.exists(tgt):
        return False
    return os.path.getmtime(tgt) > max(os.path.getmtime(s) for s in ins)

def subst(t, a1, a2):
    if not isinstance(t, str):
        return t
    out = []
    for part in t.split('+'):
        out.append(part.replace('_1', str(a1)).replace('_2', str(a2)))
    return "".join(out)

def resolve(x, conf, arg1, tgt, deps):
    if isinstance(x, list):
        if not x:
            return []
        h = x[0]
        if h == "ifexists":
            f = flat(resolve(x[1], conf, arg1, tgt, deps))
            if f and os.path.exists(str(f[0])):
                rest = x[2:]
                if rest and rest[0] == "with":
                    rest = rest[1:]
                found = []
                for it in rest:
                    found.extend(flat(resolve(it, conf, arg1, tgt, deps)))
                deps.extend(depfiles(found))
            return []
        if h == "iter":
            t = x[1] if len(x) > 1 else ""
            base = flat(resolve(arg1, conf, arg1, tgt, deps))
            return [subst(t, e, tgt) for e in base]
        if h == "stripext":
            parts = flat(resolve(x[1], conf, arg1, tgt, deps))
            return [os.path.splitext(str(e))[0] for e in parts]
        if len(x) == 3 and x[1] == "->":
            return lookup(str(x[0]), x[2], conf)
        out = []
        for it in x:
            out.extend(flat(resolve(it, conf, arg1, tgt, deps)))
        return out
    if isinstance(x, str):
        s = subst(x, arg1, tgt)
        if ":" in s:
            key, _, idx = s.partition(":")
            if key in conf and idx.isdigit():
                val = conf.get(key) or []
                i = int(idx)
                if 1 <= i <= len(val):
                    v = val[i-1]
                else:
                    v = val[-1] if val else None
                n = flat(v)
                return n[-1] if n else None
        return s
    return x

def expand(tml, arg1, tgt, conf, deps):
    out = []
    for item in tml:
        if isinstance(item, list):
            out.extend(flat(resolve(item, conf, arg1, tgt, deps)))
        elif isinstance(item, str):
            t = subst(item, arg1, tgt)
            if t != "":
                out.append(t)
        else:
            out.append(str(item))
    return out

def eval(conf):
    cmds = {}
    for e in conf.get("commands") or []:
        if isinstance(e, list) and e:
            cmds[e[0]] = e
    steps = conf.get("steps") or []

    count = len(conf.get("steps") or [])
    done = 1
    for sk, _, rtgt in steps:
        ct = sk[0]
        arg1 = resolve(sk[1], conf, sk[1], rtgt, [])
        tgt = resolve(rtgt, conf, arg1, rtgt, [])

        tml = cmds.get(ct, [])
        if not tml:
            print(f"error: no command defined for {ct}")
            continue

        deps = []
        ca = expand(tml, arg1, tgt, conf, deps)

        src = f"{arg1}.c" if ct in CC and isinstance(arg1, str) else None

        rn = True

        ins = [s for s in [src] + deps if s and os.path.exists(s)]
        if current(tgt, ins):
            print(f"{tgt} is current, skipping")
            done += 1
            rn = False

        if rn:
            cmd = " ".join(ca[1:])
            print(f"{done}/{count} {cmd}", end="\r")

            try:
                subprocess.run(cmd, shell=True, check=True)
                done += 1
            except subprocess.CalledProcessError:
                print(f"error while compiling {tgt}")
                return False

    return True
