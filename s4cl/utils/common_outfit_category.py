#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


# simulation/sims/outfits/outfit_enums.py
from s4cl.utils.common_enum import CommonEnum


class OutfitCategory(CommonEnum):
    CURRENT_OUTFIT = -1
    EVERYDAY = 0
    FORMAL = 1
    ATHLETIC = 2
    SLEEP = 3
    PARTY = 4
    BATHING = 5
    CAREER = 6
    SITUATION = 7
    SPECIAL = 8
    SWIMWEAR = 9
    HOTWEATHER = 10
    COLDWEATHER = 11
    BATUU = 12


class WeatherOutfitCategory(CommonEnum):
    HOTWEATHER = OutfitCategory.HOTWEATHER
    COLDWEATHER = OutfitCategory.COLDWEATHER


class SpecialOutfitIndex(CommonEnum):
    DEFAULT = 0
    TOWEL = 1
    FASHION = 2


class OutfitChangeReason(CommonEnum):
    Invalid = -1
    PreviousClothing = 0
    DefaultOutfit = 1
    RandomOutfit = 2
    ExitBedNPC = 3
    CurrentOutfit = 4
    FashionOutfit = 5


class OutfitIndex(CommonEnum):
    ONE = 0
    TWO = 1
    THRHEE = 2
    FOUR = 3
    FIVE = 4
