from typing import List, NamedTuple


class ScopeName(NamedTuple):
    parts: List[str]
    # def __init__(self, parts):
    #     self.parts = parts
    #     # print("Building ScopeName", parts)
    #     # breakpoint()
    # def __repr__(self):
    #     return f"ScopeName({self.parts!r})"


class ScopeDefinition(NamedTuple):
    name: ScopeName
    assignment: List = None
    options: List = None
    children: List = None

    # def __init__(self, name, defaults, options, children):


def combine_strings(parts):
    return repr("\n".join(x[0].string[1:-1] for x in parts))


def breakp(arg):
    breakpoint()
    return arg


# def swallow_tokenizer_line(parser, token):
#     breakpoint()


def merge_tokens(tokens):
    breakpoint()
