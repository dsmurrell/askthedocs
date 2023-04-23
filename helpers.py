import hashlib
import json

from rich import print as rprint
from rich.syntax import Syntax


def compute_hash(data):
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def pretty_print_dict(d):
    json_string = json.dumps(d, sort_keys=True, indent=4)
    syntax_colored_json = Syntax(
        json_string, "json", theme="solarized-dark", line_numbers=False
    )
    rprint(syntax_colored_json)
