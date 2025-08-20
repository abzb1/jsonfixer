# Json Fixer

## Motivation

AI models often generate malformed JSON output due to incorrect handling of quotation marks.   
A common issue is improperly nested double quotes, which makes the JSON invalid and unparseable with `json.loads`.   
For example:

```json
{
    "key1": "value1",
    "key2": "value2 is behind the "value1", that is good ",
}
```

The snippet above will raise a JSONDecodeError because of the invalid quoting.

## Usage

`pip install jsonquotefixer`

jsonfixer automatically fixes broken quotation marks, allowing the JSON to be safely parsed with Python’s built-in json module.

Example usage:
```python
import json
from jsonfixer import fix_quotes

a = <a malformed JSON-like string to be fixed>
json.loads(a)  # Raises JSONDecodeError!

b = fix_quotes(a)
json.loads(b)  # Successfully parsed
```
### Arguments of fix_quotes

* **s**: a malformed JSON-like string to be fixed
* **parse_code** (bool, default=False): if True, extracts and fixes JSON from strings wrapped in triple backticks (```)
* **replace_smart** (bool, default=False): if True, replaces smart quotes (“ ”) with escaped straight quote (\")
