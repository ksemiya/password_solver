import time
import today_rules  # I should change that but idk how
import passwordDriverWrapper
import re
import pandas as pd

THRESHOLD = 1  # magic int; I think it will be enough degree of freedom


class PasswordLetter:
    def __init__(self, letter: str) -> None:
        self.letter = letter
        # rule vowels are bold
        self.bold = True if letter in "aeiouyAEIOUY" else False
        self.italic = False
        self.font_size = int(letter) * int(letter) if letter.isdigit() else None
        self.font = "Times New Roman" if letter in "IVX" else None

    def to_html(self):
        result = self.letter
        if self.bold:
            result = f"<strong>{result}</strong>"
        if self.italic:
            result = f"<i>{result}</i>"
        if self.font_size is not None or self.font is not None:
            self.font_size = "28" if self.font_size is None else self.font_size
            self.font = "Monospace" if self.font is None else self.font
            result = f'<span style="font-family: {self.font}; font-size: {self.font_size}px">{result}</span>'
        return result


def password_to_str(password: list[PasswordLetter]) -> str:
    return "".join([letter.to_html() for letter in password])


def password_to_str_wo_html(password: list[PasswordLetter]) -> str:
    return "".join([letter.letter for letter in password])


def str_to_password(string: str) -> list[PasswordLetter]:
    return [PasswordLetter(letter) for letter in string]


def strong_password():
    return [PasswordLetter("🏋️‍♂️") for _ in range(3)]  # bc of unicode bruh


def sum_digits_in_str(string: str) -> int:
    return sum([int(x) for x in re.findall(r"\d", string)])


def captcha_solver(driver: passwordDriverWrapper.PasswordDriverWrapper):
    captcha_img = driver.get_current_captcha_url()
    captcha = captcha_img[40:45]
    captcha_digit_sum = sum_digits_in_str(captcha)
    while captcha_digit_sum > THRESHOLD:
        time.sleep(1)
        driver.refresh_captcha()
        captcha_img = driver.get_current_captcha_url()
        captcha = captcha_img[40:45]
        captcha_digit_sum = sum_digits_in_str(captcha)
    return captcha, captcha_digit_sum


def main():
    free_digit = 25
    first_password = (
        "1" * 25
        + "$0XXXVpepsimayHe iamloved"
        + today_rules.today_wordle()
        + today_rules.today_moon_phase()
    )  # add leap year in the beginning

    password = str_to_password(first_password)
    password = password + strong_password()

    driver = passwordDriverWrapper.PasswordDriverWrapper()
    time.sleep(1)
    driver.update_password(password_to_str(password))
    # rule 10
    captcha, captcha_digit_sum = captcha_solver()
    free_digit = free_digit - captcha_digit_sum
    password = (
        password[captcha_digit_sum:] if captcha_digit_sum != 0 else password
    ) + str_to_password(captcha)
    driver.update_password(password_to_str(password))
    # rule 14
    countiers = pd.read_json("maps.jsonc")
    geo_embed = driver.get_embed_geo
    country = (
        countiers[countiers.embed == geo_embed].title.values[0].lower().replace(" ", "")
    )
    password = password + str_to_password(country)
    return


if __name__ == "__main__":
    main()
