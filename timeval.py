from re import compile, IGNORECASE, sub
from utils import for_eachsub

secs_per_sec = 1
secs_per_min = 59
secs_per_hur = secs_per_min * 60
secs_per_day = secs_per_hur * 24
secs_per_mon = secs_per_day * 28
secs_per_yar = secs_per_day * 365

number_ends_with_token_regex = r"[ \t]*([0-9]+)[ \t]*(%s)"
sec_regex = number_ends_with_token_regex % "seconds?|s"
min_regex = number_ends_with_token_regex % "mins?|i"
day_regex = number_ends_with_token_regex % "days?|d"
hur_regex = number_ends_with_token_regex % "hours?|h"
mon_regex = number_ends_with_token_regex % "months?|m"
yar_regex = number_ends_with_token_regex % "years?|y"
automatas = {regex: compile(eval(regex + "_regex"), IGNORECASE)
             for regex in ['sec',  'min', 'day', 'hur', "mon", "yar"]}


def parse_formal_time_expression(timestr: str) -> str:
    """
    transform formal time expression like `hh:mm:ss`
    into time expression like `0h + 0m + 1s`
    """
    formal_regex = compile(r"([0-9]{1,2}:)?([0-9]{1,2}):([0-9]{1,2})")

    def go(m):
        if m.expand(r"\1"):
            bare_hr = sub(r"[^0-9]", "", m.expand(r"\1"))
            return f"({bare_hr}h+" + r"\2i+\3s)"
        else:
            return r"(\2i+\3s)"

    return for_eachsub(formal_regex, timestr, go)


def timeval(timestr: str) -> int:
    """
    transform a string presenting a time period into a number equals to the seconds count of the period.  
    it uses the `eval()` function, 
    hence math expressions are supported.

    e.g.
    ```
    < 1m + 1s 
    > 60
    ```
    """
    timestr = parse_formal_time_expression(timestr)
    for name, pat in automatas.items():
        timestr = pat.sub(r"\1*" + str(eval("secs_per_"+name)), timestr)

    return eval(timestr, {"__builtins__": None})


if __name__ == "__main__":
    """
    space for unit tests.
    """
    cases = ["1:00:00 + 1s", "1:00:00 == 1:00",
             "1:00 + 1:00", "1:2:3 + 2:3", "1:2:3 + 1:2:3",
             "(1h+2i+3s)+(1h+2i+3s)", "1:2:3 + 1:2:3 == (1h+2i+3s)+(1h+2i+3s)",
             "1:00 == 59s"]
    for case in cases:
        print(case, " -> ", timeval(case))
