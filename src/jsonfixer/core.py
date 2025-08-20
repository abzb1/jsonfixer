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

def fix_quotes(
        s: str,
        parse_code: bool = True,
        replace_smart: bool = True,
    ) -> str:

    if parse_code:
        code = parse_codeblock(s)
        if code is not None:
            s = code
            
    if replace_smart:
        s = replace_smart_quotes(s)

    out = []
    in_string = False
    in_value_string = False
    escaped = False

    stack = []

    def top():
        return stack[-1] if stack else None

    def in_obj():
        return bool(stack) and stack[-1][0] == "obj"

    def in_arr():
        return bool(stack) and stack[-1][0] == "arr"

    def set_top_state(state):
        if stack:
            ctx_type, _ = stack[-1]
            stack[-1] = (ctx_type, state)

    def push_obj():
        stack.append(("obj", "key"))

    def push_arr():
        stack.append(("arr", "value"))

    def pop_ctx():
        if stack:
            stack.pop()

    def expecting_value():
        if not stack:
            return True
        _, state = stack[-1]
        return state == "value"

    def value_finished():
        if stack:
            set_top_state("comma_or_end")

    def after_closing_value():
        if stack:
            set_top_state("comma_or_end")

    def next_non_space(idx: int):
        n_ = len(s)
        while idx < n_ and s[idx].isspace():
            idx += 1
        return idx

    def is_nonstring_value_start(ch: str):
        return ch.isdigit() or ch in "-tfn"

    i, n = 0, len(s)
    while i < n:
        ch = s[i]

        if not in_string:
            if ch.isspace():
                out.append(ch)
                i += 1
                continue

            if ch == "{":
                push_obj()
                out.append(ch)
                i += 1
                continue

            if ch == "}":
                if in_obj():
                    pop_ctx()
                out.append(ch)
                i += 1
                after_closing_value()
                continue

            if ch == "[":
                push_arr()
                out.append(ch)
                i += 1
                continue

            if ch == "]":
                if in_arr():
                    pop_ctx()
                out.append(ch)
                i += 1
                after_closing_value()
                continue

            if ch == ",":
                out.append(ch)
                i += 1
                if in_obj():
                    set_top_state("key")
                elif in_arr():
                    set_top_state("value")
                continue

            if ch == ":":
                out.append(ch)
                i += 1
                if in_obj():
                    set_top_state("value")
                continue

            if ch == '"':
                out.append(ch)
                in_string = True
                escaped = False
                if in_obj():
                    in_value_string = top()[1] == "value"
                elif in_arr():
                    in_value_string = top()[1] == "value"
                else:
                    in_value_string = True
                i += 1
                continue

            if expecting_value():
                if is_nonstring_value_start(ch):
                    value_finished()
                out.append(ch)
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

        if ch == "\\":
            out.append(ch)
            escaped = True
            i += 1
            continue

        if ch == '"':
            if in_value_string:
                j = next_non_space(i + 1)
                if j >= n or s[j] in ",]}":
                    out.append('"')
                    in_string = False
                    in_value_string = False
                    i += 1
                    value_finished()
                    continue

                out.append('\\"')
                i += 1
                continue

            out.append('"')
            in_string = False
            i += 1
            if in_obj() and top()[1] == "key":
                set_top_state("colon")
            continue

        out.append(ch)
        i += 1

    return "".join(out)