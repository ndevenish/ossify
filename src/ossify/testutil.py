"""Test utilities to regenerate and run the parser"""

import io
import textwrap
import tokenize
from typing import IO, Any

from ossify.parser import GeneratedParser as _regenerated_parser

from .tokenizer import Tokenizer

# from pegen.testutil import make_parser


# with open(Path(__file__).parent / "phild.gram") as f:
#     _regenerated_parser = make_parser(f.read())


def run_parser(file: IO[bytes], *, verbose: bool = False) -> Any:
    # Run a parser on a file (stream).
    tokenizer = Tokenizer(tokenize.generate_tokens(file.readline))  # type: ignore # typeshed issue #3515
    parser = _regenerated_parser(tokenizer, verbose=verbose)
    result = parser.start()
    if result is None:
        raise parser.make_syntax_error()
    return result


def parse_string(source: str, *, dedent: bool = True, verbose: bool = False) -> Any:
    # Run the parser on a string.
    if dedent:
        source = textwrap.dedent(source)
    file = io.StringIO(source)
    return run_parser(file, verbose=verbose)  # type: ignore # typeshed issue #3515


def parser_for(source: str, *, dedent: bool = True, verbose: bool = False) -> Any:
    # Run the parser on a string.
    if dedent:
        source = textwrap.dedent(source)
    file = io.StringIO(source)
    tokenizer = Tokenizer(tokenize.generate_tokens(file.readline))  # type: ignore # typeshed issue #3515
    parser = _regenerated_parser(tokenizer, verbose=verbose)
    return parser
