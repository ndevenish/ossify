"""Test utilities to regenerate and run the parser"""

import io
import textwrap
from pathlib import Path
from typing import IO, Any

import tatsu

# from tatsu.util import asjson
from .grammar import TatsuSemantics

# from ossify.parser import GeneratedParser as _regenerated_parser

# from .tokenizer import Tokenizer, character_generator

# from pegen.testutil import make_parser


with open(Path(__file__).parent / "tatsu.gram") as f:
    _regenerated_parser = tatsu.compile(f.read())
    # ast = parse(GRAMMAR, '3 + 5 * ( 10 - 20 )')


def run_parser(file: IO[bytes], *, verbose: bool = False) -> Any:
    # Run a parser on a file (stream).
    # tokenizer = Tokenizer(tokenize.generate_tokens(file.readline))  # type: ignore # typeshed issue #3515
    # tokenizer = Tokenizer(character_generator(file))  # type: ignore # typeshed issue #3515

    # parser = _regenerated_parser(tokenizer, verbose=verbose)
    # result = parser.start()
    # if result is None:
    #     raise parser.make_syntax_error()
    # return result
    return _regenerated_parser.parse(
        file.read(), trace=True, colorize=True, semantics=TatsuSemantics()
    )
    # parse(GRAMMAR, file)


def parse_string(source: str, *, dedent: bool = True, verbose: bool = True) -> Any:
    # Run the parser on a string.
    if dedent:
        source = textwrap.dedent(source)
    file = io.StringIO(source)
    result = run_parser(file, verbose=verbose)  # type: ignore # typeshed issue #3515
    result.print_scope()
    return result


# def parser_for(source: str, *, dedent: bool = True, verbose: bool = False) -> Any:
#     # Run the parser on a string.
#     if dedent:
#         source = textwrap.dedent(source)
#     file = io.StringIO(source)
#     tokenizer = Tokenizer(tokenize.generate_tokens(file.readline))  # type: ignore # typeshed issue #3515
#     parser = _regenerated_parser(tokenizer, verbose=verbose)
#     return parser
