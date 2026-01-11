#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from pyparsing import (
    Word,
    Combine,
    Optional,
    And,
    quotedString,
    oneOf,
    nums,
    Or,
    Suppress,
    alphanums,
)
from datetime import datetime

cvtInt = lambda toks: int(toks[0])
cvtReal = lambda toks: float(toks[0])
cvtDatetime = lambda toks: datetime(toks[0])
extEq = lambda toks: "%s eq " + str(toks[0])
extGreatOp = lambda toks: "gt" if toks[0] == ">" or toks[0] == "]" else "ge"
extGreat = lambda toks: "%s " + toks[0] + " " + str(toks[1])
extLessOp = lambda toks: "lt" if toks[0] == "<" or toks[0] == "[" else "le"
extLess = lambda toks: "%s " + toks[0] + " " + str(toks[1])
extLessInt = lambda toks: "%s " + toks[2] + " " + str(toks[1])
extInt = (
    lambda toks: "%s "
    + toks[0]
    + " "
    + str(toks[1])
    + " and %s "
    + toks[3]
    + " "
    + str(toks[2])
)
quoteAlphanums = lambda toks: "'" + toks[0] + "'"
requoteString = lambda toks: "'" + toks[0] + "'"
label = alphanums + "_"

integer = Combine(Optional(oneOf("+ -")) + Word(nums)).setParseAction(cvtInt)
exponent = Optional(oneOf("+ -")) + Word(nums)
real = Combine(
    Optional(oneOf("+ -"))
    + Word(nums)
    + "."
    + Optional(Word(nums))
    + Optional(oneOf("e E") + exponent)
).setParseAction(cvtReal)
date_part = Combine(Word(nums) + "-" + Word(nums) + "-" + Word(nums))
time_part = Combine(Word(nums) + ":" + Word(nums) + ":" + Word(nums))
date = Combine(Optional(date_part) + time_part).setParseAction(cvtDatetime)
lterm = (
    Word(label).setParseAction(quoteAlphanums)
    | quotedString.setParseAction(requoteString)
    | integer
    | real
    | date
)
uterm = Or([quotedString.setParseAction(requoteString), integer, real, date])
bracket = oneOf("] [")
interval = Or(
    [
        And(
            [bracket, Suppress(":"), uterm, bracket.copy().setParseAction(extLessOp)]
        ).setParseAction(extLessInt),
        And(
            [bracket.copy().setParseAction(extGreatOp), lterm, Suppress(":"), bracket]
        ).setParseAction(extGreat),
        And(
            [
                bracket.copy().setParseAction(extGreatOp),
                lterm,
                Suppress(":"),
                uterm,
                bracket.copy().setParseAction(extLessOp),
            ]
        )
        .setName("double")
        .setParseAction(extInt),
    ]
)
gexpr = And([oneOf("> >=").setParseAction(extGreatOp), lterm]).setParseAction(extGreat)
lexpr = And([oneOf("< <=").setParseAction(extLessOp), uterm]).setParseAction(extLess)
eexpr = And([Suppress(Optional("=")), lterm]).setParseAction(extEq)
criterion_parser = eexpr | interval | gexpr | lexpr
criterion_parser.verbose_stacktrace = True
