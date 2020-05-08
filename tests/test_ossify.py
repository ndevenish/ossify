import pytest

from ossify import grammar
from ossify.testutil import parse_string

# , parser_for


def check_raises(content):
    with pytest.raises(SyntaxError) as e:
        parse_string(content)
    return str(e.value)


def test_empty_scope():
    parse_string("a {}")


def test_leading_newline():
    test_scope = "a {\n  b = 1\n}"
    parse_string(test_scope)
    parse_string("\n" + test_scope)


def test_parses():
    parse_string(
        """
    options.something = some sort *of choice
        .help = "whaaaat"
        .optional = True
        .caption =  "Some long description"
                    "a second line"
        .short_caption=4
    another.option = "some"
    file.name = file.mds
    """
    )
    parse_string("name = file.mds")
    # multiline string
    parse_string("a = 'a'\n'b'\n'c' 4")


def test_subscope():
    parse_string("scope {\n  options.b = 4\n}")
    parse_string("scope { options.b = 4 }")
    # TODO: Merge these tests as they should give an equivalent
    # assert parse_string("scope { options.b = 4 }") == simple_subscope


def test_multiple_definitions_root_scope():
    defs = parse_string("a = 1\n  b = 2")
    assert len(defs.children) == 2
    assert all(isinstance(x, grammar.Definition) for x in defs.children)


def test_multiple_scope_definitions():
    root_scope = parse_string("scope {\n  a = 1\n  b = 2\n}", verbose=True)
    assert isinstance(root_scope.children[0], grammar.Scope)
    assert len(root_scope.children[0].children) == 2
    assert all(
        isinstance(x, grammar.Definition) for x in root_scope.children[0].children
    )
    assert str(root_scope.children[0].children[0].name) == "a"
    assert str(root_scope.children[0].children[1].name) == "b"


def test_things_that_dont_work():
    check_raises('b="3" some { cat = 9 }')
    check_raises("a = 'a'\n'b'\n'c'\n3")
    # anonymous scope
    assert "anonymous" in check_raises("{ a = 2 }")
    # Subscopes don't have values
    check_raises("options.a = 2 { subscope }")


def test_string_continuation():
    parse_string('a = "Some long description"\n  "a second line"')


def test_options():
    parse_string("a = 2\n  .caption='goodoption'")
    assert "unknown option" in check_raises("a = 2\n .badoption = 3").lower()


def test_badquote_multiline_string():
    # Even if defined as """ string, prints self as a single quoted string
    # - although can parse this so technically part of the spec
    parse_string(
        """experiments = None
    .help = "The output experiment list file name.
            If None, don't"
            "output an experiment list file.\""""
    )
    parse_string(
        """experiments = None
    .help = 'The output experiment list file name.
            If None, dont'
            "output an experiment list file.\""""
    )


def test_badquote_multiline_string_2():
    parse_string(
        """intensities = "Choice of which intensities to export. Allowed combinations:
      "
          "     scale, profile, sum, profile+sum, sum+profile+scale. Auto"
          "will
            default to scale or profile+sum depending on if"
          "the data are scaled."
        """
    )


def test_multiline_string_dedent():
    # This test case causes tokenizer problems
    r = parse_string(
        """require_images = True
  .help = "Flag which can be set to False to launch image viewer without
     "
          "checking the image format (needed for some image format classes).
 "
 """
    )
    r.print_scope()


def test_multiple_newline():
    parse_string("something = 3\n\nanother = 4")
    parse_string("something {\n}\n\nanother{}")


def test_escaped_line():
    parse_string(
        """display = *image mean variance dispersion sigma_b sigma_s threshold \
          global_threshold
  .help = None"""
    )


def test_comment():
    parse_string("some = 3 # comment\n# another comment\nb = 3\n#after")


def test_close_semicolon():
    tree = parse_string("""some = 3; .help=help""")
    assert tree.children[0].options["help"]


def test_nested_scope_definition():
    tree = parse_string("a.b.c = 2")
    assert tree.children[0].children[0].children[0].name == "c"

    tree = parse_string("a.b.c{d=1}")
    assert tree.children[0].children[0].children[0].name == "c"
    assert tree.children[0].children[0].children[0].children[0].name == "d"
    assert isinstance(
        tree.children[0].children[0].children[0].children[0], grammar.Definition
    )


def test_include():
    parse_string("include file something.phil")
    parse_string("include scope a.b.c.d")
    # subscope
    parse_string("include scope a.b.c.d smething")


def test_scope_inline_options():
    parse_string(
        """something
.multiple = True {
}"""
    )
