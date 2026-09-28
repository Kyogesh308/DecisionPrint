# Backup Removal — Implementation Note
**Date:** 2025-04-15
**Type:** implementation_note
**Author:** David Kim

## Implementation Details
Per the Q2 Cost Optimization Plan (DEC-DELTA-001), automated RDS snapshots have been disabled for the primary PostgreSQL cluster (`db-prod-main`). 

As a safety net, I've set up a cron job to perform a manual `pg_dump` of the database schema (no data) every Sunday at 2 AM, which is pushed to an S3 bucket with a 30-day lifecycle policy.

It's important to acknowledge that this only covers schema recovery. In the event of a catastrophic failure affecting both the primary and read replicas (e.g., accidental data deletion or corruption), we will not have point-in-time recovery capabilities. However, this aligns with the accepted risk profile given the `budget_pressure=high` constraint.
