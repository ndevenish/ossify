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
