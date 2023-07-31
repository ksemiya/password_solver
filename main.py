import today_rules  # I should change that but idk how
import passwordDriverWrapper


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

    # driver.

    return


if __name__ == "__main__":
    main()
