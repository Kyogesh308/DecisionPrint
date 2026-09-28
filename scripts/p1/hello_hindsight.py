import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

base_url = os.getenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
bank_id = os.getenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

with Hindsight(base_url=base_url) as client:
    client.retain(
        bank_id=bank_id,
        document_id="dp-p1-hindsight-smoke-test",
        content=(
            "P1 smoke test: Kafka was rejected when the project had two "
            "consumers and no replay requirement."
        ),
    )
    recalled = client.recall(
        bank_id=bank_id,
        query="Why was Kafka rejected?",
    )

    if not recalled.results:
        raise RuntimeError("Recall returned no memories for the smoke-test content")

    print(f"Retain: OK")
    print(f"Recall: OK ({len(recalled.results)} result(s))")
    for memory in recalled.results:
        print(f"- {memory.text}")

    reflected = client.reflect(
        bank_id=bank_id,
        query="Why was Kafka rejected?",
    )
    if not reflected.text.strip():
        raise RuntimeError("Reflect returned an empty answer")

    print("Reflect: OK")
    print(reflected.text)