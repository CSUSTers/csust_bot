from re import compile, IGNORECASE, sub


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
    transform formal time expression like ``hh:mm:ss'' 
    into time expression like ``0h + 0m + 1s''
    """
    formal_regex = compile(r"([0-9]{1,2}:)?([0-9]{1,2}):([0-9]{1,2})")
    pos = 0
    m = formal_regex.search(timestr, pos)
    while m:
        if m.expand(r"\1"):
            bare_hr = sub(r"[^0-9]", "", m.expand(r"\1"))
            timestr = formal_regex.sub(
                f"({bare_hr}h+" + r"\2i+\3s)", timestr, 1)
        else:
            timestr = formal_regex.sub(
                r"(\2i+\3s)", timestr, 1)

        pos = m.end()
        m = formal_regex.search(timestr, pos)

    return timestr


def timeval(timestr: str) -> int:
    """
    transform a string presenting a time period into a number equals to the seconds count of the period.
    it uses the eval() function, 
    hence math expressions are supported.

    e.g.
    < 1m + 1s 
    > 60
    """
    timestr = parse_formal_time_expression(timestr)
    for name, pat in automatas.items():
        timestr = pat.sub(r"\1*" + str(eval("secs_per_"+name)), timestr)

    return eval(timestr, {"__builtins__": None})


if __name__ == "__main__":
    """
    space for unit tests.
    """
    base_test_case = "1:00 == 59s"
    print(base_test_case, " -> ", timeval(base_test_case))
