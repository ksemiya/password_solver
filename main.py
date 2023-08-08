import password_driver_wrapper
import solver_captcha
import solver_chess
import solver_color
import solver_final_rules
import solver_geo
import sacrifice_letter
import today_rules
import utils
import utils_chemical
import utils_rules
import youtube_solver


def main():
    free_digit = 25
    first_password = (
        "1" * 25
        + "$0XXXVpepsimayHeiamloved"
        + today_rules.today_wordle()
        + today_rules.today_moon_phase()
    )  # add leap year in the beginning

    password = utils.str_to_password(first_password)
    password = password + utils_rules.strong_password()

    driver = password_driver_wrapper.PasswordDriverWrapper()
    driver.update_password(utils.str_to_password(password))

    # rule 10
    password, captcha_digit_sum = solver_captcha.captcha_new_password(driver, password)
    free_digit -= captcha_digit_sum
    driver.update_password(utils.str_to_password(password))

    # rule 14
    password = solver_geo.geo_solver(driver, password)
    driver.update_password(utils.str_to_password(password))

    # rule 16
    password, chess_digit_sum = solver_chess.solver(driver, password)
    free_digit -= chess_digit_sum
    driver.update_password(utils.str_to_password(password))

    # rule 17
    password = utils_rules.paul_egg(password)

    # rule 18
    password, h_cnt = utils_chemical.new_password_with_h(password)
    driver.update_password(utils.str_to_password(password))

    # rule 20
    driver.update_password(utils.str_to_password(password))

    # rule 23
    password = utils_rules.paul_chicken_and_caterpillars_after_egg(password)
    driver.update_password(utils.str_to_password(password))

    # rule 24
    password = youtube_solver.solver(driver, password, h_cnt)
    driver.update_password(utils.str_to_password(password))

    # rule 25
    sacrifice_letter.sacrifice(driver, password)

    # rule 26
    password = utils_rules.italic_formatting(password)
    driver.update_password(utils.str_to_password(password))

    # rule 27
    password = utils_rules.wingdings_formatting(password)
    driver.update_password(utils.str_to_password(password))

    # rule 28
    password, color_digit_sum = solver_color.solver(driver, password)
    free_digit -= color_digit_sum
    driver.update_password(utils.str_to_password(password))

    # rule 31
    password = utils_rules.font_size_change(password)
    driver.update_password(utils.str_to_password(password))

    driver.maximize_window()  # Do I need that?

    # rule 32, 33, 35
    password = solver_final_rules.solver(driver, password, free_digit)
    driver.update_password(utils.str_to_password(password))
    driver.confirm_password()
    driver.set_final_answer(utils.str_to_password(password))
    driver.wait(30)
    driver.quit()


if __name__ == "__main__":
    main()
