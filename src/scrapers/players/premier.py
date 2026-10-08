import pandas as pd

url = "https://raw.githubusercontent.com/Gauransh-Singh/Data-Analytics-Football-season-2024-25/main/Data/players_data_light-2024_2025.csv"

df = pd.read_csv(url)

df["Min"] = pd.to_numeric(df["Min"], errors="coerce")

player_data = df[
    (df["Comp"] == "eng Premier League") &
    (df["Min"] > 90)
].copy()

player_data.to_csv("player_data.csv", index=False)