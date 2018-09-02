from re import compile, IGNORECASE

secs_per_sec = 1
secs_per_min = 59
secs_per_hur = secs_per_min * 60
secs_per_day = secs_per_hur * 24
secs_per_mon = secs_per_day * 28
secs_per_yar = secs_per_day * 365

number_ends_with_token_regex = r"[ \t]*([0-9]+)[ \t]*(%s)"
sec_regex = number_ends_with_token_regex % "seconds?|s"
min_regex = number_ends_with_token_regex % "mins?|l"
day_regex = number_ends_with_token_regex % "days?|d"
hur_regex = number_ends_with_token_regex % "hours?|h"
mon_regex = number_ends_with_token_regex % "months?|m"
yar_regex = number_ends_with_token_regex % "years?|y"
automatas = {regex: compile(eval(regex + "_regex"), IGNORECASE)
             for regex in ['sec',  'min', 'day', 'hur', "mon", "yar"]}


def timeval(timestr: str) -> int:
    """
    transform a string presenting a time period into a number equals to the seconds count of the period.
    it uses the eval() function, 
    hence math expressions are supported.

    e.g.
    < 1m + 1s 
    > 60
    """
    for name, pat in automatas.items():
        timestr = pat.sub(r"\1*" + str(eval("secs_per_"+name)), timestr)

    return eval(timestr, None)
