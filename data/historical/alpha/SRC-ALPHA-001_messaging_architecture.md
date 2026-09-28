# Platform v2 Messaging Architecture
**Date:** 2024-04-15
**Type:** architecture_doc
**Author:** Raj Patel

## Overview
This document outlines the architecture for Project Alpha's messaging system. We're building a B2B logistics platform where order events need to be processed reliably. 

## Context & Constraints
As we evaluate our messaging needs, it's crucial to acknowledge our current operational reality and system constraints:
- **consumer_count=2**: Currently, we only have two downstream services that need to consume messages (OrderService and NotificationService).
- **replay_required=false**: If a message is missed, we don't need a historical replay; current state can be reconciled via the database.
- **traffic_volume=moderate**: We expect a few thousand events per day at peak.
- **ops_capacity=small**: Our SRE team currently consists of just 3 people (David Kim and two others). We do not have dedicated resources for complex infrastructure management.
- **async_workflows=false**: Almost all of our critical workflows are synchronous. The messaging queue is purely for decoupling non-critical side effects.

## Evaluation
We evaluated Apache Kafka and RabbitMQ. Kafka is the industry standard for event streaming, but it requires significant operational overhead, especially around ZooKeeper (or Kraft) management, partitioning, and replication. Given our `ops_capacity=small` constraint, maintaining a Kafka cluster is unfeasible. Furthermore, our `consumer_count=2` and `replay_required=false` constraints mean we wouldn't utilize Kafka's primary advantages.

RabbitMQ, on the other hand, is a traditional message broker that is easier to deploy and manage for simple point-to-point or pub/sub workloads without replay requirements. It handles our `traffic_volume=moderate` effortlessly.

## Recommendation
I recommend proceeding with RabbitMQ. It perfectly aligns with our current constraints and team capabilities. We can revisit this decision if our architecture evolves to require event sourcing or massive fan-out, but for Project Alpha, RabbitMQ is the pragmatic choice.
