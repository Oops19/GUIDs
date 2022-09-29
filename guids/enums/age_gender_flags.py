from s4cl.utils.common_enum import CommonEnum


class AgeGenderFlags(CommonEnum):
    Baby = 0x00000001
    Toddler = 0x00000002
    Child = 0x00000004
    Teen = 0x00000008
    YoungAdult = 0x00000010
    Adult = 0x00000020
    Elder = 0x00000040
    Male = 0x00001000
    Female = 0x00002000
