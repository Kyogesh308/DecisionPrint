from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from memory.cache import cached_recall_memories


DEMO_QUESTIONS = [
    "Why was Kafka rejected?",
    "What drove the Kafka decision?",
    "Which project constraints changed after the Kafka refusal?",
]


def main() -> None:
    for question in DEMO_QUESTIONS:
        cached_recall_memories(question, "project-001")
    print(f"Warmed cache for {len(DEMO_QUESTIONS)} demo questions")


if __name__ == "__main__":
    main()
