# Database Incident Postmortem — July 22, 2025
**Date:** 2025-08-01
**Type:** postmortem
**Author:** David Kim, Tom Bradley

## Summary
On July 22, 2025, a faulty migration script executed during a deployment corrupted the `shipments` table in the primary production database. Due to active replication, this corruption was immediately replicated to all read replicas. The incident resulted in a 6-hour complete system outage and partial data loss for 3 enterprise customer accounts.

## Timeline
- **14:00 UTC:** Deployment of release v2.4.1 begins.
- **14:05 UTC:** Faulty migration script drops a critical column and corrupts dependent rows.
- **14:06 UTC:** Alerts fire for high error rates on the API gateway.
- **14:15 UTC:** Incident declared. Database corruption identified.
- **14:30 UTC:** Attempt to failover to replica fails as corruption is already replicated.
- **14:45 UTC:** SRE team begins recovery process. Discovers no recent automated backups are available.
- **15:00 - 19:00 UTC:** SRE team manually reconstructs missing data from application logs and external partner APIs.
- **20:00 UTC:** System restored to a stable state. Partial data loss confirmed for 3 accounts.

## Contributing Factors
The removal of automated backups (DEC-DELTA-001) was a direct contributing factor to the extended recovery time and partial data loss. Without point-in-time recovery snapshots, the team had to rely on tedious and incomplete manual data reconstruction. The decision to prioritize `budget_pressure=high` compromised our disaster recovery capabilities.

## Lessons Learned & Action Items
1. **Never rely solely on replication for DR:** Replication propagates errors just as fast as valid data.
2. **Re-evaluate Cost Savings:** The $4,200/month saved by disabling backups was vastly outweighed by the cost of a 6-hour outage and SLA penalties for the affected customers.
3. **Action:** Immediately restore automated daily backups and implement point-in-time recovery for the primary database. (Owner: David Kim, Status: Completed)
