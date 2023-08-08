import re
import string
import time
from datetime import datetime


import pandas as pd


import captcha_solver
import chess_solver
import password_driver_wrapper
import password_letter
import geo_solver
import today_rules
import utils
import utils_chemical

THRESHOLD = 1  # magic int; I think it will be enough degree of freedom

YT_CHEATSHEET = pd.read_csv(PATH + "youtube_cheatsheet.csv")

FONT_SIZE_LIST = [28, 32, 36, 42, 49, 64, 81, 0, 1, 4, 9, 12, 16, 25]

PAUL_CONST = 3

FMT_TIME = "%I:%M"


def strong_password():
    return [
        password_letter.PasswordLetter("🏋️‍♂️") for _ in range(3)
    ]  # bc of unicode bruh


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

    return (
        duration_list,
        "youtu.be/" + YT_CHEATSHEET[YT_CHEATSHEET.duration == duration].url.values[0],
    )


def italic_formatting(
    password: list[password_letter.PasswordLetter],
) -> list[password_letter.PasswordLetter]:
    bold_cnt = sum([letter.bold for letter in password])
    for i in range(bold_cnt * 2):
        password[i + 2].italic = True
    return password


def wingdings_formatting(
    password: list[password_letter.PasswordLetter],
) -> list[password_letter.PasswordLetter]:
    wingdings_cnt = len(password) // 3 + 1
    i = 2
    curr_w_cnt = 0
    while curr_w_cnt <= wingdings_cnt:
        if password[i].letter not in "IVX":
            password[i].font = "Wingdings"
            curr_w_cnt += 1
        i += 1
    return password


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))


def color_solver(driver: password_driver_wrapper.PasswordDriverWrapper):
    rgb_str = driver.get_rgb_color()
    rgb = re.findall(r"\d+", rgb_str)
    hex_ = rgb_to_hex(*rgb)
    color_digit_sum = sum_digits_in_str(hex_)
    while color_digit_sum > THRESHOLD:
        time.sleep(1)
        driver.refresh_color()
        rgb_str = driver.get_rgb_color()
        rgb = re.findall(r"\d+", rgb_str)
        hex_ = rgb_to_hex(*rgb)
        color_digit_sum = sum_digits_in_str(hex_)
    return hex_, color_digit_sum


def font_size_change(
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    letters_dict = {}
    for letter in password:
        curr_l = letter.letter.lower()
        if curr_l.isalpha():
            if curr_l in letters_dict:
                letters_dict[curr_l] += 1
                letter.font_size = str(FONT_SIZE_LIST[letters_dict[curr_l]])
            else:
                letters_dict[curr_l] = 0
    return password


def main():
    free_digit = 25
    first_password = (
        "1" * 25
        + "$0XXXVpepsimayHeiamloved"
        + today_rules.today_wordle()
        + today_rules.today_moon_phase()
    )  # add leap year in the beginning

    password = utils.str_to_password(first_password)
    password = password + strong_password()

    driver = password_driver_wrapper.PasswordDriverWrapper()
    driver.update_password(utils.str_to_password(password))

    # rule 10
    password, captcha_digit_sum = captcha_solver.captcha_new_password(driver, password)
    free_digit -= captcha_digit_sum
    driver.update_password(utils.str_to_password(password))

    # rule 14
    password = geo_solver.geo_solver(driver, password)
    driver.update_password(utils.str_to_password(password))

    # rule 16
    password, chess_digit_sum = chess_solver.solver(driver, password)
    free_digit -= chess_digit_sum
    driver.update_password(utils.str_to_password(password))

    # rule 17

    # rule 18
    password = utils_chemical.new_password_with_h(password)
    driver.update_password(utils.str_to_password(password))

    # rule 20
    driver.update_password(utils.str_to_password(password))

    # rule 23
    password = utils.str_to_password("🐔🐛🐛") + password[1:]
    driver.update_password(utils.str_to_password(password))

    # rule 24
    yt_rule = driver.get_YT_rule()
    duration_list, youtube_url = youtube_solver(yt_rule)
    youtube_url_sum = sum_digits_in_str(youtube_url)
    free_digit = free_digit - youtube_url_sum
    password = password[:PAUL_CONST] + password[PAUL_CONST + youtube_url_sum :]
    youtube_url_elements_sum = sum(
        [DICT_ATOMICS[elem] for elem in detect_elements(youtube_url)]
    )
    password = password[: -len(H_in_password)]
    if youtube_url_elements_sum != 0:
        elements_in_password = H_in_password[:-youtube_url_elements_sum]
    else:
        elements_in_password = H_in_password
    new_elements_in_password = H_to_elements(elements_in_password)
    password = password + utils.str_to_password(new_elements_in_password)
    password = password + utils.str_to_password(youtube_url)
    driver.update_password(utils.str_to_password(password))

    # rule 25
    absence_eng_letter = sorted(
        list(
            set(string.ascii_lowercase)
            - set(utils.str_to_password_wo_html(password).lower())
        ),
        reverse=True,
    )
    scr_letter = (
        ord(absence_eng_letter[0]) - 96,
        ord(absence_eng_letter[1]) - 96,
    )  # TODO exceptions

    # there is some urls which contains w, need to be changed
    driver.sacrifice_letter(scr_letter[0])
    driver.sacrifice_letter(scr_letter[1])
    time.sleep(3)  # overwise smth goes wrong
    driver.confirm_sacrifice()

    # rule 26
    password = italic_formatting(password)
    driver.update_password(utils.str_to_password(password))

    # rule 27
    password = wingdings_formatting(password)
    driver.update_password(utils.str_to_password(password))
    time.sleep(1)

    # rule 28
    color, color_digit_sum = color_solver(driver)
    free_digit = free_digit - color_digit_sum
    password = (
        password[:PAUL_CONST]
        + password[PAUL_CONST + color_digit_sum :]
        + utils.str_to_password(color)
    )
    password = italic_formatting(password)
    driver.update_password(utils.str_to_password(password))

    # rule 31
    password = font_size_change(password)
    driver.update_password(utils.str_to_password(password))

    driver.maximize_window()

    # rule 32, 33, 35
    curr_time = datetime.now().strftime(FMT_TIME)
    digit_sum = sum_digits_in_str(curr_time)

    while free_digit - 5 < digit_sum:
        print("fucked up")
        driver.update_password(utils.str_to_password(password))
        time.sleep(15)
        curr_time = datetime.now().strftime(FMT_TIME)
        digit_sum = sum_digits_in_str(curr_time)

    last_digits = free_digit - digit_sum - 5  # 113 or 131 sum to 5

    password_len = len(password) - (last_digits // 10) + 1
    if password_len > 113:
        len_goal = 131
    else:
        len_goal = 113

    password = (
        password[:PAUL_CONST]
        + password[PAUL_CONST + free_digit :]
        + utils.str_to_password("9" * (last_digits // 9))
        + utils.str_to_password(str(last_digits % 9))
        + utils.str_to_password(str(len_goal) + " " + curr_time)
    )
    password = password + utils.str_to_password(" " * (len_goal - len(password)))
    password = wingdings_formatting(password)
    driver.update_password(utils.str_to_password(password))
    password = italic_formatting(password)
    driver.update_password(utils.str_to_password(password))
    time.sleep(1)
    driver.confirm_password()
    driver.set_final_answer(utils.str_to_password(password))

    time.sleep(30)
    driver.quit()


if __name__ == "__main__":
    main()
