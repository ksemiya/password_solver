"""Function to solve geo and return new password"""
from frozendict import frozendict
import pandas as pd

import password_driver_wrapper
import password_letter
import utils

_DF_PATH = "./databases/"
_DF_COUNTRIES = pd.read_json(_DF_PATH + "maps.jsonc")
# pylint: disable-next=no-member
_DICT_COUNTRIES = frozendict(zip(_DF_COUNTRIES.embed, _DF_COUNTRIES.title))


def geo_solver(
    driver: password_driver_wrapper.PasswordDriverWrapper,
    password: password_letter.PasswordLetter,
) -> password_letter.PasswordLetter:
    """Function to solve geo and return new password"""
    geo_embed = driver.get_embed_geo()
    country = _DICT_COUNTRIES[geo_embed].lower().replace(" ", "")
    return password + utils.str_to_password(country)
