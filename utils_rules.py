"""function for exceptional symbols in password"""
import password_letter
import utils

FONT_SIZE_LIST = [28, 32, 36, 42, 49, 64, 81, 0, 1, 4, 9, 12, 16, 25]


def strong_password():
    """add symbols for rule 21

    Strong emojii contains several unicode symbols, what is why
    it is done by using for instead of just string and
    utils.str_to_password()"""
    return [
        password_letter.PasswordLetter("🏋️‍♂️") for _ in range(3)
    ]  # bc of unicode bruh


def paul_egg(
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    """add symbol for rule 17"""
    return utils.str_to_password("🥚") + password


def paul_chicken_and_caterpillars_after_egg(
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    return utils.str_to_password("🐔🐛🐛") + password[1:]


def paul_chicken_and_caterpillars() -> password_letter.PasswordLetter:
    return utils.str_to_password("🐔🐛🐛")


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
