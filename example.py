#!/usr/bin/env python3

from klauskleber import LabelPrinter, Label


if __name__ == "__main__":

    lp = LabelPrinter("/dev/ttyUSB1")

    label = Label(
            thing_id = "1337",
            thing_name = "Stuff",
            thing_maintainer = "Heinrich")

    lp.print_label(label)
