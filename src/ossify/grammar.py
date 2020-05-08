from __future__ import annotations

import io
import token as tokenmod
import tokenize
from itertools import groupby
from tokenize import TokenInfo
from typing import Any, Iterable, List, NamedTuple, Sequence


class ScopeName(NamedTuple):
    parts: List[str]

    def __str__(self):
        return ".".join(self.parts)


class Include(NamedTuple):
    type: str
    value: str


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
    stream.write(indent + first_i + node_name + "\n" + "\033[0m")
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
    children: Sequence = ()  # Should be Scope | Definition, but mypy crashes

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
        return f"Definition {self.name} = [{len(self.assignment)} values] {self.options if self.options else ''}"


def combine_strings(parts):
    return repr("\n".join(x[0].string[1:-1] for x in parts))


def breakp(arg):
    print("Arg is: \033[32m", arg, "\033[0m")
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


def merge_tokens(*tokenlists, typename=None):
    tokens = flatten_tokens(*tokenlists)
    if typename is not None:
        merged = TokenInfo(
            type=getattr(tokenmod, typename),
            string=tokens[0].string,
            start=tokens[0].start,
            end=tokens[0].end,
            line=tokens[0].line,
        )
    else:
        merged = tokens[0]
    for token in tokens[1:]:
        # contiguous - disable for now as bad tokenization
        # assert token.start[1] == (merged.end[1] + 1) or token.start[0] == (
        #     merged.end[0] + 1
        # )
        merged = TokenInfo(
            type=merged.type,
            string=merged.string + token.string,
            start=merged.start,
            end=token.end,
            line=merged.line,
        )
    return merged


def flatten_tokens(*tokenlists):
    flat = []
    for entry in tokenlists:
        if isinstance(entry, list):
            # print("recursing", entry)
            for subentry in entry:
                flat.extend(flatten_tokens(subentry))
        else:
            flat.append(entry)
    return flat
