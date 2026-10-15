"""Fixture dùng chung: mọi test chạy trong thư mục tạm, KHÔNG đụng data/ thật."""
import pytest

from src.common.fetcher import Fetcher
from src.common.paths import PATHS


@pytest.fixture(scope="session", autouse=True)
def isolated_paths(tmp_path_factory):
    old = PATHS.base
    PATHS.set(tmp_path_factory.mktemp("btl_data"))
    PATHS.make()
    yield PATHS
    PATHS.set(old)


@pytest.fixture(scope="session")
def demo_env(isolated_paths):
    """Chạy pipeline Phần I trên dữ liệu giả lập một lần cho cả phiên test."""
    from src.pipeline.build_dataset import run_scrape
    from src.pipeline.demo_data import make_demo_raw
    from src.scrapers.player_stats.scraper import ALL_SPECS
    make_demo_raw(ALL_SPECS)
    return run_scrape(Fetcher("local"))
