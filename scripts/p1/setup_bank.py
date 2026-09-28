from __future__ import annotations

from memory import init_memory_bank
from store import init_database


def main() -> None:
    init_memory_bank()
    init_database()


if __name__ == "__main__":
    main()
