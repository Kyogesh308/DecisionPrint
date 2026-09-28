# ADR-007: Message Broker Selection
**Date:** 2024-05-02
**Type:** adr
**Author:** Raj Patel
**Reviewer:** Marcus Chen
**Status:** Accepted

## Context
Project Alpha requires a messaging backbone to decouple the OrderService from the NotificationService. We need to select a message broker that fits our current scale and team constraints. The primary constraint is a 2-consumer scenario (`consumer_count=2`). We do not require message replay (`replay_required=false`), and our expected traffic is moderate (`traffic_volume=moderate`). Crucially, our operations team is limited to 3 SREs (`ops_capacity=small`), and we lack any in-house Kafka expertise. Our workflows are predominantly synchronous (`async_workflows=false`).

## Decision
We will use RabbitMQ as our message broker.

## Rationale
1. **Complexity:** Kafka is overkill for our 2-consumer architecture. We only need simple pub/sub, not a distributed append-only log.
2. **Expertise:** The engineering team has no prior operational experience with Kafka.
3. **Operational Overhead:** An ops team of 3 cannot adequately support and maintain a highly available Kafka cluster alongside our existing infrastructure, especially without prior expertise. RabbitMQ is simpler to operate at our scale.

## Consequences
- **Positive:** Faster time to market due to simpler setup. Lower operational burden on the SRE team.
- **Negative:** If we eventually require event replay or our consumer count grows significantly, RabbitMQ may become a bottleneck or require complex routing topologies. We are trading future scalability for current operational simplicity.
