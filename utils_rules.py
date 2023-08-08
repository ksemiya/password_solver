"""function for exceptional symbols in password"""
import password_letter


def strong_password():
    """add symbols for rule 21

    Strong emojii contains several unicode symbols, what is why
    it is done by using for instead of just string and
    utils.str_to_password()"""
    return [
        password_letter.PasswordLetter("🏋️‍♂️") for _ in range(3)
    ]  # bc of unicode bruh


def paul_egg():
    """add symbol for rule 17"""
    return [password_letter.PasswordLetter("🥚")]
