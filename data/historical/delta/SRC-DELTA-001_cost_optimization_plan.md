# Infrastructure Cost Optimization Plan — Q2 2025
**Date:** 2025-03-15
**Type:** architecture_doc
**Author:** Aisha Rahman, Sarah Okonkwo
**Sensitivity:** confidential

## Overview
Due to macroeconomic factors and the upcoming Q3 funding round, Engineering has been tasked with reducing monthly infrastructure spend by 15%. This document outlines the proposed cost-cutting measures.

## Constraints
- **budget_pressure=high**: Immediate cost reductions are mandated by leadership.
- **data_criticality=medium**: While data is important, we have historically relied on cross-region replication for redundancy rather than point-in-time backups.

## Proposed Measures

1. **Downsize Staging Environments:** Reduce instance sizes in non-production environments. Estimated savings: $2,500/month.
2. **Consolidate Logging:** Reduce log retention in ELK from 30 days to 14 days. Estimated savings: $1,200/month.
3. **Disable automated database backups:** (DEC-DELTA-001) Currently, we pay for automated daily snapshots of our primary PostgreSQL cluster, alongside active replication. By relying solely on replication and manual weekly schemas, we can reduce storage and snapshot costs. 
   - **Action:** Set `backup_policy=none`.
   - **Estimated savings:** $4,200/month.

## Next Steps
These measures will be rolled out over the next two sprints. Engineering managers should review potential impacts with their teams.
