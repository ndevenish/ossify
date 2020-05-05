import pytest
from ossify import grammar
from ossify.testutil import parse_string, parser_for


def check_raises(content):
    with pytest.raises(SyntaxError) as e:
        parse_string(content)
    return str(e.value)


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


def test_things_that_dont_work():
    check_raises('b="3" some { cat = 9 }')
    check_raises("a = 'a'\n'b'\n'c'\n3")
    # anonymous scope
    assert "anonymous" in check_raises("{ a = 2 }")
    # Subscopes don't have values
    check_raises("options.a = 2 { subscope }")


def test_string_continuation():
    parse_string('a = "Some long description"\n  "a second line"')
