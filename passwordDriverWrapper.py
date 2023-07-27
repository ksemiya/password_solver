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
