import pytest
from ossify.tokenizer import character_generator


@pytest.mark.skip("is a test test")
def test_character_generator():
    with open("/Users/nickd/dials/ossify/all_dials.phil") as f:
        gen = character_generator(f)

        for t in gen:
            pass
