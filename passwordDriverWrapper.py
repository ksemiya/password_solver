from selenium import webdriver

URL_PASSWORD_GAME = "https://neal.fun/password-game/"

# class of driver and all that driver is doing


class PasswordDriverWrapper:
    def __init__(self) -> None:
        self.driver = webdriver.Safari()
        self.driver.get(URL_PASSWORD_GAME)

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
        refresh_captcha = self.driver.find_element(
            webdriver.common.by.By.CLASS_NAME.CLASS_NAME, "captcha-refresh"
        )
