"""NGƯỜI 7 — possession + playing time + misc."""
from src.scrapers.player_stats.misc import SPEC_MISC
from src.scrapers.player_stats.playing_time import SPEC_PLAYING_TIME
from src.scrapers.player_stats.possession import SPEC_POSSESSION
from tests.helpers import selftest_spec


def test_possession_playing_time_misc_parsers():
    selftest_spec(SPEC_POSSESSION, must_numeric=["Touch_Touches", "TakeOn_Succ%", "Carry_ProDist", "Recv_PrgR"])
    selftest_spec(SPEC_PLAYING_TIME, must_numeric=["Start_Mn/Start", "Sub_unSub", "Team_PPM", "TeamxG_onxGA"])
    selftest_spec(SPEC_MISC, must_numeric=["Misc_Fls", "Misc_Recov", "Aerial_Won%"])
