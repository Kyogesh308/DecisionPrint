# Platform v2 Caching Architecture
**Date:** 2024-04-20
**Type:** architecture_doc
**Author:** Priya Sharma

## Overview
This document outlines the caching strategy for Platform v2. Caching is critical to reduce database load and improve API response times for common queries.

## Design
We will deploy a single Redis instance. 

**Constraints & Metrics:**
- **instance_count=1**: A single master node is sufficient.
- **cache_hit_ratio=0.85**: Our target hit ratio for heavily accessed endpoints.
- **session_persistence=false**: Redis will be treated purely as an ephemeral cache. Session data will be stored in PostgreSQL.

## Rationale
For our current scale, a single Redis instance handles our caching needs adequately. We do not need the complexity of a Redis Cluster or Sentinel setup. If the instance goes down, applications will fallback to the database (thundering herd protections must be implemented in the application layer).
