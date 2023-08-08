import string

import password_driver_wrapper
import password_letter
import utils


def sacrifice(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
) -> None:
    # rule 25
    absence_eng_letter = sorted(
        list(
            set(string.ascii_lowercase)
            - set(utils.password_to_str_wo_html(password).lower())
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
    # overwise smth goes wrong
    driver.confirm_sacrifice()
