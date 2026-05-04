# jsonfixer

A small utility to repair broken / pseudo-JSON strings that AI models often
produce, so they can be parsed by Python's built-in `json` module.

## Motivation

LLM outputs frequently contain JSON that *looks* correct but is actually invalid:

- Unescaped inner double quotes inside string values
- Raw control characters (literal newlines, tabs, etc.) inside strings
- Smart/curly quotes (`“ ” ‘ ’`) instead of straight quotes
- The whole JSON wrapped in Markdown triple-backtick code fences
- The whole JSON returned as a quoted string with escaped `\n` sequences

For example, the following is **not** valid JSON and `json.loads` will fail:

```json
{
    "key1": "value1",
    "key2": "value2 is behind the "value1", that is good"
}
```

`jsonfixer` detects and repairs these common patterns so you can reliably
call `json.loads()` on the result.

## Features

- Escapes stray inner double quotes inside string values (`"` → `\"`)
- Converts literal control characters inside strings to proper JSON escapes
  (`\n`, `\t`, `\r`, `\b`, `\f`, and `\u00XX` for other `< 0x20` code points)
- Normalizes CRLF (`\r\n`) inside strings to `\n`
- Optional extraction of JSON from Markdown code fences (```` ```json ... ``` ````)
- Optional replacement of smart quotes (`“ ” ‘ ’`) with straight quotes (`" '`)
- Leaves already-valid JSON unchanged
- Pure Python, no runtime dependencies

## Installation

```bash
pip install jsonquotefixer
```

## Usage

### Basic example

```python
import json
from jsonfixer import fix_quotes

broken = '{"title": "The "Great" Gatsby", "author": "F. Scott Fitzgerald"}'

json.loads(broken)          # raises json.JSONDecodeError

fixed = fix_quotes(broken)
json.loads(fixed)
# {'title': 'The "Great" Gatsby', 'author': 'F. Scott Fitzgerald'}
```

### Extracting from a Markdown code block

Pass `parse_code=True` when the model wraps the JSON in triple backticks,
or returns it as a JSON-encoded string with escaped newlines:

```python
from jsonfixer import fix_quotes

raw = '```json\n{"a": "hello"}\n```'
fix_quotes(raw, parse_code=True)
# '{"a": "hello"}'
```

### Replacing smart quotes

Pass `replace_smart=True` to convert curly quotes to straight quotes before
the fix-up step runs:

```python
from jsonfixer import fix_quotes

raw = '{“a”: “hello”}'
fix_quotes(raw, replace_smart=True)
# '{"a": "hello"}'
```

### All options combined

```python
fix_quotes(raw, parse_code=True, replace_smart=True)
```

## API

### `fix_quotes(s, parse_code=False, replace_smart=False) -> str`

Main entry point. Returns a repaired JSON string.

| Argument        | Type   | Default | Description                                                                 |
|-----------------|--------|---------|-----------------------------------------------------------------------------|
| `s`             | `str`  | —       | The broken / pseudo-JSON string to repair.                                  |
| `parse_code`    | `bool` | `False` | Extract JSON from Markdown code fences, and unwrap outer JSON string quotes.|
| `replace_smart` | `bool` | `False` | Replace smart quotes (`“ ” ‘ ’`) with straight quotes (`" '`) before fixing.|

### `parse_codeblock(s) -> str | None`

Extracts the content of the first triple-backtick code fence in `s`
(with or without a language tag). Also handles the case where newlines
appear as the literal two-character sequence `\n`. Returns `None` if no
code fence is found.

### `replace_smart_quotes(s) -> str`

Returns `s` with smart quotes replaced by their straight-quote equivalents.
Does not perform any other repair.

## Development

### Setting up

```bash
git clone https://github.com/abzb1/jsonfixer.git
cd jsonfixer
pip install -e '.[dev]'
```

### Running the tests

Tests are written with `pytest`:

```bash
pytest
```

Or, to run a specific test and see verbose output:

```bash
pytest tests/test_fix_quotes.py -v
pytest tests/test_fix_quotes.py::test_valid_json_unchanged -v
```

### Pre-commit hooks

The repository ships with a `.pre-commit-config.yaml`. Enable it with:

```bash
pre-commit install
pre-commit run --all-files
```

## License

MIT — see [LICENSE](LICENSE).

## Citation

If you use this repository in your research, please cite it as follows:

```bibtex
@misc{
    oh2025jsonfixer,
    author = {Oh, Hongseok},
    title = {jsonfixer: A Utility for Fixing Invalid JSON Outputs},
    year = {2025},
    howpublished = {https://github.com/abzb1/jsonfixer},
    note = {GitHub repository}
}
```
