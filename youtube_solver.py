from frozendict import frozendict
import pandas as pd
import re

import password_driver_wrapper
import password_letter
import utils
import utils_chemical
import utils_rules

_DF_PATH = "./databases/"
_YT_CHEATSHEET = pd.read_csv(_DF_PATH + "youtube_cheatsheet.csv")
_DICT_YT = frozendict(zip(_YT_CHEATSHEET.duration, _YT_CHEATSHEET.url))


def youtube_solver(yt_rule: str):
    exact_time = re.findall(
        "Your password must include the URL of an exactly \d+ minute long YouTube video",
        yt_rule,
    )
    if len(exact_time) > 0:
        duration_list = re.findall(r"\d+", exact_time[0]) + ["0"]
    else:
        duration_list = re.findall(
            r"\d+",
            re.findall(
                "Your password must include the URL of a \d+ minute \d+ second long YouTube video",
                yt_rule,
            )[0],
        )
    duration = int(duration_list[0]) * 60 + int(duration_list[1])

    return "youtu.be/" + _DICT_YT[duration]


def solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
    h_cnt: int,
) -> password_letter.PasswordLetter:
    yt_rule = driver.get_YT_rule()
    youtube_url = youtube_solver(yt_rule)
    youtube_url_sum = utils.sum_digits_in_str(youtube_url)
    paul_and_caterpillars = utils_rules.paul_chicken_and_caterpillars()
    paul_len = len(paul_and_caterpillars)
    password = paul_and_caterpillars + password[paul_len + youtube_url_sum :]
    youtube_url_elements_sum = utils_chemical.sum_detect_elements(youtube_url)
    password = password[:-h_cnt]
    if youtube_url_elements_sum != 0:
        elements_in_password = h_cnt - youtube_url_elements_sum
    else:
        elements_in_password = h_cnt
    new_elements_in_password = utils_chemical.h_to_elements(elements_in_password)
    password = password + utils.str_to_password(new_elements_in_password)
    password = password + utils.str_to_password(youtube_url)
    return password
