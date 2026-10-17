"""In log đơn giản ra màn hình."""
import sys


def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"   ⚠ {msg}", file=sys.stderr, flush=True)
