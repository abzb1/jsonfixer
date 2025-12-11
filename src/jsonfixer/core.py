import re


def parse_codeblock(s: str) -> str | None:
    
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    match = pattern.search(s)
    if not match:
        return None

    return match.group(2).strip()


def replace_smart_quotes(s: str) -> str:
    
    return (
        s.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def _fix_inner_json_quotes(s: str) -> str:
    
    out: list[str] = []
    i = 0
    n = len(s)
    in_string = False
    escaped = False

    def next_non_space(idx: int) -> int:
        while idx < n and s[idx].isspace():
            idx += 1
        return idx

    while i < n:
        ch = s[i]

        if not in_string:
            if ch.isspace():
                out.append(ch)
                i += 1
                continue

            if ch == '"':
                in_string = True
                escaped = False
                out.append('"')
                i += 1
                continue

            out.append(ch)
            i += 1
            continue

        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue

        if ch == '\\':
            out.append(ch)
            escaped = True
            i += 1
            continue
        
        if ch == "\r":
            if i + 1 < n and s[i + 1] == "\n":
                i += 1
            out.append("\\n")
            i += 1
            continue

        if ch == "\n":
            out.append("\\n")
            i += 1
            continue

        if ch == "\t":
            out.append("\\t")
            i += 1
            continue

        if ch == "\b":
            out.append("\\b")
            i += 1
            continue

        if ch == "\f":
            out.append("\\f")
            i += 1
            continue

        if ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
            i += 1
            continue

        if ch == '"':
            j = next_non_space(i + 1)

            if j >= n or s[j] in ',}]:':
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
        code = parse_codeblock(s)
        if code is not None:
            s = code

    if replace_smart:
        s = replace_smart_quotes(s)

    return _fix_inner_json_quotes(s)