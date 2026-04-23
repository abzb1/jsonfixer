import json

import pytest

from jsonfixer import (
    fix_quotes,
    parse_codeblock,
    replace_smart_quotes,
)


def test_trailing_quote_in_value():
    s = '{"a": "hello "world"}'
    out = fix_quotes(s)

    json.loads(out)
    assert '\\"' in out or out != s


def test_valid_json_unchanged():
    s = '{"a": "b", "n": 1, "ok": true, "arr": ["x", "y"]}'
    out = fix_quotes(s)

    assert out == s
    assert json.loads(out) == json.loads(s)


def test_list():
    s = (
        "```json\n"
        "[\n"
        '    "qwer asdf",\n'
        '    "zxcv asdf",\n'
        '    "ASDF, ZXCV",\n'
        '    "QWER ASDF",\n'
        '    "ASDF ASDF"\n'
        "]\n"
        "```"
    )
    out = fix_quotes(s, parse_code=True, replace_smart=True)

    assert out.startswith("[")
    assert out.endswith("]")
    json.loads(out)


def test_escaped_list():
    s = '```json\\n["qq","ww","ee","rr","aa"]\\n```'
    out = fix_quotes(s, parse_code=True, replace_smart=True)

    assert out.startswith("[")
    assert out.endswith("]")
    json.loads(out)


def test_replace_smart_quotes_double():
    s = "\u201chello\u201d"
    assert replace_smart_quotes(s) == '"hello"'


def test_replace_smart_quotes_single():
    s = "\u2018world\u2019"
    assert replace_smart_quotes(s) == "'world'"


def test_replace_smart_quotes_mixed():
    s = "\u201chello\u201d and \u2018world\u2019"
    assert replace_smart_quotes(s) == "\"hello\" and 'world'"


def test_replace_smart_quotes_no_smart_quotes():
    s = "\"hello\" and 'world'"
    assert replace_smart_quotes(s) == s


def test_smart_quotes_in_value():
    s = '{"a": \u201chello world\u201d}'
    out = fix_quotes(s, replace_smart=True)
    assert json.loads(out) == {"a": "hello world"}


def test_smart_quotes_in_keys_and_values():
    s = "{\u201ca\u201d: \u201chello\u201d}"
    out = fix_quotes(s, replace_smart=True)
    assert json.loads(out) == {"a": "hello"}


def test_smart_quotes_in_array():
    s = "[\u201cfoo\u201d, \u201cbar\u201d]"
    out = fix_quotes(s, replace_smart=True)
    assert json.loads(out) == ["foo", "bar"]


def test_literal_newline_in_string():
    s = '{"a": "line1\nline2"}'
    out = fix_quotes(s)
    assert json.loads(out) == {"a": "line1\nline2"}


def test_literal_tab_in_string():
    s = '{"a": "col1\tcol2"}'
    out = fix_quotes(s)
    assert json.loads(out) == {"a": "col1\tcol2"}


def test_crlf_in_string_normalized():
    s = '{"a": "line1\r\nline2"}'
    out = fix_quotes(s)
    assert json.loads(out) == {"a": "line1\nline2"}


def test_backspace_in_string():
    s = '{"a": "text\bmore"}'
    out = fix_quotes(s)
    assert "\\b" in out
    assert json.loads(out) == {"a": "text\bmore"}


def test_formfeed_in_string():
    s = '{"a": "text\fmore"}'
    out = fix_quotes(s)
    assert "\\f" in out
    assert json.loads(out) == {"a": "text\fmore"}


def test_control_char_below_0x20_unicode_escaped():
    s = '{"a": "hello\x01world"}'
    out = fix_quotes(s)
    assert "\\u0001" in out
    assert json.loads(out) == {"a": "hello\x01world"}


def test_nul_byte_unicode_escaped():
    s = '{"a": "hello\x00world"}'
    out = fix_quotes(s)
    assert "\\u0000" in out
    assert json.loads(out) == {"a": "hello\x00world"}


def test_preescaped_newline_unchanged():
    s = '{"a": "line1\\nline2"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"a": "line1\nline2"}


def test_preescaped_tab_unchanged():
    s = '{"a": "col1\\tcol2"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"a": "col1\tcol2"}


def test_preescaped_quote_unchanged():
    s = '{"a": "say \\"hello\\""}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"a": 'say "hello"'}


def test_double_backslash_preserved():
    s = '{"path": "C:\\\\Users\\\\file"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"path": "C:\\Users\\file"}


def test_inner_quote_in_middle_of_value():
    s = '{"a": "hel"lo"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["a"]


def test_multiple_inner_quotes_in_value():
    s = '{"a": "one "two" three"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert "one" in result["a"]
    assert "two" in result["a"]
    assert "three" in result["a"]


def test_inner_quote_at_end_before_delimiter():
    s = '{"a": "hello world""}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert "hello world" in result["a"]


def test_inner_quote_in_key():
    s = '{"hel"lo": "world"}'
    out = fix_quotes(s)
    result = json.loads(out)
    key = next(iter(result))
    assert '"' in key
    assert result[key] == "world"


def test_inner_quote_in_array_element():
    s = '["hello "world", "foo "bar"]'
    out = fix_quotes(s)
    result = json.loads(out)
    assert len(result) == 2
    assert '"' in result[0]


def test_multiple_keys_with_inner_quotes():
    s = '{"a": "foo "bar", "b": "baz "qux"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["a"]
    assert '"' in result["b"]


def test_realistic_ai_generated_quotes():
    s = '{"title": "The "Great" Gatsby", "author": "F. Scott Fitzgerald"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["title"]
    assert "Great" in result["title"]
    assert result["author"] == "F. Scott Fitzgerald"


def test_nested_object_with_inner_quote():
    s = '{"outer": {"inner": "hello "world"}}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["outer"]["inner"]


def test_mixed_value_types_unchanged():
    s = '{"s": "hello", "n": 42, "b": true, "nil": null}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"s": "hello", "n": 42, "b": True, "nil": None}


def test_string_array_unchanged():
    s = '["alpha", "beta", "gamma"]'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == ["alpha", "beta", "gamma"]


def test_deeply_nested_unchanged():
    s = '{"a": {"b": {"c": {"d": "value"}}}}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out)["a"]["b"]["c"]["d"] == "value"


def test_codeblock_with_language_tag():
    s = '```json\n{"a": 1}\n```'
    assert parse_codeblock(s) == '{"a": 1}'


def test_codeblock_without_language_tag():
    s = '```\n{"a": 1}\n```'
    assert parse_codeblock(s) == '{"a": 1}'


def test_codeblock_different_language():
    s = "```python\n[1, 2, 3]\n```"
    assert parse_codeblock(s) == "[1, 2, 3]"


def test_codeblock_with_surrounding_text():
    s = 'Here is the JSON:\n```json\n{"x": 99}\n```\nDone.'
    assert parse_codeblock(s) == '{"x": 99}'


def test_no_codeblock_returns_none():
    assert parse_codeblock('{"a": 1}') is None


def test_no_codeblock_plain_text_returns_none():
    assert parse_codeblock("just some plain text") is None


def test_parse_code_extracts_object_from_codeblock():
    s = '```json\n{"a": "hello"}\n```'
    out = fix_quotes(s, parse_code=True)
    assert json.loads(out) == {"a": "hello"}


def test_parse_code_extracts_array_from_codeblock():
    s = '```json\n["x", "y", "z"]\n```'
    out = fix_quotes(s, parse_code=True)
    assert json.loads(out) == ["x", "y", "z"]


def test_parse_code_unwraps_double_quoted_json_string():
    inner = '{"a": "hello"}'
    s = json.dumps(inner)
    out = fix_quotes(s, parse_code=True)
    assert json.loads(out) == {"a": "hello"}


def test_parse_code_false_does_not_extract_codeblock():
    s = '```json\n{"a": 1}\n```'
    out = fix_quotes(s, parse_code=False)
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_parse_code_and_replace_smart_combined():
    s = "```json\n{\u201ca\u201d: \u201chello\u201d}\n```"
    out = fix_quotes(s, parse_code=True, replace_smart=True)
    assert json.loads(out) == {"a": "hello"}


def test_empty_object_unchanged():
    assert fix_quotes("{}") == "{}"


def test_empty_array_unchanged():
    assert fix_quotes("[]") == "[]"


def test_empty_string_value_unchanged():
    s = '{"a": ""}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"a": ""}


def test_unicode_content_preserved():
    s = '{"name": "장삼", "city": "복경"}'
    out = fix_quotes(s)
    assert json.loads(out) == {"name": "장삼", "city": "복경"}


def test_url_in_value_unchanged():
    s = '{"url": "https://example.com/path?q=1&r=2"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"url": "https://example.com/path?q=1&r=2"}


def test_plain_string_with_inner_quotes():
    s = '"say "hello" please"'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result
    assert "hello" in result


def test_cjk_korean_hangul_preserved():
    s = '{"인사": "안녕하세요", "도시": "서울특별시"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"인사": "안녕하세요", "도시": "서울특별시"}


def test_cjk_chinese_simplified_preserved():
    s = '{"问候": "你好世界", "城市": "北京"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"问候": "你好世界", "城市": "北京"}


def test_cjk_chinese_traditional_preserved():
    s = '{"問候": "你好世界", "城市": "臺北"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"問候": "你好世界", "城市": "臺北"}


def test_cjk_japanese_mixed_scripts_preserved():
    s = '{"挨拶": "こんにちは", "カナ": "カタカナ", "漢字": "日本語"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {
        "挨拶": "こんにちは",
        "カナ": "カタカナ",
        "漢字": "日本語",
    }


def test_cjk_mixed_languages_array():
    s = '["한국어", "中文", "日本語", "English"]'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == ["한국어", "中文", "日本語", "English"]


def test_cjk_with_inner_quote_korean():
    s = '{"제목": "그는 "안녕"이라고 말했다"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["제목"]
    assert "안녕" in result["제목"]


def test_cjk_with_inner_quote_chinese():
    s = '{"标题": "他说"你好"就走了"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["标题"]
    assert "你好" in result["标题"]


def test_cjk_with_inner_quote_japanese():
    s = '{"題名": "彼は"こんにちは"と言った"}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert '"' in result["題名"]
    assert "こんにちは" in result["題名"]


def test_cjk_with_smart_quotes():
    s = "{\u201c이름\u201d: \u201c김철수\u201d, \u201c国\u201d: \u201c韓国\u201d}"
    out = fix_quotes(s, replace_smart=True)
    assert json.loads(out) == {"이름": "김철수", "国": "韓国"}


def test_cjk_with_literal_newline_in_value():
    s = '{"문장": "첫째 줄\n둘째 줄"}'
    out = fix_quotes(s)
    assert json.loads(out) == {"문장": "첫째 줄\n둘째 줄"}


def test_cjk_codeblock_extraction():
    s = '```json\n{"人物": "孔子", "朝代": "春秋"}\n```'
    out = fix_quotes(s, parse_code=True)
    assert json.loads(out) == {"人物": "孔子", "朝代": "春秋"}


def test_cjk_codeblock_with_smart_quotes_and_inner_quote():
    s = (
        "```json\n"
        '{\u201c인용\u201d: \u201c공자 왈 "학이시습지"라 하였다\u201d}\n'
        "```"
    )
    out = fix_quotes(s, parse_code=True, replace_smart=True)
    result = json.loads(out)
    assert "학이시습지" in result["인용"]
    assert '"' in result["인용"]


def test_cjk_fullwidth_punctuation_preserved():
    s = '{"문장": "안녕하세요, 세계!", "句": "你好,世界!"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {
        "문장": "안녕하세요, 세계!",
        "句": "你好,世界!",
    }


def test_cjk_emoji_and_mixed_content():
    s = '{"메시지": "안녕 🌏 世界 🗾 日本"}'
    out = fix_quotes(s)
    assert out == s
    assert json.loads(out) == {"메시지": "안녕 🌏 世界 🗾 日本"}


def test_cjk_nested_object_with_inner_quote():
    s = '{"외부": {"내부": "그는 "안녕"이라 했다"}}'
    out = fix_quotes(s)
    result = json.loads(out)
    assert "안녕" in result["외부"]["내부"]
    assert '"' in result["외부"]["내부"]
