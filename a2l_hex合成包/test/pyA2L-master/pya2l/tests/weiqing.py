from collections import namedtuple, OrderedDict
import enum

CompuTab = namedtuple("CompuTabRange", "inVal outVal")
print(CompuTab.index)
print(CompuTab.count)
print(CompuTab.inVal)
sub=CompuTab("a","b")

class ValueType(enum.IntEnum):

    INT = 0
    FLOAT = 2
    STRING = 3
    IDENT = 4

print(ValueType.FLOAT.value)