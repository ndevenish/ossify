import io
import re
import token
import tokenize
from tokenize import TokenInfo
from typing import Iterator, List

numchars = '0123456789'

reNamelike = re.compile(r"[A-Za-z_]")
reWhitespace = re.compile("[ \t]+")
reName = re.compile(r"[A-Za-z_]\w*")
reStringStart = re.compile(r'"""|"|\'\'\'|\'')

def read_number(data):
    if "3" in data:
        print(data)
    # Cheat for now
    # -1 because will always be a newline, but sometimes that newline
    # is an escaped newline
    s = io.StringIO(data[:-1])
    toke = next(tokenize.generate_tokens(s.readline))
    if toke.type == token.NUMBER:
        return toke.string
    return False

def character_generator(file_interface, encoding="utf-8", verbose=True):
    raw_data = file_interface.read()
    try:
        data = raw_data.decode(encoding)
    except AttributeError:
        data = raw_data

    pos, maxlen = 0, len(data)
    line_start, line_end = 0, 0
    line_no = 0
    while pos < maxlen:
        # if pos > 3050:
        #     return
        _previous_pos = pos
        if line_end <= pos:
            line_no += 1
            # work out the line end for line-slicing
            line_start = line_end
            line_end = data.find("\n", pos) + 1
            if line_end == 0:
                line_end = maxlen
        line = data[line_start:line_end]
        line_remaining = data[pos:line_end]
        if verbose:
            print("Processing line: \033[37m" + repr(data[line_start:pos] +"_e_[30;1m|_e_[0m" + data[pos:line_end]).replace("_e_", "\033"))

        if data[pos] == "\\" and not (pos+1) == maxlen and data[pos+1] == "\n":
            # Handle swallowing escaped newlines
            if verbose:
                print("Escaped newline")
            pos += 2
        elif data[pos] == "\t":
            if verbose:
                print(f"{pos}: Tab (sent space)")
            yield TokenInfo(type=token.OP, string=" ", start=(line_no, pos), end=(line_no, pos), line=line)
            pos += 1
        elif data[pos] == "\n":
            if verbose:
                print(f"{pos}: NEWLINE")
            pos += 1
            yield TokenInfo(type=token.NEWLINE, string="\n", start=(line_no, pos-1), end=(line_no, pos), line=line)
        elif string := reStringStart.match(data, pos=pos):
            quote_type = string.group()
            end_pattern = r"(?<!\\)" + quote_type
            re_endquote = re.compile(end_pattern, re.M | re.S)
            end_match = re_endquote.search(data, pos=pos+len(quote_type))
            assert end_match, "Unterminated string"
            contents = data[string.start()+len(quote_type):end_match.end()-len(quote_type)]
            start_l = line_no
            line_no += contents.count("\n")
            # Found the start of some string
            # data.find(quote_type, pos=pos+len(string))
            if verbose:
                print(f"STRING: {contents!r}")
            yield TokenInfo(type=token.STRING, string=quote_type + contents + quote_type, start=(start_l, pos), end=(line_no+1, pos), line="")
            pos = end_match.end()
        elif name := reName.match(data, pos=pos):
            yield TokenInfo(type=token.NAME, string=name.group(), start=(line_no, name.start()), end=(line_no, name.end()), line=line)
            pos += len(name.group())
        elif data[pos] in "0123456789":
            yield TokenInfo(type=token.NUMBER, string=data[pos], start=(line_no, pos), end=(line_no, pos), line=line)
            pos += 1
        else:
            if verbose:
                print(f"OP: {data[pos]}")
            yield TokenInfo(type=token.OP, string=data[pos], start=(line_no, pos), end=(line_no, pos+1), line=line)
            # print("Something else?")
            pos += 1

        assert pos != _previous_pos, "Didn't advance position"

    yield TokenInfo(type=token.NEWLINE, string="\n", start=(line_no, pos), end=(line_no, pos), line="")
    yield TokenInfo(type=token.ENDMARKER, string="", start=(line_no, pos+1), end=(line_no, pos+1), line="")
    return None

def simple_generator(file_interface, encoding = "utf-8", verbose=True):

    #
    # needcont: Currently processing a continuing string
    # contstr: The string currently being built
    # endprog: The match condition for ending a continuing string
    raw_data = file_interface.read()
    try:
        data = raw_data.decode(encoding)
    except AttributeError:
        data = raw_data

    # last_line = b""
    # line = b""
    # line_no = 0
    # while True:
    #     try:
    #         last_line = line
    #         line = file_interface()
    #     except StopIteration:
    #         line = b""
    #     if encoding is not None:
    #         line = line.decode(encoding)
    #     line_no += 1
    #     pos, max = 0, len(line)

    pos, maxlen = 0, len(data)
    line_start, line_end = 0, 0
    line_no = 0
    while pos < maxlen:
        # if pos > 3050:
        #     return
        _previous_pos = pos
        if line_end <= pos:
            line_no += 1
            # work out the line end for line-slicing
            line_start = line_end
            line_end = data.find("\n", pos) + 1
            if line_end == 0:
                line_end = maxlen
        line = data[line_start:line_end]
        line_remaining = data[pos:line_end]
        if verbose:
            print("Processing line: \033[37m" + repr(data[line_start:pos] +"_e_[30;1m|_e_[0m" + data[pos:line_end]).replace("_e_", "\033"))

        if match := reWhitespace.match(line_remaining):
            # Skip whitespace
            pos += match.end()
        elif data[pos] == "\\" and not (pos+1) == maxlen and data[pos+1] == "\n":
            # Handle swallowing escaped newlines
            if verbose:
                print("Escaped newline")
            pos += 2
        elif data[pos] == "\n":
            if verbose:
                print(f"NEWLINE")
            pos += 1
            yield TokenInfo(type=token.NEWLINE, string="\n", start=(line_no, pos-1), end=(line_no, pos), line=line)
        elif match := reName.match(line_remaining):
            if verbose:
                print(f"NAME: {match.group(0)}")
            pos += match.end()
            yield TokenInfo(type=token.NAME, string=match.group(0), start=(line_no, match.start()), end=(line_no, match.end()), line=line)
        elif data[pos] == "#":
            pos = line_end
        elif number := read_number(line_remaining):
            if verbose:
                print(f"NUMBER: {number}")
            yield TokenInfo(type=token.NUMBER, string=number, start=(line_no, pos), end=(line_no, pos+len(number)), line=line)
            pos += len(number)
        elif string := reStringStart.match(data, pos=pos):
            quote_type = string.group()
            end_pattern = r"(?<!\\)" + quote_type
            re_endquote = re.compile(end_pattern, re.M | re.S)
            end_match = re_endquote.search(data, pos=pos+len(quote_type))
            assert end_match, "Unterminated string"
            contents = data[string.start()+len(quote_type):end_match.end()-len(quote_type)]
            # Found the start of some string
            # data.find(quote_type, pos=pos+len(string))
            if verbose:
                print(f"STRING: {contents!r}")
            pos = end_match.end()
        else:
            if verbose:
                print(f"CHAR: {data[pos]}")
            yield TokenInfo(type=token.OP, string=data[pos], start=(line_no, pos), end=(line_no, pos+1), line=line)
            # print("Something else?")
            pos += 1

        assert pos != _previous_pos, "Didn't advance position"

    return TokenInfo(type=token.ENDMARKER, string="", start=pos, end=pos, line="")


Mark = int  # NewType('Mark', int)

exact_token_types = token.EXACT_TOKEN_TYPES  # type: ignore


def shorttok(tok: tokenize.TokenInfo) -> str:
    return (
        "%-25.25s"
        % f"{tok.start[0]}.{tok.start[1]}: {token.tok_name[tok.type]}:{tok.string!r}"
    )


class Tokenizer:
    """Caching wrapper for the tokenize module.

    This is pretty tied to Python's syntax.
    """

    _tokens: List[tokenize.TokenInfo]

    def __init__(
        self, tokengen: Iterator[tokenize.TokenInfo], *, verbose: bool = False
    ):
        self._tokengen = tokengen
        self._tokens = []
        self._index = 0
        self._verbose = verbose
        if verbose:
            self.report(False, False)

    def getnext(self) -> tokenize.TokenInfo:
        """Return the next token and updates the index."""
        cached = True
        while self._index == len(self._tokens):
            tok = next(self._tokengen)
            if tok.type in (tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT,):
                continue
            # Transform NL to NEWLINE
            if tok.type == token.NL:
                tok = tokenize.TokenInfo(
                    token.NEWLINE,
                    tok.string,
                    start=tok.start,
                    end=tok.end,
                    line=tok.line,
                )
            if tok.type == token.ERRORTOKEN and tok.string.isspace():
                continue
            self._tokens.append(tok)
            cached = False
        tok = self._tokens[self._index]
        self._index += 1
        if self._verbose:
            self.report(cached, False)
        return tok

    def peek(self) -> tokenize.TokenInfo:
        """Return the next token *without* updating the index."""
        while self._index == len(self._tokens):
            tok = next(self._tokengen)
            if tok.type in (tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT,):
                continue
            # Transform NL to NEWLINE
            if tok.type == token.NL:
                tok = tokenize.TokenInfo(
                    token.NEWLINE,
                    tok.string,
                    start=tok.start,
                    end=tok.end,
                    line=tok.line,
                )
            if tok.type == token.ERRORTOKEN and tok.string.isspace():
                continue
            self._tokens.append(tok)
        return self._tokens[self._index]

    def diagnose(self) -> tokenize.TokenInfo:
        if not self._tokens:
            self.getnext()
        return self._tokens[-1]

    def mark(self) -> Mark:
        return self._index

    def reset(self, index: Mark) -> None:
        if index == self._index:
            return
        assert 0 <= index <= len(self._tokens), (index, len(self._tokens))
        old_index = self._index
        self._index = index
        if self._verbose:
            self.report(True, index < old_index)

    def report(self, cached: bool, back: bool) -> None:
        if back:
            fill = "-" * self._index + "-"
        elif cached:
            fill = "-" * self._index + ">"
        else:
            fill = "-" * self._index + "*"
        if self._index == 0:
            print(f"{fill} (Bof)")
        else:
            tok = self._tokens[self._index - 1]
            print(f"{fill} {shorttok(tok)}")
