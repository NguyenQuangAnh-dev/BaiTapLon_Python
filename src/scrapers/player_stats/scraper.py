import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
SEASON = '2024/2025'


def parse_defense_data(html_content, league_name='Premier League'):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    records = []
    if not table:
        return pd.DataFrame()

    for row in table.find('tbody').find_all('tr'):
        if row.find('th', {'scope': 'row'}) is None:
            continue

        player_cell = row.find('td', {'data-stat': 'player'})
        if not player_cell:
            continue

        player_name = player_cell.text.strip()

        def get_stat(stat_name):
            cell = row.find('td', {'data-stat': stat_name})
            if not cell or cell.text.strip() == '':
                return None
            val_clean = cell.text.strip().replace(',', '')
            try:
                return int(float(val_clean))
            except ValueError:
                return None

        record = {
            'player_id': player_name,
            'season': SEASON,
            'league': league_name,
            'tackles': get_stat('tackles'),
            'interceptions': get_stat('interceptions'),
            'clearances': get_stat('clearances'),
            'blocks': get_stat('blocks'),
        }
        records.append(record)

    return pd.DataFrame(records)


def run_scraper(url, output_path):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    df = parse_defense_data(response.text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    pass