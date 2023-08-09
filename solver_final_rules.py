from datetime import datetime

import password_driver_wrapper
import password_letter
import utils
import utils_rules

_FMT_TIME = "%I:%M"


def solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
    free_digit: int,
) -> password_letter.PasswordLetter:
    curr_time = datetime.now().strftime(_FMT_TIME)
    digit_sum = utils.sum_digits_in_str(curr_time)

    while free_digit - 5 < digit_sum:
        print("fucked up", free_digit, digit_sum)
        driver.update_password(utils.password_to_str(password))
        driver.wait(15)
        curr_time = datetime.now().strftime(_FMT_TIME)
        digit_sum = utils.sum_digits_in_str(curr_time)

    last_digits = free_digit - digit_sum - 5  # 113 or 131 sum to 5

    password_len = (
        len(password) - (last_digits // 10) + 1
    )  # we can present digits as 9's and % 9
    if password_len > 113:
        len_goal = 131
    else:
        len_goal = 113
    paul_and_caterpillars = utils_rules.paul_chicken_and_caterpillars()
    paul_len = len(paul_and_caterpillars)
    password = (
        paul_and_caterpillars
        + password[paul_len + free_digit :]
        + utils.str_to_password("9" * (last_digits // 9))
        + utils.str_to_password(str(last_digits % 9))
        + utils.str_to_password(str(len_goal) + " " + curr_time)
    )
    password = password + utils.str_to_password(" " * (len_goal - len(password)))
    password = utils_rules.wingdings_formatting(password)
    password = utils_rules.italic_formatting(password)

    return password
