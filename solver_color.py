import re

import password_driver_wrapper
import password_letter
import utils
import utils_rules

THRESHOLD = 1


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))


def color_solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
):
    rgb_str = driver.get_rgb_color()
    rgb = re.findall(r"\d+", rgb_str)
    hex_ = rgb_to_hex(*rgb)
    color_digit_sum = utils.sum_digits_in_str(hex_)
    while color_digit_sum > THRESHOLD:
        driver.refresh_color()
        driver.update_password(utils.password_to_str(password))
        rgb_str = driver.get_rgb_color()
        rgb = re.findall(r"\d+", rgb_str)
        hex_ = rgb_to_hex(*rgb)
        color_digit_sum = utils.sum_digits_in_str(hex_)
    return hex_, color_digit_sum


def solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    color, color_digit_sum = color_solver(driver, password)
    paul_and_caterpillars = utils_rules.paul_chicken_and_caterpillars()
    paul_len = len(paul_and_caterpillars)
    password = (
        paul_and_caterpillars
        + password[paul_len + color_digit_sum :]
        + utils.str_to_password(color)
    )
    password = utils_rules.italic_formatting(password)
    return password, color_digit_sum
