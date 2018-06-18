from itertools import starmap, repeat
from operator import add, mod
from functools import reduce


def url_encode(s: str):
    """
    将字符串编码为搜索引擎需求的形式(%XX)。
    param {s} string to encode.
    ret the encoded string.

    example
    < 'flip flappers'
    > '%66%6c%69%70%20%66%6c%61%70%70%65%72%73'

    < '\01\02'
    > '%01%02'

    < "来自深渊今天更新了吗？"
    > "%e6%9d%a5%e8%87%aa%e6%b7%b1%e6%b8%8a%e4%bb%8a%e5%a4%a9%e6%9b%b4%e6%96%b0%e4%ba%86%e5%90%97%ef%bc%9f"
    """ 
    return reduce(add,
                  starmap(
                      mod, zip(repeat("%%%.2x"),
                      s.encode("utf-8"))), 
                  "")
    