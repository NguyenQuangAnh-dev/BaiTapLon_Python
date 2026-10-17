#!/usr/bin/env python3
"""python radarChartPlot.py --p1 <tên 1> --p2 <tên 2> --Attribute <thuộc_tính_1,...,thuộc_tính_n>

Ví dụ: python radarChartPlot.py --p1 "Mohamed Salah" --p2 "Erling Haaland" --Attribute Sh_Gls,Sh_SoT,SCA_SCA90
Logic nằm ở src/visualization/radar.py (NGƯỜI 10)."""
import sys

from src.visualization.radar import radar_cli

if __name__ == "__main__":
    sys.exit(radar_cli())
