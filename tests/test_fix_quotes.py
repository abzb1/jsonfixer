from jsonfixer import fix_quotes

def test_trailing_quote_in_value():
    s = '{"a": "hello "world"}'
    out = fix_quotes(s)
    assert '\\"' in out or out != s

def test_valid_json_unchanged():
    s = '{"a": "b", "n": 1, "ok": true, "arr": ["x", "y"]}'
    out = fix_quotes(s)
    assert out == s