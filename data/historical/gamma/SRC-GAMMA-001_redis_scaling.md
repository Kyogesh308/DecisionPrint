# Redis Cluster Migration — Gamma Project
**Date:** 2025-02-10
**Type:** architecture_doc
**Author:** Priya Sharma

## Context
As part of Project Gamma, we are evaluating our infrastructure scalability. Our user base has grown 3x since Alpha, and our single Redis instance is struggling to keep up with the load and memory requirements.

## Current State
- **cache_hit_ratio=0.72**: The cache hit ratio has degraded significantly from our 0.85 target. Evictions are high due to memory limits on the single instance.

## Proposed Architecture
We need to migrate to a Redis Cluster topology.

**New Constraints:**
- **instance_count=4**: We will deploy a 4-node Redis Cluster to partition the data and increase available memory.
- **session_persistence=true**: With increased reliability, we will migrate user session storage from PostgreSQL to Redis to improve login performance.

## Implementation Plan
1. Provision 4-node Redis Cluster in AWS ElastiCache.
2. Update application clients to support cluster mode.
3. Cutover caching traffic.
4. Migrate session data logic.
