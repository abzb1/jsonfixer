import json

from jsonfixer import fix_quotes

def test_trailing_quote_in_value():
    s = '{"a": "hello "world"}'
    out = fix_quotes(s)

    print(json.loads(out))

    assert '\\"' in out or out != s

def test_valid_json_unchanged():
    s = '{"a": "b", "n": 1, "ok": true, "arr": ["x", "y"]}'
    out = fix_quotes(s)

    assert json.dumps(json.loads(out), ensure_ascii=False) == json.dumps(json.loads(s), ensure_ascii=False)

def test_list():

    aaa = """
```json\n[\n    "qwer asdf",\n    "zxcv asdf",\n    "ASDF, ZXCV",\n    "QWER ASDF",\n    "ASDF ASDF"\n]\n```
""".strip()
    out = fix_quotes(aaa, parse_code=True, replace_smart=True)
    assert out.startswith("[")
    assert out.endswith("]")
    try:
        print(json.loads(out))
        print(json.loads(out).__class__)
    except json.JSONDecodeError:
        assert False, "Failed to parse JSON"

if __name__ == "__main__":
    test_trailing_quote_in_value()
    test_valid_json_unchanged()
    test_list()