"""Validate community translations with no third-party dependencies."""
from pathlib import Path
import argparse
import json
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {'zh_cn', 'zh_tw', 'en_us', 'no_no'}


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def placeholders(value):
    return [token for token in re.findall(r'%(?:%|n|.)', value) if token not in {'%%', '%n'}]


def validate(root):
    registry = load(root / 'languages.json')
    assert registry['schemaVersion'] == 1 and registry['baseLanguage'] == 'en_us'
    base = load(root / 'client/en_us.json')
    assert isinstance(base, dict) and base
    assert all(isinstance(k, str) and k.startswith(('screen.boardraid.', 'hud.boardraid.', 'msg.boardraid.', 'task.boardraid.', 'key.boardraid.', 'category.boardraid.', 'toast.boardraid.')) and isinstance(v, str) and v.strip() for k, v in base.items())
    codes = set()
    report = []
    for entry in registry['languages']:
        code = entry['code']
        assert re.fullmatch(r'[a-z]{2,3}_[a-z0-9]{2,8}', code), 'Invalid language code'
        assert code not in codes, 'Duplicate language'
        assert isinstance(entry['name'], str) and 0 < len(entry['name']) <= 80
        assert not any(ord(c) < 32 for c in entry['name']), 'Control character in display name'
        assert entry['status'] in {'ready', 'draft'}
        codes.add(code)
        values = load(root / 'client' / (code + '.json'))
        assert isinstance(values, dict) and set(values) <= set(base), 'Unknown translation key'
        if entry['status'] == 'ready' or code in PROTECTED:
            assert set(values) == set(base), 'Ready language must be complete'
            assert entry['status'] == 'ready', 'Existing language cannot be demoted'
        for key, value in values.items():
            assert isinstance(value, str) and value.strip(), 'Translation must be a nonempty string'
            assert placeholders(value) == placeholders(base[key]), 'Placeholder mismatch: ' + key
        report.append({'code': code, 'status': entry['status'], 'translated': len(values), 'total': len(base)})
    assert PROTECTED <= codes, 'Missing existing language'
    assert codes == {p.stem for p in (root / 'client').glob('*.json')}, 'Unregistered language file'
    return report


def self_test():
    assert placeholders('A %% B %s %d %n') == ['%s', '%d']
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=pairs)
    except ValueError:
        pass
    else:
        raise AssertionError('Duplicate key accepted')
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'client').mkdir()
        entries = [{'code': code, 'name': code, 'status': 'ready'} for code in sorted(PROTECTED)]
        registry = {'schemaVersion': 1, 'baseLanguage': 'en_us', 'languages': entries}
        (root / 'languages.json').write_text(json.dumps(registry), encoding='utf-8')
        for code in PROTECTED:
            (root / 'client' / (code + '.json')).write_text('{"msg.boardraid.test":"Hi %s"}', encoding='utf-8')
        validate(root)
        target = root / 'client/zh_tw.json'
        for invalid in ['{"msg.boardraid.test":"Hi %d"}', '{}', '{"unknown":"Hi"}']:
            target.write_text(invalid, encoding='utf-8')
            try:
                validate(root)
            except AssertionError:
                pass
            else:
                raise AssertionError('Invalid translation accepted')
        target.write_text('{"msg.boardraid.test":"Hi %s"}', encoding='utf-8')
        entries.append({'code': 'ja_jp', 'name': '日本語', 'status': 'draft'})
        (root / 'languages.json').write_text(json.dumps(registry), encoding='utf-8')
        (root / 'client/ja_jp.json').write_text('{}', encoding='utf-8')
        validate(root)
    print('PASS: duplicate key, placeholder, missing/unknown key rejected; draft accepted')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(validate(ROOT), ensure_ascii=False, indent=2))
