import time
import today_rules  # I should change that but idk how
import passwordDriverWrapper
import re
import requests
import pandas as pd
from xml.etree import ElementTree as ET

THRESHOLD = 1  # magic int; I think it will be enough degree of freedom

DF_COUNTRIES = pd.read_json("maps.jsonc")

DF_ATOMICS = pd.read_csv("right_atomic_numbers.csv")
DICT_ATOMICS = dict(zip(DF_ATOMICS.symbol, DF_ATOMICS.number))
DICT_NUMBERS = dict(zip(DF_ATOMICS.number, DF_ATOMICS.symbol))


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


def get_chess_position(chess_img):
    # Make a request to the URL
    response = requests.get(chess_img)

    # Check if the request was successful
    if response.status_code == 200:
        svg_data = response.content

        # Parse SVG data
        tree = ET.ElementTree(ET.fromstring(svg_data))

        # Loop over all elements in the SVG
        for elem in tree.iter():
            if elem.text is not None:
                chess_position = elem.text
                return chess_position
    else:
        print("Failed to fetch SVG.")  # TODO raise Err
    return


def color_move(chess_move):
    if "White" in chess_move:
        return "w"
    if "Black" in chess_move:
        return "b"
    return "WRONG MOVE"


def from_svg_to_FEN(chess_position, chess_move):
    # Remove leading/trailing white space and split the string into lines
    rows = chess_position.strip().split("\n")

    # Initialize an empty list to hold FEN rows
    fen_rows = []

    # Iterate over rows
    for row in rows:
        # Remove leading/trailing white space and split row into squares
        squares = row.strip().split(" ")
        # Initialize counter for empty squares
        empty = 0
        # Initialize an empty string to hold FEN for this row
        fen_row = ""
        # Iterate over squares
        for square in squares:
            if square == ".":
                # Increment counter for empty squares
                empty += 1
            else:
                # If the square is not empty and there were empty squares before, add count to FEN
                if empty > 0:
                    fen_row += str(empty)
                    # Reset empty squares counter
                    empty = 0
                # Add piece to FEN
                fen_row += square
        # If the row ends with one or more empty squares, add count to FEN
        if empty > 0:
            fen_row += str(empty)
        # Add FEN for this row to the list of FEN rows
        fen_rows.append(fen_row)
    # Join the FEN rows with slashes to get the final FEN
    fen_board = "/".join(fen_rows)
    fen = fen_board + " " + color_move(chess_move) + " - - 0 1"

    return fen


def get_best_move(fen):
    import chess.engine

    # Define the path to your Stockfish engine file
    engine_path = "/opt/homebrew/Cellar/stockfish/16/bin/stockfish"

    # Initialize the chessboard with a given FEN
    board = chess.Board(fen)

    # Initialize the engine
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    # Find the best move
    result = engine.play(board, chess.engine.Limit(time=1.0))
    best_move = result.move

    # From UCI to algebraic notation
    best_move_alg_not = board.san(best_move)

    # It is good practice to close the engine after using it
    engine.quit()

    return best_move_alg_not


def solve_chess_position(chess_img, chess_move):
    chess_position = get_chess_position(chess_img)
    fen = from_svg_to_FEN(chess_position, chess_move)
    best_move = get_best_move(fen)
    return best_move


def detect_elements(s):
    i = 0
    detected_list = []
    two_symbols_flg = 0
    candidate = ""
    while i < len(s):
        if s[i].isupper():
            if i + 1 == len(s):
                candidate = s[i]
            elif s[i + 1].islower():
                two_symbols_flg = 1
                candidate = s[i : i + 2]
            else:
                candidate = s[i]
            if candidate in DICT_ATOMICS.keys():
                detected_list.append(candidate)
                i += two_symbols_flg
            elif two_symbols_flg == 1:
                if candidate[:1] in DICT_ATOMICS.keys():
                    detected_list.append(candidate[:1])
        two_symbols_flg = 0
        i += 1
    return detected_list


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

    geo_embed = driver.get_embed_geo
    country = (
        DF_COUNTRIES[DF_COUNTRIES.embed == geo_embed]
        .title.values[0]
        .lower()
        .replace(" ", "")
    )
    password = password + str_to_password(country)
    # rule 16
    chess_img = driver.get_chess_svg
    chess_move = driver.get_chess_move_text
    chess_solution = solve_chess_position(chess_img, chess_move)
    chess_digit_sum = sum([int(x) for x in re.findall(r"\d", chess_solution)])
    free_digit = free_digit - chess_digit_sum
    password = (
        str_to_password("🥚")
        + (password[chess_digit_sum:] if chess_digit_sum != 0 else password)
        + str_to_password(chess_solution)
    )

    driver.update_password(password_to_str(password))


if __name__ == "__main__":
    main()
