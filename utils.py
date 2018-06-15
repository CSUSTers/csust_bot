from itertools import starmap, cycle, repeat
from operator import add, mod
from functools import reduce


def url_encode(s: str):
    """
    将字符串编码为搜索引擎需求的形式(%XX)。
    param {s} string to encode.
    ret the encoded string.

    example
    > 'flip flappers'
    > '%66%6c%69%70%20%66%6c%61%70%70%65%72%73'

    > '\01\02'
    > '%01%02'
    """
    encoded = s.encode("utf-8")
    firstprocess = starmap(add, zip(cycle("%"), 
                   starmap(mod, zip(repeat("%.2x"), encoded))))
    return reduce(add, firstprocess)
    