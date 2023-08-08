from bs4 import BeautifulSoup
import datetime
import requests


def today_wordle():
    # today date
    today_date = datetime.datetime.now()
    today_date_str = today_date.strftime("%Y-%m-%d")  # 2023-08-08
    url_wordle_ans = "https://neal.fun/api/password-game/wordle?date=" + today_date_str
    page = requests.get(
        url_wordle_ans, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
    )
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.text[11:16]


def today_moon_phase():
    # return '🌖'
    dict_moon_phases = {
        "New Moon": "🌑",
        "Waxing Crescent": "🌒",
        "First Quarter": "🌓",
        "Waxing Gibbous": "🌔",
        "Full Moon": "🌕",
        "Waning Gibbous": "🌖",
        "Last Quarter": "🌗",
        "Waning Crescent": "🌘",
    }  # should I have it like this?

    url_moon_phases = "https://www.moongiant.com/phase/today/"
    page = requests.get(url_moon_phases, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    moon_details = soup.find("div", {"id": "moonDetails"})
    return dict_moon_phases[moon_details.contents[1].string]
