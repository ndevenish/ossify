import sys
from pathlib import Path

import tatsu
from tatsu.util import generic_main

from .grammar import TatsuSemantics

with open(Path(__file__).parent / "tatsu.gram") as f:
    PHILParser = tatsu.compile(f.read())


def main(filename, start=None, **kwargs):
    if start is None:
        start = "start"
    if not filename or filename == "-":
        text = sys.stdin.read()
    else:
        with open(filename) as f:
            text = f.read()

    parser = PHILParser
    tree = parser.parse(
        text, rule_name=start, filename=filename, semantics=TatsuSemantics(), **kwargs
    )
    tree.print_scope()
    return tree


if __name__ == "__main__":
    # import json
    # from tatsu.util import asjson

    ast = generic_main(main, PHILParser, name="PHIL")
    # ast.print_scope()
    # print('AST:')
    # print(ast)
    # print()
    # print('JSON:')
    # print(json.dumps(asjson(ast), indent=2))
    # print()
