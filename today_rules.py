from bs4 import BeautifulSoup
import datetime
import requests


def today_wordle():
    url_wordle_ans = " https://word.tips/todays-wordle-answer/"

    # today date
    today_date = datetime.datetime.now()
    today_worlde_raw = today_date.strftime("%B %-d")  # July 4
    page = requests.get(url_wordle_ans, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    child_soup = soup.find_all("strong")
    for x in child_soup:
        if today_worlde_raw in x.string:
            return x.string[-5:].lower()


def today_moon_phase():
    # return '🌖'
    dict_moon_phases = {
        "New": "🌑",
        "Waxing Crescent": "🌒",
        "First Quarter": "🌓",
        "Waxing Gibbous": "🌔",
        "Full": "🌕",
        "Waning Gibbous": "🌖",
        "Last Quarter": "🌗",
        "Waning Crescent": "🌘",
    }  # should I have it like this?

    url_moon_phases = "https://www.moongiant.com/phase/today/"
    page = requests.get(url_moon_phases, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    moon_details = soup.find("div", {"id": "moonDetails"})
    return dict_moon_phases[moon_details.contents[1].string]
