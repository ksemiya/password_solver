"""utils.py contains some functions which works with list[PasswordLetter]"""
import re

import password_letter


def password_to_str(password: list[password_letter.PasswordLetter]) -> str:
    """Convert list[PasswordLetter] to string with all html notation"""
    return "".join([letter.to_html() for letter in password])


def password_to_str_wo_html(password: list[password_letter.PasswordLetter]) -> str:
    """Convert list[PasswordLetter] to string without the html notation"""
    return "".join([letter.letter for letter in password])


def str_to_password(string: str) -> list[password_letter.PasswordLetter]:
    """Convert string to list[PasswordLetter]"""
    return [password_letter.PasswordLetter(letter) for letter in string]


def sum_digits_in_str(string: str) -> int:
    """Sum all digits in string and return sum"""
    return sum(int(x) for x in re.findall(r"\d", string))
