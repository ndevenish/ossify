from typing import List, NamedTuple

breakpoint()


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
    pass
    # Flatten
    tokens = [x[0][0] for x in tokens]
    assert all(
        t.start[0] == t.end[0] == tokens[0].start[0] for t in tokens
    ), "Merging all from same line"
    str_start = min(t.start[1] for t in tokens)
    str_end = max(t.end[1] for t in tokens)
    return tokens[0].line[str_start:str_end]
    print(tokens)


def cause_error(message, token=None):
    if not token:
        raise SyntaxError(message)
    else:
        starts = f"  {token.start[0]}: "
        raise SyntaxError(
            f"\n{starts}{token.line.rstrip()}\n{' '*(token.start[1]+len(starts))}^ {message}"
        )
