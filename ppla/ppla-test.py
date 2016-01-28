#!/usr/bin/env python3

from ppla import Text



def test_text():
    t = Text(1, "Hallo Welt!", 23, 42, orientation = 2, mult_x = 9)
    assert t.encode() == bytes("219100004200230Hallo Welt!\r", "CP437")
