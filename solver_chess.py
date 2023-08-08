"""Function to solve chess and return new password"""
from xml.etree import ElementTree as ET

import chess.engine
import requests

import password_driver_wrapper
import password_letter
import utils


def get_chess_position(chess_img):
    # Make a request to the URL
    response = requests.get(chess_img, timeout=10)

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
        raise RuntimeError("Failed to fetch SVG.")
    return


def color_move(chess_move):
    if "White" in chess_move:
        return "w"
    if "Black" in chess_move:
        return "b"
    return "WRONG MOVE"


def from_svg_to_fen(chess_position, chess_move):
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
    best_move_alg_notation = board.san(best_move)

    # It is good practice to close the engine after using it
    engine.quit()

    return best_move_alg_notation


def solve_chess_position(chess_img, chess_move):
    chess_position = get_chess_position(chess_img)
    fen = from_svg_to_fen(chess_position, chess_move)
    best_move = get_best_move(fen)
    return best_move


def solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    chess_img = driver.get_chess_svg()
    chess_move = driver.get_chess_move_text()
    chess_solution = solve_chess_position(chess_img, chess_move)
    chess_digit_sum = utils.sum_digits_in_str(chess_solution)
    return (
        password[chess_digit_sum:] if chess_digit_sum != 0 else password
    ) + utils.str_to_password(chess_solution), chess_digit_sum
