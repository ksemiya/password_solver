import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.safari import remote_connection
from selenium.webdriver.safari import options

URL_PASSWORD_GAME = "https://neal.fun/password-game/"


# class of driver and all that driver is doing
class PasswordDriverWrapper:
    def __init__(self, remote_server_addr) -> None:
        # /usr/bin/safaridriver -p 50259
        if remote_server_addr is None:
            remote_server_addr = "http://localhost:50259"
        self.driver = webdriver.Remote(
            command_executor=remote_connection.SafariRemoteConnection(
                remote_server_addr=remote_server_addr
            ),
            options=options.Options(),
        )
        # self.driver = webdriver.Safari()
        self.driver.get(URL_PASSWORD_GAME)
        time.sleep(1)

    def update_password(self, new_password: str) -> None:
        self.driver.execute_script(
            f"document.querySelector('.ProseMirror').innerHTML = '<p>{new_password}</p>';"
        )

    def get_current_captcha_url(self) -> str:
        # example https://neal.fun/password-game/captchas/xe8xm.png
        return self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "captcha-img"
        ).get_attribute(
            "src"
        )  # [40:45] # TODO refactor [40:45] lets do that in separate function

    def refresh_captcha(self) -> None:
        time.sleep(1)
        self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "captcha-refresh"
        ).click()

    def get_embed_geo(self) -> str:
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        child_soup = soup.find_all("iframe")
        for x in child_soup:
            if x["src"].startswith("https://www.google.com/maps/embed"):
                geo_embed = x["src"]
        return geo_embed

    def get_chess_svg(self) -> str:
        time.sleep(1)
        return self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "chess-img"
        ).get_attribute("src")

    def get_chess_move_text(self) -> str:
        return self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "move"
        ).text.strip()

    def get_YT_rule(self) -> str:
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        child_soup = soup.find_all(class_="rule rule rule-error youtube")
        return child_soup[0].text

    def sacrifice_letter(self, letter_num) -> None:
        self.driver.find_element(
            webdriver.common.by.By.XPATH,
            f'//*[@id="__layout"]/div/div/div[2]/div[5]/div/div[1]/div/div/div/div[2]/div/button[{letter_num}]',
        ).send_keys(webdriver.common.keys.Keys.ENTER)

    def confirm_sacrifice(self) -> None:
        time.sleep(3)
        self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "sacrafice-btn"
        ).send_keys(webdriver.common.keys.Keys.ENTER)

    def get_rgb_color(self) -> str:
        return self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME, "rand-color"
        ).get_attribute("style")

    def refresh_color(self) -> None:
        time.sleep(1)
        self.driver.find_element(webdriver.common.by.By.CLASS_NAME, "refresh").click()

    def confirm_password(self) -> None:
        time.sleep(1)
        self.driver.find_element(
            webdriver.common.by.By.XPATH,
            '//*[@id="__layout"]/div/div/div[2]/div[5]/div/div[1]/div/div/div/div[2]/button[1]',
        ).send_keys(webdriver.common.keys.Keys.ENTER)

    def set_final_answer(self, final_password: str) -> None:
        self.driver.execute_script(
            f"document.querySelector('.ProseMirror:not(.password-final)').innerHTML = '<p>{final_password}</p>';"
        )

    def maximize_window(self) -> None:
        self.driver.maximize_window()

    def quit(self):
        self.driver.quit()

    def wait(self, sec):
        time.sleep(sec)
