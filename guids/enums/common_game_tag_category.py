from s4cl.utils.common_enum import CommonEnum


class CommonGameTagCategory(CommonEnum):
    """Identifiers for vanilla game tags (These have been gathered dynamically from the :class:`.Tag` enum)."""

    INVALID: 'CommonGameTagCategory' = 0x0000
    Mood: 'CommonGameTagCategory' = 0x0040
    Color: 'CommonGameTagCategory' = 0x0041
    Style: 'CommonGameTagCategory' = 0x0042
    Theme: 'CommonGameTagCategory' = 0x0043
    AgeAppropriate: 'CommonGameTagCategory' = 0x0044
    Archetype: 'CommonGameTagCategory' = 0x0045
    OutfitCategory: 'CommonGameTagCategory' = 0x0046
    Skill: 'CommonGameTagCategory' = 0x0047
    EyeColor: 'CommonGameTagCategory' = 0x0048
    Persona: 'CommonGameTagCategory' = 0x0049
    Special: 'CommonGameTagCategory' = 0x004A
    HairColor: 'CommonGameTagCategory' = 0x004B
    ColorPalette: 'CommonGameTagCategory' = 0x004C
    Hair: 'CommonGameTagCategory' = 0x004D
    FacialHair: 'CommonGameTagCategory' = 0x004E
    Hat: 'CommonGameTagCategory' = 0x004F
    FaceMakeup: 'CommonGameTagCategory' = 0x0050
    Top: 'CommonGameTagCategory' = 0x0051
    Bottom: 'CommonGameTagCategory' = 0x0052
    Body: 'CommonGameTagCategory' = 0x0053
    Shoes: 'CommonGameTagCategory' = 0x0054
    BottomAccessory: 'CommonGameTagCategory' = 0x0055
    BuyCatEE: 'CommonGameTagCategory' = 0x0056
    BuyCatPA: 'CommonGameTagCategory' = 0x0057
    BuyCatLD: 'CommonGameTagCategory' = 0x0058
    BuyCatSS: 'CommonGameTagCategory' = 0x0059
    BuyCatVO: 'CommonGameTagCategory' = 0x005A
    Uniform: 'CommonGameTagCategory' = 0x005B
    Accessories: 'CommonGameTagCategory' = 0x005C
    BuyCatMAG: 'CommonGameTagCategory' = 0x005D
    FloorPattern: 'CommonGameTagCategory' = 0x005E
    WallPattern: 'CommonGameTagCategory' = 0x005F
    Fabric: 'CommonGameTagCategory' = 0x0060
    Build: 'CommonGameTagCategory' = 0x0061
    Pattern: 'CommonGameTagCategory' = 0x0062
    HairLength: 'CommonGameTagCategory' = 0x0063
    HairTexture: 'CommonGameTagCategory' = 0x0064
    TraitGroup: 'CommonGameTagCategory' = 0x0065
    SkinHue: 'CommonGameTagCategory' = 0x0066
    Reward: 'CommonGameTagCategory' = 0x0067
    TerrainPaint: 'CommonGameTagCategory' = 0x0068
    EyebrowThickness: 'CommonGameTagCategory' = 0x0069
    EyebrowShape: 'CommonGameTagCategory' = 0x006A

class UnCommonGameTagCategory(CommonEnum):
    """Identifiers for vanilla game tags (These have been gathered dynamically from the :class:`.Tag` enum)."""

    INVALID: 'UnCommonGameTagCategory' = 0
    Mood: 'UnCommonGameTagCategory' = 2 ** 1
    Color: 'UnCommonGameTagCategory' = 2 ** 2
    Style: 'UnCommonGameTagCategory' = 2 ** 3
    Theme: 'UnCommonGameTagCategory' = 2 ** 4
    AgeAppropriate: 'UnCommonGameTagCategory' = 2 ** 5
    Archetype: 'UnCommonGameTagCategory' = 2 ** 6
    OutfitCategory: 'UnCommonGameTagCategory' = 2 ** 7
    Skill: 'UnCommonGameTagCategory' = 2 ** 8
    EyeColor: 'UnCommonGameTagCategory' = 2 ** 9
    Persona: 'UnCommonGameTagCategory' = 2 ** 10
    Special: 'UnCommonGameTagCategory' = 2 ** 11
    HairColor: 'UnCommonGameTagCategory' = 2 ** 12
    ColorPalette: 'UnCommonGameTagCategory' = 2 ** 13
    Hair: 'UnCommonGameTagCategory' = 2 ** 14
    FacialHair: 'UnCommonGameTagCategory' = 2 ** 15
    Hat: 'UnCommonGameTagCategory' = 2 ** 16
    FaceMakeup: 'UnCommonGameTagCategory' = 2 ** 17
    Top: 'UnCommonGameTagCategory' = 2 ** 18
    Bottom: 'UnCommonGameTagCategory' = 2 ** 19
    Body: 'UnCommonGameTagCategory' = 2 ** 20
    Shoes: 'UnCommonGameTagCategory' = 2 ** 21
    BottomAccessory: 'UnCommonGameTagCategory' = 2 ** 22
    BuyCatEE: 'UnCommonGameTagCategory' = 2 ** 23
    BuyCatPA: 'UnCommonGameTagCategory' = 2 ** 24
    BuyCatSS: 'UnCommonGameTagCategory' = 2 ** 25
    BuyCatVO: 'UnCommonGameTagCategory' = 2 ** 26
    Uniform: 'UnCommonGameTagCategory' = 2 ** 27
    Accessories: 'UnCommonGameTagCategory' = 2 ** 28
    BuyCatMAG: 'UnCommonGameTagCategory' = 2 ** 29
    FloorPattern: 'UnCommonGameTagCategory' = 2 ** 30
    WallPattern: 'UnCommonGameTagCategory' = 2 ** 31
    Fabric: 'UnCommonGameTagCategory' = 2 ** 32
    Build: 'UnCommonGameTagCategory' = 2 ** 33
    Pattern: 'UnCommonGameTagCategory' = 2 ** 34
    HairLength: 'UnCommonGameTagCategory' = 2 ** 35
    HairTexture: 'UnCommonGameTagCategory' = 2 ** 36
    TraitGroup: 'UnCommonGameTagCategory' = 2 ** 37
    SkinHue: 'UnCommonGameTagCategory' = 2 ** 38
    Reward: 'UnCommonGameTagCategory' = 2 ** 39
    TerrainPaint: 'UnCommonGameTagCategory' = 2 ** 40
    EyebrowThickness: 'UnCommonGameTagCategory' = 2 ** 41
    EyebrowShape: 'UnCommonGameTagCategory' = 2 ** 42