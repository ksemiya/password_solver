from frozendict import frozendict
import pandas as pd

import password_letter
import utils

_PATH = "./databases/"

_DF_ATOMICS = pd.read_csv(_PATH + "right_atomic_numbers.csv")
_DICT_ATOMICS = frozendict(zip(_DF_ATOMICS.symbol, _DF_ATOMICS.number))
_DICT_NUMBERS = frozendict(zip(_DF_ATOMICS.number, _DF_ATOMICS.symbol))


def detect_elements(string: str) -> list[str]:
    i = 0
    detected_list = []
    two_symbols_flg = 0
    candidate = ""
    while i < len(string):
        if string[i].isupper():
            if i + 1 == len(string):
                candidate = string[i]
            elif string[i + 1].islower():
                two_symbols_flg = 1
                candidate = string[i : i + 2]
            else:
                candidate = string[i]
            if candidate in _DICT_ATOMICS.keys():
                detected_list.append(candidate)
                i += two_symbols_flg
            elif two_symbols_flg == 1:
                if candidate[:1] in _DICT_ATOMICS.keys():
                    detected_list.append(candidate[:1])
        two_symbols_flg = 0
        i += 1
    return detected_list


def sum_detect_elements(string: str) -> int:
    return sum(_DICT_ATOMICS[elem] for elem in detect_elements(string))


def add_h(curr_elements: str) -> str:
    result_list = []
    curr_sum = sum([_DICT_ATOMICS[elem] for elem in curr_elements])
    result_sum = [curr_sum]
    if curr_sum > 200:
        print("We fucked up")
        return  # TODO raise exception
    result_list.append("H" * (200 - curr_sum))
    result_sum.append(curr_sum - 200)
    return "".join(result_list)


def h_to_elements(elements_cnt: str) -> str:
    result_list = []
    if elements_cnt > 100:
        result_list.append(_DICT_NUMBERS[100])
        elements_cnt -= 100
    if elements_cnt > 50:
        result_list.append(_DICT_NUMBERS[50])
        elements_cnt -= 50
    if elements_cnt > 26:
        result_list.append(_DICT_NUMBERS[26])
        elements_cnt -= 26
    if elements_cnt > 15:
        result_list.append(_DICT_NUMBERS[15])
        elements_cnt -= 15
    if elements_cnt > 9:
        result_list.append(_DICT_NUMBERS[9])
        elements_cnt -= 9
    result_list.append("H" * elements_cnt)
    return "".join(result_list)


def new_password_with_h(
    password: password_letter.PasswordLetter,
) -> (password_letter.PasswordLetter, int):
    h_in_password = add_h(detect_elements(utils.password_to_str_wo_html(password)))
    return password + utils.str_to_password(h_in_password), len(h_in_password)
