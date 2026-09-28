# Async Job Queue Workaround — Implementation Note
**Date:** 2024-11-20
**Type:** implementation_note
**Author:** Elena Vasquez

## Context
During the implementation of Project Beta, our asynchronous processing requirements have grown faster than anticipated. We are now integrating with three new external logistics partners, which requires dedicated background job processing. 

## Current State
Our `consumer_count` has grown to 5. We are now using RabbitMQ for limited asynchronous workflows (`async_workflows=limited`), extending it beyond its original pub/sub mandate from Project Alpha.

## Implementation Details
We've set up new exchanges and queues in our existing RabbitMQ cluster to handle these jobs. However, we're starting to see some friction. The routing logic in RabbitMQ is becoming complex to manage across 5 consumers with varying retry and dead-letter requirements. 

As we decided in Alpha last year, Kafka was rejected (ADR-007) due to operational complexity. While that was the right call at the time, RabbitMQ is definitely being stretched by these new use cases. We've implemented a workaround using a combination of delayed message plugins and explicit ack/nack handling in the workers to simulate robust job queues, but it's fragile.

We will monitor the RabbitMQ cluster closely. If the consumer count grows further, this workaround will likely become unmaintainable.
