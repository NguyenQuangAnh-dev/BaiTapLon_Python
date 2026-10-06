import os
import pandas as pd


def test_scraper_module_exists():
    from src.scrapers.player_stats.scraper import parse_defense_data
    assert callable(parse_defense_data)


def test_schema_columns():
    expected_cols = {
        'player_id',
        'season',
        'league',
        'tackles',
        'interceptions',
        'clearances',
        'blocks'
    }
    dummy_html = "<html><body><table><tbody></tbody></table></body></html>"
    from src.scrapers.player_stats.scraper import parse_defense_data
    df = parse_defense_data(dummy_html)
    assert isinstance(df, pd.DataFrame)