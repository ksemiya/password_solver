"""Function to solve captcha and return new password"""
import password_driver_wrapper
import password_letter
import utils

_THRESHOLD = 1  # magic int; I think it will be enough degree of freedom


def captcha_solver(driver: password_driver_wrapper.PasswordDriverWrapper) -> (str, int):
    """Sovle captcha"""
    captcha_img = driver.get_current_captcha_url()
    captcha = captcha_img[40:45]
    captcha_digit_sum = utils.sum_digits_in_str(captcha)
    while captcha_digit_sum > _THRESHOLD:
        driver.refresh_captcha()
        captcha_img = driver.get_current_captcha_url()
        captcha = captcha_img[40:45]
        captcha_digit_sum = utils.sum_digits_in_str(captcha)
    return captcha, captcha_digit_sum


def captcha_new_password(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
) -> (password_letter.PasswordLetter, int):
    """Return new password"""
    captcha, captcha_digit_sum = captcha_solver(driver)
    return (
        password[captcha_digit_sum:] if captcha_digit_sum != 0 else password
    ) + utils.str_to_password(captcha), captcha_digit_sum
