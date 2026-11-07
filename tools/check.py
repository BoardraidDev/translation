from pathlib import Path
import json, re, sys
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
def check(root):
    failures=[]
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.parts: continue
        if p.suffix in {'.pem','.key','.jar','.zip'} or p.name.startswith('.env'):
            failures.append(str(p.relative_to(root)))
        if p.suffix not in {'.md','.json','.py','.yml'}: continue
        s=p.read_text(encoding='utf-8')
        if p.suffix=='.json': json.loads(s)
        if p.suffix=='.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s):
                u=urlsplit(target)
                if u.scheme and u.scheme not in {'https','mailto'}: failures.append(target)
                if not u.scheme and u.path:
                    q=(p.parent/unquote(u.path)).resolve()
                    if not q.is_relative_to(root.resolve()) or not q.exists(): failures.append(target)
        if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)',s):
            failures.append('credential pattern: '+str(p.relative_to(root)))
    if (root/'openapi.json').exists():
        api=json.loads((root/'openapi.json').read_text(encoding='utf-8'))
        allowed={'/api/status','/api/leaderboard','/api/player','/api/head'}
        assert set(api['paths'])==allowed
        assert all(set(item)=={'get'} for item in api['paths'].values())
    if (root/'catalog.json').exists():
        import subprocess, tempfile
        subprocess.run([sys.executable,str(root/'tools/build.py'),'--self-test'],check=True)
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([sys.executable,str(root/'tools/build.py'),'--output',td],check=True)
            assert (Path(td)/'wiki.html').exists() and (Path(td)/'en/wiki.html').exists()
    if (root/'languages.json').exists():
        import subprocess
        subprocess.run([sys.executable,str(root/'tools/validate.py'),'--self-test'],check=True)
        subprocess.run([sys.executable,str(root/'tools/validate.py')],check=True)
    return failures
if '--self-test' in sys.argv:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r=Path(td); (r/'README.md').write_text('[bad](missing.md)',encoding='utf-8')
        assert check(r)
        (r/'README.md').write_text('# Valid',encoding='utf-8'); assert not check(r)
    print('PASS: missing-link red / valid green')
else:
    errors=check(ROOT)
    print('PASS: public content' if not errors else '\n'.join(errors))
    raise SystemExit(bool(errors))
