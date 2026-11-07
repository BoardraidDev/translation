"""Build a data-only Minecraft 1.16.1 preview resource pack."""
import argparse
import json
import zipfile
from validate import ROOT, validate

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
validate(ROOT)
with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED) as pack:
    pack.writestr('pack.mcmeta', json.dumps({'pack': {'pack_format': 5, 'description': 'BoardRaid community translation preview'}}))
    for path in sorted((ROOT / 'client').glob('*.json')):
        pack.writestr('assets/boardraid/lang/' + path.name, path.read_bytes())
print('Created data-only preview pack')
