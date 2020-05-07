from __future__ import annotations

import io
import tokenize
from itertools import groupby
from typing import Any, Iterable, List, NamedTuple


class ScopeName(NamedTuple):
    parts: List[str]

    def __str__(self):
        return ".".join(self.parts)


ScopeOptions = dict
DefinitionOptions = dict


def _render_graph(stream, node, indent: str = "", last=True, first=True):
    """Draw a textual representation of the node graph"""
    if first:
        first_i = ""
        second_i = ""
    elif last:
        first_i = "╰─"
        second_i = "  "
    else:
        first_i = "├─"
        second_i = "│ "
    node_name = str(node)
    if isinstance(node, dict) or isinstance(node, list):
        node_name = str(type(node))
    stream.write(indent + first_i + node_name + "\n")
    indent = indent + second_i
    if hasattr(node, "children"):
        children = list(node.children)
    elif isinstance(node, Definition):
        children = list(node.assignment)
    elif (
        not isinstance(node, Iterable)
        or isinstance(node, str)
        or isinstance(node, tokenize.TokenInfo)
    ):
        return
    else:
        children = list(node)
    for i, child in enumerate(children):
        _render_graph(
            stream, child, indent=indent, last=(i + 1) == len(children), first=False,
        )


class Scope(NamedTuple):
    name: str
    options: ScopeOptions
    children: List  # Should be Scope | Definition, but mypy crashes

    def print_scope(self):
        stream = io.StringIO()
        _render_graph(stream, self)
        print(stream.getvalue())

    def __str__(self):
        return f"Scope {self.name}"


class Definition(NamedTuple):
    name: str
    assignment: Any
    options: DefinitionOptions

    def __str__(self):
        return f"Definition {self.name} = {len(self.assignment)}"


def combine_strings(parts):
    return repr("\n".join(x[0].string[1:-1] for x in parts))


def breakp(arg):
    breakpoint()
    return arg


# def swallow_tokenizer_line(parser, token):
#     breakpoint()


def merge_bad_multiline_string(tokens):
    """Merge a multiline series of tokens into one string"""
    # Form is [quote, (others), quote]. We need to keep the quotes because
    # they may be on their own line with indents
    assert tokens[0].string == tokens[-1].string
    parts = [tokens[0]] + [x[0][0] for x in tokens[1]] + [tokens[-1]]

    # Validate that we have an entry for every line this covers
    # otherwise we don't have the line data to reconstruct
    all_lines = set(x.start[0] for x in parts)
    line_start, line_end = min(all_lines), max(all_lines)
    assert all_lines == set(range(line_start, line_end + 1))

    composite = []
    for line, tokens in groupby(parts, lambda x: x.start[0]):
        tokens = list(tokens)
        if line == line_start:
            composite.append(tokens[0].line[tokens[0].start[1] :])
        else:
            # Subsequent lines miss indent tokens
            # - we should always have a line end token that covers the
            # whole active line (what about comments? supported?)
            composite.append(tokens[0].line[: tokens[-1].end[1]])

        # composite.append(merge_line_tokens(list(tokens)))

    # Merge and strip the quotes off here
    full_line = "".join(composite)[1:-1]
    # print(f"\033[1mMERGING MULTILINE STRING: {full_line!r}\033[0m")
    return [f'"""{full_line}"""']


def merge_line_tokens(tokens):
    """Take a list of tokens and read the literal string they cover"""
    assert all(
        t.start[0] == t.end[0] == tokens[0].start[0] for t in tokens
    ), "Merging all from same line"
    str_start = min(t.start[1] for t in tokens)
    str_end = max(t.end[1] for t in tokens)
    return tokens[0].line[str_start:str_end]


def cause_error(message, token=None):
    if not token:
        raise SyntaxError(message)
    else:
        starts = f"  {token.start[0]}: "
        raise SyntaxError(
            f"\n{starts}{token.line.rstrip()}\n{' '*(token.start[1]+len(starts))}^ {message}"
        )
