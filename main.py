import time
import today_rules  # I should change that but idk how
import passwordDriverWrapper
import re
import requests
import string
import pandas as pd
from csv import writer
from datetime import datetime
from xml.etree import ElementTree as ET

THRESHOLD = 1  # magic int; I think it will be enough degree of freedom

DF_COUNTRIES = pd.read_json("maps.jsonc")

DF_ATOMICS = pd.read_csv("right_atomic_numbers.csv")
DICT_ATOMICS = dict(zip(DF_ATOMICS.symbol, DF_ATOMICS.number))
DICT_NUMBERS = dict(zip(DF_ATOMICS.number, DF_ATOMICS.symbol))

YT_CHEATSHEET = pd.read_csv("youtube_cheatsheet.csv")

FONT_SIZE_LIST = [28, 32, 36, 42, 49, 64, 81, 0, 1, 4, 9, 12, 16, 25]


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


def detect_elements(string: str) -> list[str]:
    i = 0
    detected_list = []
    two_symbols_flg = 0
    candidate = ""
    while i < len(string):
        if string[i].isupper():
            if i + 1 == len(string):
                candidate = string[i]
            elif string[i + 1].islower():
                two_symbols_flg = 1
                candidate = string[i : i + 2]
            else:
                candidate = string[i]
            if candidate in DICT_ATOMICS.keys():
                detected_list.append(candidate)
                i += two_symbols_flg
            elif two_symbols_flg == 1:
                if candidate[:1] in DICT_ATOMICS.keys():
                    detected_list.append(candidate[:1])
        two_symbols_flg = 0
        i += 1
    return detected_list


def add_H(curr_elements: str) -> str:
    result_list = []
    curr_sum = sum([DICT_ATOMICS[elem] for elem in curr_elements])
    result_sum = [curr_sum]
    if curr_sum > 200:
        print("We fucked up")
        return  # TODO raise exception
    result_list.append("H" * (200 - curr_sum))
    result_sum.append(curr_sum - 200)
    return "".join(result_list)


def H_to_elements(elements: str) -> str:
    elements_sum = len(elements)
    result_list = []
    if elements_sum > 100:
        result_list.append(DICT_NUMBERS[100])
        elements_sum -= 100
    if elements_sum > 50:
        result_list.append(DICT_NUMBERS[50])
        elements_sum -= 50
    if elements_sum > 26:
        result_list.append(DICT_NUMBERS[26])
        elements_sum -= 26
    if elements_sum > 15:
        result_list.append(DICT_NUMBERS[15])
        elements_sum -= 15
    if elements_sum > 9:
        result_list.append(DICT_NUMBERS[9])
        elements_sum -= 9
    result_list.append("H" * elements_sum)
    return "".join(result_list)


def youtube_solver(yt_rule: str):
    exact_time = re.findall(
        "Your password must include the URL of an exactly \d+ minute long YouTube video",
        yt_rule,
    )
    if len(exact_time) > 0:
        duration_list = re.findall(r"\d+", exact_time[0]) + ["0"]
    else:
        duration_list = re.findall(
            r"\d+",
            re.findall(
                "Your password must include the URL of a \d+ minute \d+ second long YouTube video",
                yt_rule,
            )[0],
        )
    duration = int(duration_list[0]) * 60 + int(duration_list[1])

    return (
        duration_list,
        "youtu.be/" + YT_CHEATSHEET[YT_CHEATSHEET.duration == duration].url.values[0],
    )


def italic_formatting(password: list[PasswordLetter]) -> list[PasswordLetter]:
    bold_cnt = sum([letter.bold for letter in password])
    for i in range(bold_cnt * 2):
        password[i + 2].italic = True
    return password


def wingdings_formatting(password: list[PasswordLetter]) -> list[PasswordLetter]:
    wingdings_cnt = len(password) // 3 + 1
    i = 2
    curr_w_cnt = 0
    while curr_w_cnt <= wingdings_cnt:
        if password[i].letter not in "IVX":
            password[i].font = "Wingdings"
            curr_w_cnt += 1
        i += 1
    return password


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))


def color_solver(driver: passwordDriverWrapper.PasswordDriverWrapper):
    rgb_str = driver.get_rgb_color()
    rgb = re.findall(r"\d+", rgb_str)
    hex_ = rgb_to_hex(*rgb)
    color_digit_sum = sum_digits_in_str(hex_)
    while color_digit_sum > THRESHOLD:
        time.sleep(1)
        driver.refresh_color()
        rgb_str = driver.get_current_captcha_url()
        rgb = rgb_str[40:45]
        hex_ = rgb_to_hex(*rgb)
        color_digit_sum = sum_digits_in_str(hex_)
    return hex_, color_digit_sum


def font_size_change(password: PasswordLetter) -> PasswordLetter:
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


def main():
    free_digit = 25
    first_password = (
        "1" * 25
        + "$0XXXVpepsimayHeiamloved"
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

    # rule 18
    H_in_password = add_H(detect_elements(password_to_str_wo_html(password)))
    password = password + str_to_password(H_in_password)
    driver.update_password(password_to_str(password))

    # rule 20
    driver.update_password(password_to_str(password))

    # rule 23
    password = str_to_password("🐔🐛🐛") + password[1:]
    driver.update_password(password_to_str(password))

    # rule 24
    yt_rule = driver.get_YT_rule()
    duration_list, youtube_url = youtube_solver(yt_rule)
    youtube_url_sum = sum([int(x) for x in re.findall(r"\d", youtube_url)])
    free_digit = free_digit - youtube_url_sum
    password = password[:2] + password[2 + youtube_url_sum :]
    youtube_url_elements_sum = sum(
        [DICT_ATOMICS[elem] for elem in detect_elements(youtube_url)]
    )
    password = password[: -len(H_in_password)]
    if youtube_url_elements_sum != 0:
        elements_in_password = H_in_password[:-youtube_url_elements_sum]
    new_elements_in_password = H_to_elements(elements_in_password)
    password = password + str_to_password(new_elements_in_password)
    password = password + str_to_password(youtube_url)
    driver.update_password(password_to_str(password))

    # rule 25
    absence_eng_letter = sorted(
        list(
            set(string.ascii_lowercase) - set(password_to_str_wo_html(password).lower())
        ),
        reverse=True,
    )
    scr_letter = (
        ord(absence_eng_letter[0]) - 96,
        ord(absence_eng_letter[1]) - 96,
    )  # TODO exceptions

    # logging
    yt_ok = True
    try:  # fuck it is so bad written
        driver.sacrifice_letter(scr_letter[0])
    except:
        yt_ok = False
    # List that we want to add as a new row
    log_list = [
        datetime.now(),
        password_to_str_wo_html(password),
        captcha,
        country,
        chess_img,
        chess_move,
        chess_solution,
        duration_list,
        youtube_url,
        "".join(absence_eng_letter),
        scr_letter,
        yt_ok,
    ]
    # Open our existing CSV file in append mode
    with open("logs.csv", "a") as f:
        writer_object = writer(f)
        writer_object.writerow(log_list)
        f.close()
    time.sleep(3)

    # there is some urls which contains w, need to be changed
    driver.sacrifice_letter(scr_letter[0])
    driver.sacrifice_letter(scr_letter[1])
    time.sleep(3)  # overwise smth goes wrong
    driver.confirm_sacrifice()

    # rule 26
    password = italic_formatting(password)
    driver.update_password(password_to_str(password))

    # rule 27
    password = wingdings_formatting(password)
    driver.update_password(password_to_str(password))

    # rule 28
    color, color_digit_sum = color_solver(driver)
    free_digit = free_digit - color_digit_sum
    password = password[:2] + password[2 + color_digit_sum :] + str_to_password(color)
    password = italic_formatting(password)
    driver.update_password(password_to_str(password))

    # rule 31
    password = font_size_change(password)
    driver.update_password(password_to_str(password))

    driver.maximize_window()


if __name__ == "__main__":
    main()
