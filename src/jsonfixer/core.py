import json
import re

_CODEBLOCK_RE = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
_CODEBLOCK_ESCAPED_RE = re.compile(r"```(?:\w+)?\\n(.*?)```", re.DOTALL)

_SMART_QUOTES = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
    }
)

_CONTROL_ESCAPES = {
    "\n": "\\n",
    "\t": "\\t",
    "\b": "\\b",
    "\f": "\\f",
}

_VALUE_TERMINATORS = frozenset(",}]:")


def parse_codeblock(s: str) -> str | None:
    match = _CODEBLOCK_RE.search(s)
    if match:
        return match.group(1).strip()

    match = _CODEBLOCK_ESCAPED_RE.search(s)
    if match:
        inner = match.group(1)
        try:
            inner = inner.encode("utf-8").decode("unicode_escape")
        except UnicodeDecodeError:
            pass
        return inner.strip()

    return None


def replace_smart_quotes(s: str) -> str:
    return s.translate(_SMART_QUOTES)


def _fix_inner_json_quotes(s: str) -> str:
    out: list[str] = []
    n = len(s)
    i = 0
    in_string = False

    while i < n:
        ch = s[i]

        if not in_string:
            out.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        if ch == "\\":
            out.append(ch)
            if i + 1 < n:
                out.append(s[i + 1])
                i += 2
            else:
                i += 1
            continue

        if ch == "\r":
            out.append("\\n")
            i += 2 if i + 1 < n and s[i + 1] == "\n" else 1
            continue

        escape = _CONTROL_ESCAPES.get(ch)
        if escape is not None:
            out.append(escape)
            i += 1
            continue

        if ch < "\x20":
            out.append(f"\\u{ord(ch):04x}")
            i += 1
            continue

        if ch == '"':
            j = i + 1
            while j < n and s[j].isspace():
                j += 1
            if j >= n or s[j] in _VALUE_TERMINATORS:
                in_string = False
                out.append('"')
            else:
                out.append('\\"')
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def fix_quotes(
    s: str,
    parse_code: bool = False,
    replace_smart: bool = False,
) -> str:
    if parse_code:
        stripped = s.strip()
        if stripped.startswith('"') and stripped.endswith('"'):
            try:
                s = json.loads(stripped)
            except json.JSONDecodeError:
                pass

        code = parse_codeblock(s)
        if code is not None:
            s = code

    if replace_smart:
        s = replace_smart_quotes(s)

    return _fix_inner_json_quotes(s)
