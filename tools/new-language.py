"""Create an empty community language draft; never overwrite existing work."""
import argparse
import json
import re
from validate import ROOT, load, validate

parser = argparse.ArgumentParser()
parser.add_argument('code')
parser.add_argument('--name', required=True)
args = parser.parse_args()
assert re.fullmatch(r'[a-z]{2,3}_[a-z0-9]{2,8}', args.code)
assert 0 < len(args.name) <= 80 and not any(ord(c) < 32 for c in args.name)
validate(ROOT)
registry = load(ROOT / 'languages.json')
assert args.code not in {entry['code'] for entry in registry['languages']}, 'Language already exists'
path = ROOT / 'client' / (args.code + '.json')
with path.open('x', encoding='utf-8', newline='\n') as stream:
    stream.write('{}\n')
registry['languages'].append({'code': args.code, 'name': args.name, 'status': 'draft'})
(ROOT / 'languages.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
validate(ROOT)
print('Created draft: ' + args.code)
